import sys
sys.stdout.reconfigure(encoding="utf-8")

# task.py
c = open("src/api/task.py", encoding="utf-8").read()
c = c.replace("def claim_reward(req: ClaimRequest, player_id: int = 1,", "def claim_reward(req: ClaimRequest,")
c = c.replace("def accept_task(req: AcceptRequest, player_id: int = 1,", "def accept_task(req: AcceptRequest,")
c = c.replace("TaskService(db).claim_reward(player_id, req.task_id)", "TaskService(db).claim_reward(req.player_id, req.task_id)")
c = c.replace("TaskService(db).accept_task(player_id, req.task_id)", "TaskService(db).accept_task(req.player_id, req.task_id)")
open("src/api/task.py", "w", encoding="utf-8").write(c)
print("task.py OK")

# tasks.js
c = open("static/js/tasks.js", encoding="utf-8").read()
c = c.replace("'/task/list?player_id=1'", "'/task/list?player_id='+(localStorage.getItem('player_id')||1)")
c = c.replace('JSON.stringify({task_id:taskId})', 'JSON.stringify({task_id:taskId,player_id:parseInt(localStorage.getItem("player_id"))||1})')
c = c.replace('JSON.stringify({task_id: taskId})', 'JSON.stringify({task_id: taskId,player_id: parseInt(localStorage.getItem("player_id"))||1})')
open("static/js/tasks.js", "w", encoding="utf-8").write(c)
print("tasks.js OK")
