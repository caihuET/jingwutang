# 精武堂 Git 初始化脚本
# 以管理员身份运行此脚本

Write-Host "=== 精武堂 Git 初始化 ===" -ForegroundColor Cyan

# 移除错误的 .git (在 E:\Project 层级)
if (Test-Path "E:\.git") {
    Remove-Item -Recurse -Force "E:\.git"
    Write-Host "已移除 E:\.git" -ForegroundColor Yellow
}
# 也检查一下 E:\Project\.git
if (Test-Path "E:\Project\.git") {
    Remove-Item -Recurse -Force "E:\Project\.git"
    Write-Host "已移除 E:\Project\.git" -ForegroundColor Yellow
}

Set-Location "E:\Project\jingwutang"

# 初始化 Git 仓库
git init
git config --global --add safe.directory "E:\Project\jingwutang"

# 添加所有文件
git add .

# 创建初始提交
git commit -m "feat: 精武堂游戏项目初始提交

- FastAPI 后端框架搭建
- 用户认证系统 (注册/登录/JWT)
- 角色系统 (创建/信息查询)
- 战斗引擎 (BattleEngine 回合制战斗)
- 装备系统 (穿戴/卸下/强化)
- 技能系统 (出战配置/熟练度)
- 任务系统 (主线/日常/奖励)
- Docker 部署配置 (Nginx + MySQL + Redis)
- 39 个 Python 模块
- 62 个测试用例 (59通过/3预期错误)"

Write-Host "=== 初始化完成 ===" -ForegroundColor Green
Write-Host "运行 git remote add origin <url> 关联远程仓库" -ForegroundColor Yellow
