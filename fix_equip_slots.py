with open("E:/Project/jingwutang/frontend/pages/equipment.html", "r", encoding="utf-8") as f:
    c = f.read()

# Find the equipped slot rendering section
idx = c.find("var slots={1:")
if idx < 0:
    print("ERROR: slots not found")
    exit()

# Find the end of the equipped slot rendering
end_key = 'document.getElementById("equippedSlots").innerHTML=eh'
end_idx = c.find(end_key)
if end_idx < 0:
    print("ERROR: end marker not found")
    exit()

print("Found slot section from", idx, "to", end_idx + len(end_key))

# Extract the slot rendering code
old_code = c[idx:end_idx + len(end_key)]
print("OLD CODE:")
print(old_code[:300])
print("...")
print(old_code[-200:])
