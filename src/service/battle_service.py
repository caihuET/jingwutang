"""战斗服务"""
import json
import random
from src.service.battle_engine import BattleEngine, BattleUnit, MONSTERS
from src.repository.player_repo import PlayerRepository
from src.repository.equipment_repo import EquipmentRepository
from src.repository.skill_repo import SkillRepository
from src.models.battle_log import BattleLog
from src.utils.errors import GameException
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

        # 装备加成
        equipped = self.equip_repo.get_equipped(player.id)
        for eq in equipped:
            base_stats["attack"] += getattr(eq, "enhance_attack", 0) or 0
            base_stats["defense"] += getattr(eq, "enhance_defense", 0) or 0

        # 出战技能
        skills_data = self.skill_repo.get_slotted_skills(player.id)
        skills = []
        for ps in skills_data:
            skills.append({
                "id": ps.id,
                "name": f"技能{ps.skill_id}",
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
            hp=player.max_hp,
            mp=player.max_mp,
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
