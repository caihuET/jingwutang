with open("E:/Project/jingwutang/frontend/pages/meridians.html", "r", encoding="utf-8") as f:
    c = f.read()

# Find the player info .then() callback section
old = "  if(document.getElementById(" + chr(34) + "merRep" + chr(34) + "))document.getElementById(" + chr(34) + "merRep" + chr(34) + ").textContent=" + chr(34) + "\u4fee\u4e3a: " + chr(34) + "+(p.reputation||0);"

new = old + chr(10)
new += "  // Update sidebar from API data" + chr(10)
new += "  var sn=document.querySelector(" + chr(34) + ".sidebar .profile .name" + chr(34) + ");if(sn)sn.textContent=p.name;" + chr(10)
new += "  var si=document.querySelector(" + chr(34) + ".sidebar .profile .info" + chr(34) + ");if(si)si.textContent=" + chr(34) + "Lv." + chr(34) + "+p.level+" + chr(34) + " | " + chr(34) + "+p.school_name+" + chr(34) + " | \u6218\u529b " + chr(34) + "+(p.combat_power||0);" + chr(10)
new += "  var ehp=p.effective_max_hp||p.max_hp;" + chr(10)
new += "  var hps=document.querySelector(" + chr(34) + ".sidebar .stats .srow:nth-child(1) span:last-child" + chr(34) + ");if(hps)hps.textContent=p.hp+"/"+ehp;" + chr(10)
new += "  var mps=document.querySelector(" + chr(34) + ".sidebar .stats .srow:nth-child(2) span:last-child" + chr(34) + ");if(mps)mps.textContent=p.mp+"/"+p.max_mp;" + chr(10)
new += "  var sts=document.querySelector(" + chr(34) + ".sidebar .stats .srow:nth-child(3) span:last-child" + chr(34) + ");if(sts)sts.textContent=p.stamina;"

if old in c:
    c = c.replace(old, new, 1)
    print("Sidebar update added!")
else:
    print("Pattern not found!")
    # Debug
    idx = c.find("merRep")
    if idx>=0:
        print("Found merRep:", repr(c[idx:idx+100]))

with open("E:/Project/jingwutang/frontend/pages/meridians.html", "w", encoding="utf-8") as f:
    f.write(c)
print("Done")
