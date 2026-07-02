import sys
sys.stdout.reconfigure(encoding="utf-8")

# equipment.html - 用 find+replace（100%可靠）
c = open("frontend/pages/equipment.html", encoding="utf-8").read()
old = c
start = c.find("<title>")
end = c.find("</title>")
if start >= 0: c = c[:start] + "<title>装备 | 精武堂</title>" + c[end+8:]
c = c.replace("</head>", "<script src=\"/game/jwt/static/js/common.js\"></script>\n</head>")
c = c.replace("</body>", "<script src=\"/game/jwt/static/js/equipment.js\"></script>\n</body>")
if c != old:
    open("frontend/pages/equipment.html", "w", encoding="utf-8").write(c)
    print("equipment.html OK")

# skills.html
c = open("frontend/pages/skills.html", encoding="utf-8").read()
old = c
start = c.find("<title>")
end = c.find("</title>")
if start >= 0: c = c[:start] + "<title>技能 | 精武堂</title>" + c[end+8:]
c = c.replace("</head>", "<script src=\"/game/jwt/static/js/common.js\"></script>\n</head>")
modal = "<style>\n.modal-overlay{display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.5);z-index:1000;align-items:center;justify-content:center}\n.modal-overlay.show{display:flex}\n.modal-content{background:white;border-radius:8px;padding:20px;max-width:500px;width:90%;max-height:80vh;overflow-y:auto}\n</style>\n<div id=\"slotModal\" class=\"modal-overlay\" onclick=\"closeModal()\">\n<div class=\"modal-content\" id=\"modalContent\"></div>\n</div>"
if "slotModal" not in c:
    c = c.replace("</body>", modal + "\n</body>")
if c != old:
    open("frontend/pages/skills.html", "w", encoding="utf-8").write(c)
    print("skills.html OK")