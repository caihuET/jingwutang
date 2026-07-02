"""战斗服务"""
import json
import random
from src.service.battle_engine import BattleEngine, BattleUnit, MONSTERS
from src.repository.player_repo import PlayerRepository
from src.repository.equipment_repo import EquipmentRepository
from src.repository.skill_repo import SkillRepository
from src.models.battle_log import BattleLog
from src.utils.errors import GameException
from src.models.skill import SkillDefinition
from src.models.player_attr import PlayerAttribute
from src.utils.constants import ErrorCode
from src.utils.constants import EXP_TABLE, BattleType, SkillType
from src.service.task_service import TaskService


class BattleService:
    def __init__(self, db):
        self.db = db
        self.player_repo = PlayerRepository(db)
        self.equip_repo = EquipmentRepository(db)
        self.skill_repo = SkillRepository(db)

    def pve_battle(self, player_id: int, map_id: int) -> dict:
        """PvE 历练战斗"""
        player = self.player_repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        if player.stamina < 10:
            raise GameException(ErrorCode.STAMINA_NOT_ENOUGH, "体力不足")
        if map_id not in MONSTERS:
            raise GameException(ErrorCode.PARAM_INVALID, "地图不存在")

        # 构建玩家战斗单元
        unit = self._build_player_unit(player)
        engine = BattleEngine()
        engine.setup_pve(unit, map_id)
        result = engine.execute()

        # 扣除体力
        player.stamina -= 10

        # 发放奖励
        exp_gain = result.exp_gained
        gold_gain = result.gold_gained
        is_win = result.winner and result.winner.is_player

        if is_win:
            player.exp += exp_gain
            player.gold += gold_gain
            # 检查升级
            leveled_up = False
            while player.level < 100 and player.exp >= EXP_TABLE[player.level]:
                player.exp -= EXP_TABLE[player.level]
                player.level += 1
                player.free_points += 5
                leveled_up = True

        self.db.commit()

        # 任务进度更新
        ts = TaskService(self.db)
        ts.check_progress(player_id, "pve_battle", 1)
        if map_id in (2, 4):
            ts.check_progress(player_id, "kill_boss", 1)
        if is_win and leveled_up:
            ts.check_progress(player_id, "reach_level", player.level)
        drop_name = self._drop_equipment(player_id, map_id) if is_win else None

        # 保存战斗日志
        log = BattleLog(
            attacker_id=player_id,
            defender_id=-map_id,
            battle_type=BattleType.PVE,
            result=1 if is_win else 2,
            rounds=result.rounds,
            log_detail=result.log,
            drop_exp=exp_gain,
            drop_gold=gold_gain,
        )
        self.db.add(log)
        self.db.commit()

        return {
            "result": "win" if is_win else "lose",
            "rounds": result.rounds,
            "log": result.log,
            "exp_gained": exp_gain,
            "gold_gained": gold_gain,
            "stamina_consumed": 10,
            "drop_item": drop_name,
        }

    def _build_player_unit(self, player) -> BattleUnit:
        """从数据库角色构建战斗单元"""
        # 基础属性
        base_stats = {
            "attack": 10 + player.level * 2,
            "defense": 5 + player.level,
            "magic_attack": 5 + player.level,
            "magic_defense": 5 + player.level,
            "speed": 10 + player.level,
        }

        # 属性加成
        attr = self.db.query(PlayerAttribute).filter(PlayerAttribute.player_id == player.id).first()
        if attr:
            base_stats["attack"] += max(0, (attr.strength - 10) * 0.5)
            base_stats["speed"] += max(0, (attr.agility - 10) * 0.3)
            base_stats["magic_attack"] += max(0, (attr.spirit - 10) * 0.3)
            base_stats["magic_defense"] += max(0, (attr.spirit - 10) * 0.3)

        # 装备加成
        equipped = self.equip_repo.get_equipped(player.id)
        hp_bonus = 0
        for eq in equipped:
            base_stats["attack"] += getattr(eq, "enhance_attack", 0) or 0
            base_stats["defense"] += getattr(eq, "enhance_defense", 0) or 0
            hp_bonus += getattr(eq, "enhance_hp", 0) or 0
        max_hp_extra = 0
        max_mp_extra = 0
        if attr:
            max_hp_extra = max(0, (attr.constitution - 10) * 5)
            max_mp_extra = max(0, (attr.spirit - 10) * 3)

        # 出战技能
        skills_data = self.skill_repo.get_slotted_skills(player.id)
        skill_ids = [ps.skill_id for ps in skills_data]
        skill_defs = {}
        if skill_ids:
            for sd in self.db.query(SkillDefinition).filter(SkillDefinition.id.in_(skill_ids)).all():
                skill_defs[sd.id] = sd.name
        skills = []
        for ps in skills_data:
            skills.append({
                "id": ps.id,
                "name": skill_defs.get(ps.skill_id, f"技能{ps.skill_id}"),
                "skill_type": SkillType.PHYSICAL,
                "base_damage": 100 + ps.level * 15,
                "mp_cost": 10 + ps.level * 5,
                "cooldown": 0,
                "damage_type": 1,
            })

        return BattleUnit(
            unit_id=player.id,
            name=player.name,
            level=player.level,
            hp=player.max_hp + int(max_hp_extra) + hp_bonus,
            mp=player.max_mp + int(max_mp_extra),
            attack=base_stats["attack"],
            defense=base_stats["defense"],
            magic_attack=base_stats["magic_attack"],
            magic_defense=base_stats["magic_defense"],
            speed=base_stats["speed"],
            crit_rate=0.05,
            dodge_rate=0.05,
            skills=skills,
            is_player=True,
        )

    def _drop_equipment(self, player_id: int, map_id: int) -> dict:
        """战斗胜利后概率掉落装备"""
        from src.models.equipment import EquipmentDefinition, PlayerEquipment
        
        DROP_RATES = {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.50}
        if random.random() > DROP_RATES.get(map_id, 0.15):
            return None
        
        qm = {1: (1, 2), 2: (1, 3), 3: (2, 4), 4: (3, 5)}
        q_min, q_max = qm.get(map_id, (1, 2))
        quality = random.randint(q_min, q_max)
        
        defs = self.equip_repo.db.query(EquipmentDefinition).filter(
            EquipmentDefinition.quality <= quality
        ).all()
        if not defs:
            defs = self.equip_repo.db.query(EquipmentDefinition).all()
        if not defs:
            return None
        
        eq = random.choice(defs)
        pe = PlayerEquipment(
            player_id=player_id, equip_def_id=eq.id, slot=eq.slot,
            quality=quality, is_equipped=0, enhance_level=0, durability=100,
        )
        self.equip_repo.db.add(pe)
        self.equip_repo.db.commit()
        
        qn = {1: "粗糙", 2: "普通", 3: "精良", 4: "优秀", 5: "传说"}
        return {"name": eq.name, "quality": qn.get(quality), "slot": eq.slot}
