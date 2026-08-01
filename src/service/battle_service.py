"""战斗服务"""

import json

import random

from src.service.battle_engine import BattleEngine, BattleUnit, MONSTERS

from src.repository.player_repo import PlayerRepository

from src.repository.equipment_repo import EquipmentRepository

from src.repository.skill_repo import SkillRepository

from src.models.battle_log import BattleLog

from src.utils.errors import GameException

from src.models.skill import SkillDefinition, PlayerSkill

from src.models.player_attr import PlayerAttribute

from src.utils.constants import ErrorCode

from src.utils.constants import EXP_TABLE, BattleType, SkillType, PASSIVE_SKILL_EFFECTS
from src.utils.constants import get_passive_name

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
        reputation_gain = max(1, exp_gain // 10)  # 修为 = 经验/10
        is_win = result.winner and result.winner.is_player
        if is_win:
            player.exp += exp_gain
            player.gold += gold_gain
            player.reputation += reputation_gain
            # 检查升级

            leveled_up = False

            while player.level < 100 and player.exp >= EXP_TABLE[player.level]:

                player.exp -= EXP_TABLE[player.level]

                player.level += 1

                player.free_points += 5

                player.max_hp += 20

                player.max_mp += 10

                player.hp = player.max_hp

                player.mp = player.max_mp

                leveled_up = True



        # 重新计算战力
        player.combat_power = self._calc_combat_power(player)
        self.db.commit()

        # 技能熟练度增长（已装备技能每场战斗+1）
        slotted = self.skill_repo.get_slotted_skills(player.id)
        all_skills = self.skill_repo.get_player_skills(player.id)
        for ps in all_skills:
            is_slotted = (ps.slot_position is not None)
            ps.proficiency += 2 if is_slotted else 1
            # 每20点熟练度可升1级（满级20）
            level_up_times = ps.proficiency // 20
            if level_up_times > 0 and ps.level < 20:
                level_gain = min(level_up_times, 20 - ps.level)
                ps.level += level_gain
                ps.proficiency -= level_gain * 20
        if all_skills:
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
            "reputation_gained": reputation_gain,
            "stamina_consumed": 10,
            "drop_item": drop_name,

        }



    def _calc_combat_power(self, player) -> int:

        """计算角色战力"""

        attr = self.db.query(PlayerAttribute).filter(

            PlayerAttribute.player_id == player.id

        ).first()

        hp = player.max_hp

        level_power = player.level * 10

        str_power = (attr.strength if attr else 10) * 2

        agi_power = (attr.agility if attr else 10) * 1

        con_power = (attr.constitution if attr else 10) * 3

        spi_power = (attr.spirit if attr else 10) * 2

        from src.service.equipment_service import EquipmentService
        from src.utils.constants import calc_equip_power
        bonuses = EquipmentService(self.db).get_equipped_bonuses(player.id)
        equip_power = calc_equip_power(bonuses)

        # 经脉加成
        meridian_hp = 0
        meridian_atk = 0
        meridian_def = 0
        try:
            from src.models.meridian import MeridianAcupoint
            from src.repository.meridian_repo import MeridianRepository
            mer_repo = MeridianRepository(self.db)
            pms = mer_repo.get_all_player_meridians(player.id)
            for pm in pms:
                acups = self.db.query(MeridianAcupoint).filter(
                    MeridianAcupoint.meridian_id == pm.meridian_id,
                    MeridianAcupoint.position <= pm.current_acupoint
                ).all()
                for ap in acups:
                    meridian_hp += ap.bonus_hp
                    meridian_atk += ap.bonus_attack
                    meridian_def += ap.bonus_defense
        except Exception:
            pass
        meridian_power = meridian_atk + meridian_def * 2 + meridian_hp // 2
        return int(level_power + str_power + agi_power + con_power + spi_power + equip_power + meridian_power)



    def _get_passive_bonuses(self, player) -> dict:
        """汇总已学被动技能的常驻加成"""
        bonuses = {}
        rows = self.db.query(PlayerSkill, SkillDefinition).join(
            SkillDefinition, SkillDefinition.id == PlayerSkill.skill_id
        ).filter(
            PlayerSkill.player_id == player.id,
            SkillDefinition.skill_type == SkillType.PASSIVE,
            PlayerSkill.is_learned == 1,
        ).all()
        for ps, sd in rows:
            effects = PASSIVE_SKILL_EFFECTS.get(get_passive_name(sd.school_id or 0, sd.name), {})
            for key, value in effects.items():
                bonuses[key] = bonuses.get(key, 0) + value * ps.level
        return bonuses






    def _build_player_unit(self, player) -> BattleUnit:
        """从数据库角色构建战斗单元"""
        # 经脉加成
        meridian_hp = 0
        meridian_atk = 0
        meridian_def = 0
        meridian_spd = 0
        try:
            from src.models.meridian import MeridianAcupoint
            from src.repository.meridian_repo import MeridianRepository
            mer_repo = MeridianRepository(self.db)
            pms = mer_repo.get_all_player_meridians(player.id)
            for pm in pms:
                acups = self.db.query(MeridianAcupoint).filter(
                    MeridianAcupoint.meridian_id == pm.meridian_id,
                    MeridianAcupoint.position <= pm.current_acupoint
                ).all()
                for ap in acups:
                    meridian_hp += ap.bonus_hp
                    meridian_atk += ap.bonus_attack
                    meridian_def += ap.bonus_defense
                    meridian_spd += ap.bonus_speed
        except Exception:
            pass
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



        # 装备加成（基础 + 强化 + 附加属性）
        from src.service.equipment_service import EquipmentService
        equip_bonuses = EquipmentService(self.db).get_equipped_bonuses(player.id)
        base_stats["attack"] += equip_bonuses["attack"]
        base_stats["defense"] += equip_bonuses["defense"]
        base_stats["magic_attack"] += equip_bonuses["magic_attack"]
        base_stats["magic_defense"] += equip_bonuses["magic_defense"]
        base_stats["speed"] += equip_bonuses["speed"]
        hp_bonus = equip_bonuses["hp"]
        mp_bonus = equip_bonuses["mp"]

        max_hp_extra = 0

        max_mp_extra = 0

        if attr:

            max_hp_extra = max(0, (attr.constitution - 10) * 5)

            max_mp_extra = max(0, (attr.spirit - 10) * 3)



        # 被动技能加成
        passive_bonus = self._get_passive_bonuses(player)






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
            hp=player.max_hp + int(max_hp_extra) + hp_bonus + meridian_hp + int(passive_bonus.get("max_hp", 0)),
            mp=player.max_mp + int(max_mp_extra) + mp_bonus + int(passive_bonus.get("max_mp", 0)),
            attack=base_stats["attack"] + int(meridian_atk) + int(passive_bonus.get("attack", 0)),
            defense=base_stats["defense"] + int(meridian_def) + int(passive_bonus.get("defense", 0)),
            magic_attack=base_stats["magic_attack"] + int(passive_bonus.get("magic_attack", 0)),
            magic_defense=base_stats["magic_defense"] + int(passive_bonus.get("magic_defense", 0)),
            speed=base_stats["speed"] + int(meridian_spd) + int(passive_bonus.get("speed", 0)),
            crit_rate=0.05 + passive_bonus.get("crit_rate", 0),
            dodge_rate=0.05 + passive_bonus.get("dodge_rate", 0),
            skills=skills,
            heal_per_round=int(passive_bonus.get("heal_per_round", 0)),
            lifesteal=passive_bonus.get("lifesteal", 0),
            reflect_rate=min(0.5, passive_bonus.get("reflect_rate", 0)),
            is_player=True,

        )



    def _drop_equipment(self, player_id: int, map_id: int) -> dict:
        """战斗胜利后概率掉落装备（品质和等级与玩家等级、地图等级挂钩）"""
        from src.models.equipment import EquipmentDefinition, PlayerEquipment
        from src.models.player import Player
        
        # 获取玩家等级
        player = self.equip_repo.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None
        player_level = player.level
        
        # 掉落概率
        DROP_RATES = {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.50}
        if random.random() > DROP_RATES.get(map_id, 0.15):
            return None
        
        # 根据玩家等级调整品质范围
        qm = {1: (1, 2), 2: (1, 3), 3: (2, 4), 4: (3, 6)}
        q_min, q_max = qm.get(map_id, (1, 2))
        # 玩家等级高时，品质下限提升
        if player_level >= 60:
            q_min = max(q_min, 5)
        elif player_level >= 40:
            q_min = max(q_min, 4)
        elif player_level >= 25:
            q_min = max(q_min, 3)
        elif player_level >= 15:
            q_min = max(q_min, 2)
        quality = random.randint(q_min, q_max)
        
        # 筛选装备：品质匹配且等级要求不超过玩家等级
        defs = self.equip_repo.db.query(EquipmentDefinition).filter(
        EquipmentDefinition.quality <= quality,
        EquipmentDefinition.level_required <= player_level
        ).order_by(EquipmentDefinition.level_required.desc()).all()
        if not defs:
            # 回退：只按品质筛选
            defs = self.equip_repo.db.query(EquipmentDefinition).filter(
                EquipmentDefinition.quality <= quality
            ).order_by(EquipmentDefinition.level_required.desc()).all()
        if not defs:
            return None
        
        # 优先掉落等级接近玩家等级的装备（取前1/3高等级装备中随机）
        tier_size = max(1, len(defs) // 3)
        eq = random.choice(defs[:tier_size])
        
        pe = PlayerEquipment(
            player_id=player_id, equip_def_id=eq.id, slot=eq.slot,
            quality=quality, is_equipped=0, enhance_level=0, durability=100,
        )
        self.equip_repo.db.add(pe)
        self.equip_repo.db.flush()
        from src.service.equipment_service import EquipmentService
        EquipmentService(self.equip_repo.db).generate_affixes_for_equipment(pe)
        self.equip_repo.db.commit()
        
        qn = {1: "普通", 2: "优秀", 3: "精良", 4: "史诗", 5: "传说", 6: "红装"}
        return {"name": eq.name, "quality": qn.get(quality), "slot": eq.slot}

