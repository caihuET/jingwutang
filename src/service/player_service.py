"""角色服务"""
from src.utils.validators import validate_nickname, check_sensitive_words
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.utils.constants import SchoolType, EXP_TABLE
from src.models.player_attr import PlayerAttribute
from src.repository.player_repo import PlayerRepository
from datetime import datetime


class PlayerService:
    """角色业务"""

    def __init__(self, db):
        self.repo = PlayerRepository(db)

    def get_by_user(self, user_id: int) -> dict:
        """按 user_id 查询角色"""
        from sqlalchemy import text
        try:
            row = self.repo.db.execute(text("SELECT id, name, level FROM players WHERE user_id = :uid"), {"uid": user_id}).fetchone()
            if row:
                return {"player_id": int(row[0]), "name": row[1], "level": row[2]}
        except:
            pass
        try:
            player = self.repo.get_by_user_id(user_id)
            if player:
                return {"player_id": player.id, "name": player.name, "level": player.level}
        except:
            pass
        return None

    def create(self, user_id: int, name: str, gender: int, school_id: int) -> dict:
        """创建角色"""
        if not validate_nickname(name):
            raise GameException(ErrorCode.PARAM_INVALID, "昵称格式不正确")
        if not check_sensitive_words(name):
            raise GameException(ErrorCode.NICKNAME_SENSITIVE, "昵称包含敏感词")
        if self.repo.get_by_name(name):
            raise GameException(ErrorCode.NICKNAME_EXISTS, "昵称已存在")
        existing = self.repo.get_by_user_id(user_id)
        if existing:
            return {"player_id": existing.id}
        player = self.repo.create(user_id, name, gender, school_id)
        self._assign_school_skills(player.id, school_id)
        attr = PlayerAttribute(player_id=player.id)
        self.repo.db.add(attr)
        self.repo.db.commit()
        return {"player_id": player.id}

    
    def _assign_school_skills(self, player_id: int, school_id: int):
        """分配门派技能"""
        from src.models.skill import SkillDefinition, PlayerSkill
        skills = self.repo.db.query(SkillDefinition).filter(
            SkillDefinition.school_id == school_id
        ).all()
        for i, sd in enumerate(skills):
            slot = i + 1 if i < 4 else None
            sp = PlayerSkill(
                player_id=player_id, skill_id=sd.id,
                level=1, proficiency=0,
                slot_position=slot, is_learned=1,
            )
            self.repo.db.add(sp)
        self.repo.db.commit()

    def allocate_attribute(self, player_id: int, strength: int = 0, agility: int = 0, constitution: int = 0, spirit: int = 0) -> dict:
        """分配属性点"""
        player = self.repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        total = strength + agility + constitution + spirit
        if total > player.free_points:
            raise GameException(ErrorCode.PARAM_INVALID, "自由属性点不足")
        attr = self.repo.db.query(PlayerAttribute).filter(PlayerAttribute.player_id == player_id).first()
        if not attr:
            attr = PlayerAttribute(player_id=player_id)
            self.repo.db.add(attr)
        attr.strength += strength
        attr.agility += agility
        attr.constitution += constitution
        attr.spirit += spirit
        player.free_points -= total
        self.repo.db.commit()
        return {
            "strength": attr.strength,
            "agility": attr.agility,
            "constitution": attr.constitution,
            "spirit": attr.spirit,
            "free_points": player.free_points,
        }

    def get_info(self, player_id: int) -> dict:
        """获取角色信息"""
        player = self.repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        self._apply_stamina_recovery(player)
        self._apply_level_hp_mp(player)
        self._check_new_skills(player)
        self._check_new_tasks(player)
        meridian_bonuses = self._calc_meridian_bonuses(player_id)
        attr = self.repo.db.query(PlayerAttribute).filter(PlayerAttribute.player_id == player_id).first()
        combat_power = self._calc_combat_power(player)
        return {
            "name": player.name,
            "level": player.level,
            "exp": player.exp,
            "hp": player.hp,
            "max_hp": player.max_hp,
            "mp": player.mp,
            "max_mp": player.max_mp,
            "stamina": player.stamina,
            "gold": player.gold,
            "ingot": player.ingot,
            "reputation": player.reputation,
            "combat_power": combat_power,
            "school_name": SchoolType.NAMES.get(player.school_id, "未知"),
            "exp_needed": EXP_TABLE[player.level] if player.level < 100 else 0,
            "exp_progress": round(player.exp / EXP_TABLE[player.level] * 100, 1) if player.level < 100 and EXP_TABLE[player.level] > 0 else 0,
            "max_stamina": self._get_max_stamina(player.level),
            "free_points": player.free_points,
            "strength": attr.strength if attr else 10,
            "agility": attr.agility if attr else 10,
            "constitution": attr.constitution if attr else 10,
            "spirit": attr.spirit if attr else 10,
            "meridian_bonus_hp": meridian_bonuses["hp"],
            "meridian_bonus_attack": meridian_bonuses["attack"],
            "meridian_bonus_defense": meridian_bonuses["defense"],
            "meridian_bonus_speed": meridian_bonuses["speed"],
            "effective_max_hp": player.max_hp + meridian_bonuses["hp"],
            "effective_max_mp": player.max_mp,
        }

    def _get_max_stamina(self, level: int) -> int:
        return min(150, 100 + (level // 10) * 5)

    def _apply_stamina_recovery(self, player):
        """离线体力恢复 (每 5 分钟 1 点)"""
        now = datetime.utcnow()
        elapsed = max(0, int((now - player.updated_at).total_seconds()))
        recovered = int(elapsed / 300)
        if recovered > 0:
            max_sta = self._get_max_stamina(player.level)
            player.stamina = min(max_sta, player.stamina + recovered)
            self.repo.db.commit()

    def buy_stamina(self, player_id: int) -> dict:
        """购买体力"""
        player = self.repo.get_by_id(player_id)
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        if player.daily_stamina_bought >= 3:
            raise GameException(ErrorCode.DAILY_LIMIT, "今日购买次数已用完")
        prices = [50, 100, 150]
        cost = prices[player.daily_stamina_bought]
        if player.ingot < cost:
            raise GameException(ErrorCode.INGOT_NOT_ENOUGH, "元宝不足")
        player.ingot -= cost
        player.stamina = min(self._get_max_stamina(player.level), player.stamina + 60)
        player.daily_stamina_bought += 1
        self.repo.db.commit()
        return {
            "stamina": player.stamina,
            "max_stamina": self._get_max_stamina(player.level),
            "ingot": player.ingot,
            "bought_today": player.daily_stamina_bought,
            "cost": cost,
        }

    def _apply_level_hp_mp(self, player):
        """根据等级自动修正 HP/MP 上限（每级 +20HP / +10MP）"""
        expected_hp = 100 + max(0, player.level - 1) * 20
        expected_mp = 50 + max(0, player.level - 1) * 10
        need_commit = False
        if player.max_hp < expected_hp:
            player.max_hp = expected_hp
            need_commit = True
        if player.max_mp < expected_mp:
            player.max_mp = expected_mp
            need_commit = True
        if player.hp > player.max_hp:
            player.hp = player.max_hp
            need_commit = True
        if player.mp > player.max_mp:
            player.mp = player.max_mp
            need_commit = True
        if need_commit:
            self.repo.db.commit()

    def _check_new_skills(self, player):
        """根据等级解锁新技能"""
        from src.models.skill import SkillDefinition, PlayerSkill
        defs = self.repo.db.query(SkillDefinition).filter(
            SkillDefinition.school_id == player.school_id
        ).order_by(SkillDefinition.id).all()
        need_commit = False
        for i, sd in enumerate(defs):
            # 前2个技能Lv1解锁，之后每5级解锁一个
            if i < 2:
                required = 1
            else:
                required = (i - 1) * 5
            if player.level >= required:
                existing = self.repo.db.query(PlayerSkill).filter(
                    PlayerSkill.player_id == player.id,
                    PlayerSkill.skill_id == sd.id
                ).first()
                if not existing:
                    ps = PlayerSkill(
                        player_id=player.id, skill_id=sd.id,
                        level=1, proficiency=0, is_learned=1,
                    )
                    self.repo.db.add(ps)
                    need_commit = True
        if need_commit:
            self.repo.db.commit()

    def _check_new_tasks(self, player):
        """根据等级自动领取任务"""
        from src.models.task import TaskDefinition, PlayerTask
        from src.service.task_service import TaskService
        defs = self.repo.db.query(TaskDefinition).filter(
            TaskDefinition.min_level <= player.level
        ).order_by(TaskDefinition.sort_order).all()
        need_commit = False
        for td in defs:
            # 检查最大等级限制
            if td.max_level is not None and player.level > td.max_level:
                continue
            existing = self.repo.db.query(PlayerTask).filter(
                PlayerTask.player_id == player.id,
                PlayerTask.task_id == td.id
            ).first()
            if not existing:
                pt = PlayerTask(
                    player_id=player.id,
                    task_id=td.id,
                    progress=0,
                    target=td.requirement_value,
                    status=0,
                )
                self.repo.db.add(pt)
                need_commit = True
        if need_commit:
            self.repo.db.commit()
            # 对新任务执行进度检查，追溯已完成的条件
            ts = TaskService(self.repo.db)
            ts.check_progress(player.id, "reach_level", player.level)
            from src.repository.equipment_repo import EquipmentRepository
            equipped = EquipmentRepository(self.repo.db).get_equipped(player.id)
            if equipped:
                ts.check_progress(player.id, "equip_item", len(equipped))
            from src.service.battle_engine import BattleLog
            battle_count = self.repo.db.query(BattleLog).filter(
                BattleLog.attacker_id == player.id,
                BattleLog.battle_type == 1
            ).count() if hasattr(BattleLog, 'battle_type') else 0
            if battle_count:
                ts.check_progress(player.id, "pve_battle", battle_count)

    def _calc_combat_power(self, player) -> int:
        """计算角色战力"""
        from src.repository.equipment_repo import EquipmentRepository
        attr = self.repo.db.query(PlayerAttribute).filter(
            PlayerAttribute.player_id == player.id
        ).first()
        level_power = player.level * 10
        str_power = (attr.strength if attr else 10) * 2
        agi_power = (attr.agility if attr else 10) * 1
        con_power = (attr.constitution if attr else 10) * 3
        spi_power = (attr.spirit if attr else 10) * 2
        equip_repo = EquipmentRepository(self.repo.db)
        equipped = equip_repo.get_equipped(player.id)
        eq_attack = 0
        eq_defense = 0
        eq_hp = 0
        for eq in equipped:
            eq_attack += getattr(eq, "enhance_attack", 0) or 0
            eq_defense += getattr(eq, "enhance_defense", 0) or 0
            eq_hp += getattr(eq, "enhance_hp", 0) or 0
        equip_power = eq_attack + eq_defense * 2 + eq_hp // 2
        # 经脉加成
        meridian = self._calc_meridian_bonuses(player.id)
        meridian_power = meridian["attack"] + meridian["defense"] * 2 + meridian["hp"] // 2
        return int(level_power + str_power + agi_power + con_power + spi_power + equip_power + meridian_power)

    def _calc_meridian_bonuses(self, player_id: int) -> dict:
        """计算经脉加成总和"""
        from src.models.meridian import MeridianAcupoint
        from src.repository.meridian_repo import MeridianRepository
        repo = MeridianRepository(self.repo.db)
        pms = repo.get_all_player_meridians(player_id)
        total_hp = 0
        total_atk = 0
        total_def = 0
        total_spd = 0
        for pm in pms:
            acupoints = self.repo.db.query(MeridianAcupoint).filter(
                MeridianAcupoint.meridian_id == pm.meridian_id,
                MeridianAcupoint.position <= pm.current_acupoint
            ).all()
            for ap in acupoints:
                total_hp += ap.bonus_hp
                total_atk += ap.bonus_attack
                total_def += ap.bonus_defense
                total_spd += ap.bonus_speed
        return {"hp": total_hp, "attack": total_atk, "defense": total_def, "speed": total_spd}
