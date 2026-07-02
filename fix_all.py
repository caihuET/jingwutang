import sys, re
sys.stdout.reconfigure(encoding="utf-8")
# 1 equipment
c=open("frontend/pages/equipment.html",encoding="utf-8").read()
c=re.sub(r"<title>[^<]*</title>","<title>装备 | 精武堂</title>",c)
c=c.replace("</head>",'<script src="/game/jwt/static/js/common.js"></script>\n</head>')
c=c.replace("</body>",'<script src="/game/jwt/static/js/equipment.js"></script>\n</body>')
open("frontend/pages/equipment.html","w",encoding="utf-8").write(c)
# 2 skills
c=open("frontend/pages/skills.html",encoding="utf-8").read()
c=re.sub(r"<title>[^<]*</title>","<title>技能 | 精武堂</title>",c)
c=c.replace("</head>",'<script src="/game/jwt/static/js/common.js"></script>\n</head>')
m='<style>\n.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center}\n.modal-overlay.show{display:flex}\n.modal-content{background:white;border-radius:8px;padding:20px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto}\n</style>\n<div id="slotModal" class="modal-overlay" onclick="closeModal()">\n<div class="modal-content" id="modalContent"></div>\n</div>'
if "slotModal" not in c:c=c.replace("</body>",m+"\n</body>")
open("frontend/pages/skills.html","w",encoding="utf-8").write(c)
# 3 common.js
c=open("static/js/common.js",encoding="utf-8").read()
for k,v in [("game.html","江湖首页"),("player.html","角色信息"),("equipment.html","背包行囊"),("skills.html","武学技能"),("meridians.html","经脉修炼"),("battle.html","闯荡江湖"),("tasks.html","任务"),("ranking.html","排行榜"),("shop.html","商城")]:
    c=re.sub(r"(label:'/game/jwt/" + k + r"',\s*label:')[^']*'",r"\1" + v + "'",c)
open("static/js/common.js","w",encoding="utf-8").write(c)
# 4 skills.js
c=open("static/js/skills.js",encoding="utf-8").read()
c=c.replace("'技能#' + s.skill_id","s.name || '技能#' + s.skill_id")
open("static/js/skills.js","w",encoding="utf-8").write(c)
# 5 tasks.js
c=open("static/js/tasks.js",encoding="utf-8").read()
c=c.replace("'/task/list?player_id=1'","'/task/list?player_id='+(localStorage.getItem('player_id')||1)")
c=c.replace("JSON.stringify({task_id:taskId})",'JSON.stringify({task_id:taskId,player_id:parseInt(localStorage.getItem("player_id"))||1})')
c=c.replace("JSON.stringify({task_id: taskId})",'JSON.stringify({task_id: taskId,player_id: parseInt(localStorage.getItem("player_id"))||1})')
open("static/js/tasks.js","w",encoding="utf-8").write(c)
# 6 task.py
c=open("src/api/task.py",encoding="utf-8").read()
c=c.replace("def claim_reward(req: ClaimRequest, player_id: int = 1,","def claim_reward(req: ClaimRequest,")
c=c.replace("def accept_task(req: AcceptRequest, player_id: int = 1,","def accept_task(req: AcceptRequest,")
c=c.replace("TaskService(db).claim_reward(player_id, req.task_id)","TaskService(db).claim_reward(req.player_id, req.task_id)")
c=c.replace("TaskService(db).accept_task(player_id, req.task_id)","TaskService(db).accept_task(req.player_id, req.task_id)")
open("src/api/task.py","w",encoding="utf-8").write(c)
print("完成")
