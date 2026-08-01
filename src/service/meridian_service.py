"""经脉服务"""
from src.repository.meridian_repo import MeridianRepository
from src.utils.errors import GameException
from src.utils.constants import ErrorCode
from src.models.meridian import MeridianDefinition, MeridianAcupoint


MERIDIAN_NAMES = ["任脉", "督脉", "冲脉", "带脉", "阴维脉"]
MERIDIAN_COUNTS = [12, 10, 10, 8, 8]


class MeridianService:
    def __init__(self, db):
        self.repo = MeridianRepository(db)
        self._ensure_seed_data()

    def _ensure_seed_data(self):
        """自动初始化经脉数据（若表为空）"""
        from sqlalchemy import text
        db = self.repo.db
        # 用原生 SQL 创建表（解决外键类型不匹配问题）
        db.execute(text("CREATE TABLE IF NOT EXISTS meridian_definitions ("
            "id INTEGER AUTO_INCREMENT PRIMARY KEY, "
            "name VARCHAR(16) NOT NULL, "
            "acupoint_count INTEGER DEFAULT 10, "
            "bonus_hp INTEGER DEFAULT 0, "
            "bonus_attack INTEGER DEFAULT 0, "
            "bonus_defense INTEGER DEFAULT 0"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"))
        db.execute(text("CREATE TABLE IF NOT EXISTS meridian_acupoints ("
            "id INTEGER AUTO_INCREMENT PRIMARY KEY, "
            "meridian_id INTEGER NOT NULL, "
            "position INTEGER NOT NULL, "
            "name VARCHAR(16) NOT NULL, "
            "reputation_cost INTEGER NOT NULL, "
            "bonus_hp INTEGER DEFAULT 0, "
            "bonus_attack INTEGER DEFAULT 0, "
            "bonus_defense INTEGER DEFAULT 0, "
            "bonus_speed INTEGER DEFAULT 0, "
            "INDEX idx_meridian (meridian_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"))
        db.execute(text("CREATE TABLE IF NOT EXISTS player_meridians ("
            "id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY, "
            "player_id BIGINT UNSIGNED NOT NULL, "
            "meridian_id INTEGER NOT NULL, "
            "current_acupoint INTEGER DEFAULT 0, "
            "INDEX idx_player (player_id)"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"))
        db.commit()
        # 检查是否已有经脉定义数据
        if self.repo.get_all_meridians():
            return
        # 注入经脉种子数据
        for i, name in enumerate(MERIDIAN_NAMES):
            count = MERIDIAN_COUNTS[i]
            hp = count * 8
            atk = count * 3 if i in (1, 4) else 0
            dfn = count * 3 if i == 2 else 0
            md = MeridianDefinition(name=name, acupoint_count=count, bonus_hp=hp, bonus_attack=atk, bonus_defense=dfn)
            db.add(md)
            db.flush()
            for pos in range(1, count + 1):
                cost = 20 + pos * 10
                bh = 5 + pos * 2
                ba = 1 + pos if i in (1, 4) else 0
                bd = 1 + pos if i == 2 else 0
                bs = 1 if i == 3 and pos % 3 == 0 else 0
                ap = MeridianAcupoint(meridian_id=md.id, position=pos, name=name + str(pos) + "穴",
                    reputation_cost=cost, bonus_hp=bh, bonus_attack=ba, bonus_defense=bd, bonus_speed=bs)
                db.add(ap)
        db.commit()

    def get_meridians(self, player_id: int) -> list:
        """获取经脉完整状态"""
        meridians = self.repo.get_all_meridians()
        result = []
        for md in meridians:
            acupoints = self.repo.get_acupoints(md.id)
            pm = self.repo.ensure_player_meridian(player_id, md.id)
            result.append({
                "meridian_id": md.id,
                "name": md.name,
                "acupoint_count": md.acupoint_count,
                "current_acupoint": pm.current_acupoint,
                "acupoints": [{
                    "id": ap.id,
                    "position": ap.position,
                    "name": ap.name,
                    "reputation_cost": ap.reputation_cost,
                    "bonus_hp": ap.bonus_hp,
                    "bonus_attack": ap.bonus_attack,
                    "bonus_defense": ap.bonus_defense,
                    "bonus_speed": ap.bonus_speed,
                    "unlocked": ap.position <= pm.current_acupoint,
                } for ap in acupoints],
                "total_unlocked": pm.current_acupoint,
            })
        return result

    def breakthrough(self, player_id: int, meridian_id: int) -> dict:
        """打通穴位"""
        from src.models.player import Player
        md = self.repo.get_meridian_def(meridian_id)
        if not md:
            raise GameException(ErrorCode.PARAM_INVALID, "经脉不存在")
        acupoints = self.repo.get_acupoints(meridian_id)
        pm = self.repo.ensure_player_meridian(player_id, meridian_id)
        if pm.current_acupoint >= md.acupoint_count:
            raise GameException(ErrorCode.PARAM_INVALID, "该经脉已全部打通")
        next_pos = pm.current_acupoint + 1
        next_acupoint = None
        for ap in acupoints:
            if ap.position == next_pos:
                next_acupoint = ap
                break
        if not next_acupoint:
            raise GameException(ErrorCode.PARAM_INVALID, "穴位不存在")
        player = self.repo.db.query(Player).filter(Player.id == player_id).first()
        if not player:
            raise GameException(ErrorCode.PARAM_INVALID, "角色不存在")
        # 检查修为
        cost = next_acupoint.reputation_cost
        if player.reputation < cost:
            raise GameException(ErrorCode.REPUTATION_NOT_ENOUGH, "修为不足")
        player.reputation -= cost
        pm.current_acupoint = next_pos
        # 检查是否经脉圆满额外加成
        extra_reputation = 0
        if pm.current_acupoint == md.acupoint_count:
            extra_reputation = md.bonus_hp + md.bonus_attack + md.bonus_defense
        self.repo.db.commit()
        # 通知任务系统
        try:
            from src.service.task_service import TaskService
            ts = TaskService(self.repo.db)
            ts.check_progress(player_id, "breakthrough", 1)
            if pm.current_acupoint == md.acupoint_count:
                ts.check_progress(player_id, "meridian_complete", 1)
        except Exception:
            pass
        return {
            "meridian_id": meridian_id,
            "current_acupoint": pm.current_acupoint,
            "acupoint_name": next_acupoint.name,
            "cost": cost,
            "reputation_left": player.reputation,
            "complete": pm.current_acupoint == md.acupoint_count,
        }
