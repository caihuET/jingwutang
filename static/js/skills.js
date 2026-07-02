var API_BASE = '/game/jwt/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    loadSkills();
});

function loadSkills() {
    showLoading(true);
    fetch(API_BASE + '/skill/list?player_id=1', {
        headers: {'Authorization':'Bearer '+localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showLoading(false);
        if (data.code === 0) { renderSkills(data.data || []); }
        else { showToast(data.message || '加载失败', 'error'); }
    })
    .catch(function() { showLoading(false); showToast('网络异常', 'error'); });
}

function renderSkills(skills) {
    var slotted = skills.filter(function(s) { return s.slot_position !== null; });
    var learned = skills.filter(function(s) { return s.slot_position === null && s.is_learned === 1; });
    renderSlotGrid(slotted, skills);
    renderLearned(learned);
}

function renderSlotGrid(slotted, allSkills) {
    var html = '';
    for (var i = 1; i <= 4; i++) {
        var s = slotted.find(function(x) { return x.slot_position === i; });
        html += '<div class="stat-card" style="min-width:140px;cursor:pointer" onclick="openSlotSelector(' + i + ')">';
        html += '<div class="label">技能槽 ' + i + '</div>';
        if (s) { html += '<div class="value" style="font-size:16px">s.name || s.name || s.name || s.name || s.name || s.name || '技能#' + s.skill_id + '</div><div class="label">Lv.' + s.level + '</div>'; }
        else { html += '<div class="value" style="font-size:14px;color:#6b5b4e">- 空 -</div>'; }
        html += '</div>';
    }
    document.getElementById('slotGrid').innerHTML = html;
    window._allSkills = allSkills;
}

function renderLearned(skills) {
    if (skills.length === 0) {
        document.getElementById('skillList').innerHTML = '<div class="text-muted">暂无已学技能</div>';
        return;
    }
    var html = '<table class="data-table"><tr><th>技能</th><th>等级</th><th>熟练度</th><th>操作</th></tr>';
    for (var i = 0; i < skills.length; i++) {
        var s = skills[i];
        html += '<tr><td>s.name || s.name || s.name || s.name || s.name || s.name || '技能#' + s.skill_id + '</td><td>Lv.' + s.level + '</td><td>' + s.proficiency + '</td>';
        html += '<td><button class="btn btn-sm btn-secondary" onclick="openSlotSelector(0,' + s.id + ')">设为出战</button></td></tr>';
    }
    html += '</table>';
    document.getElementById('skillList').innerHTML = html;
}

function openSlotSelector(slotIdx, skillId) {
    var skills = window._allSkills || [];
    var html = '<h3>选择出战技能</h3>';
    html += '<table class="data-table"><tr><th>技能</th><th>等级</th><th>熟练度</th><th>选择</th></tr>';
    for (var i = 0; i < skills.length; i++) {
        var s = skills[i];
        html += '<tr><td>s.name || s.name || s.name || s.name || s.name || s.name || '技能#' + s.skill_id + '</td><td>Lv.' + s.level + '</td><td>' + s.proficiency + '</td>';
        var checked = s.slot_position === slotIdx ? 'checked' : '';
        html += '<td><input type="radio" name="slotSkill" value="' + s.id + '" ' + checked + '></td></tr>';
    }
    html += '</table>';
    html += '<div class="modal-actions">';
    html += '<button class="btn btn-sm btn-secondary" onclick="closeModal()">取消</button>';
    html += '<button class="btn btn-sm btn-danger" onclick="saveSlots(' + slotIdx + ')">保存</button>';
    html += '</div>';
    document.getElementById('modalContent').innerHTML = html;
    document.getElementById('slotModal').classList.add('show');
}

function saveSlots(slotIdx) {
    var selected = document.querySelector('input[name="slotSkill"]:checked');
    if (!selected) { showToast('请选择一个技能', 'error'); return; }
    var skills = window._allSkills || [];
    var newSlots = [];
    for (var i = 0; i < skills.length; i++) {
        var s = skills[i];
        if (s.slot_position !== null && s.slot_position !== slotIdx) { newSlots.push(s.id); }
    }
    newSlots.push(parseInt(selected.value));
    if (newSlots.length > 4) newSlots = newSlots.slice(-4);
    showToast('保存中...', 'info');
    fetch(API_BASE + '/skill/slot', {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({skill_ids: newSlots})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        closeModal();
        if (d.code === 0) { showToast('设置成功', 'success'); loadSkills(); }
        else { showToast(d.message || '保存失败', 'error'); }
    })
    .catch(function() { closeModal(); showToast('网络异常', 'error'); });
}

function closeModal() { document.getElementById('slotModal').classList.remove('show'); }
