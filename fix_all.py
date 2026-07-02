import sys, re
sys.stdout.reconfigure(encoding="utf-8")

# ========== 1. skills.html ==========
c = open("frontend/pages/skills.html", encoding="utf-8").read()
c = re.sub(r"<title>.*?</title>", "<title>技能 | 精武堂</title>", c, flags=re.DOTALL)
c = c.replace('<script src="/game/jwt/static/js/skills.js">', 
              '<script src="/game/jwt/static/js/common.js"></script>\n<script src="/game/jwt/static/js/skills.js">')
if "slotModal" not in c:
    modal = '''<style>
.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center}
.modal-overlay.show{display:flex}
.modal-content{background:white;border-radius:8px;padding:20px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto}
</style>
<div id="slotModal" class="modal-overlay" onclick="closeModal()">
<div class="modal-content" id="modalContent"></div>
</div>'''
    c = c.replace("</body>", modal + "\n</body>")
open("frontend/pages/skills.html", "w", encoding="utf-8").write(c)
print("1/4 skills.html OK")

# ========== 2. task.py ==========
c = open("src/api/task.py", encoding="utf-8").read()
c = c.replace("def claim_reward(req: ClaimRequest, player_id: int = 1,", "def claim_reward(req: ClaimRequest,")
c = c.replace("def accept_task(req: AcceptRequest, player_id: int = 1,", "def accept_task(req: AcceptRequest,")
c = c.replace("TaskService(db).claim_reward(player_id, req.task_id)", "TaskService(db).claim_reward(req.player_id, req.task_id)")
c = c.replace("TaskService(db).accept_task(player_id, req.task_id)", "TaskService(db).accept_task(req.player_id, req.task_id)")
open("src/api/task.py", "w", encoding="utf-8").write(c)
print("2/4 task.py OK")

# ========== 3. tasks.js ==========
c = open("static/js/tasks.js", encoding="utf-8").read()
c = c.replace("'/task/list?player_id=1'", "'/task/list?player_id='+(localStorage.getItem('player_id')||1)")
c = c.replace('JSON.stringify({task_id:taskId})', 'JSON.stringify({task_id:taskId,player_id:parseInt(localStorage.getItem("player_id"))||1})')
c = c.replace('JSON.stringify({task_id: taskId})', 'JSON.stringify({task_id: taskId,player_id: parseInt(localStorage.getItem("player_id"))||1})')
open("static/js/tasks.js", "w", encoding="utf-8").write(c)
print("3/4 tasks.js OK")

# ========== 4. task_service.py ==========
c = open("src/service/task_service.py", encoding="utf-8").read()
if "def auto_assign_tasks" in c:
    lines = c.split("\n")
    keep = []
    skip = 0
    for l in lines:
        if l.strip().startswith("def auto_assign_tasks") or l.strip().startswith("def daily_refresh"):
            skip = 1; continue
        if skip and (l.strip().startswith("def ") or l.strip().startswith("class ")):
            skip = 0; keep.append(l); continue
        if not skip: keep.append(l)
    open("src/service/task_service.py", "w", encoding="utf-8").write("\n".join(keep))
print("4/4 task_service.py OK")

print("\n所有修复完成！请执行 git diff --stat 验证")