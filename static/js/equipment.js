var API_BASE = '/game/jwt/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    loadEquipment();
});

function loadEquipment() {
    showLoading(true);
    fetch(API_BASE + '/equipment/list?player_id=1', {
        headers: {'Authorization':'Bearer '+localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showLoading(false);
        if (data.code === 0) { renderEquipment(data.data || []); }
        else { showToast(data.message || '加载失败', 'error'); }
    })
    .catch(function() { showLoading(false); showToast('网络异常', 'error'); });
}

function renderEquipment(items) {
    var equipped = items.filter(function(i) { return i.is_equipped === 1; });
    var bag = items.filter(function(i) { return i.is_equipped === 0; });
    renderEquipped(equipped);
    renderBag(bag);
}

function renderEquipped(items) {
    var slots = {1:'武器',2:'防具',3:'饰品',4:'坐骑'};
    var html = '';
    for (var i = 1; i <= 4; i++) {
        var eq = items.find(function(e) { return e.slot === i; });
        html += '<div class="stat-card" style="min-width:120px">';
        html += '<div class="label">' + slots[i] + '</div>';
        if (eq) {
            html += '<div class="value" style="font-size:16px">' + eq.name + '</div>';
            html += '<div class="label">+' + (eq.enhance_level||0) + ' ' + qName(eq.quality) + '</div>';
        } else {
            html += '<div class="value" style="font-size:14px;color:#6b5b4e">- 空 -</div>';
        }
        html += '</div>';
    }
    document.getElementById('equippedSlots').innerHTML = html;
}

function renderBag(items) {
    if (items.length === 0) {
        document.getElementById('bagContent').innerHTML = '<div class="text-muted">背包空空如也</div>';
        return;
    }
    var html = '<table class="data-table"><tr><th>名称</th><th>品质</th><th>部位</th><th>强化</th><th>操作</th></tr>';
    for (var i = 0; i < items.length; i++) {
        var e = items[i];
        var qCls = 'q' + Math.min(e.quality, 5);
        html += '<tr><td class="' + qCls + '">' + e.name + '</td>';
        html += '<td><span class="quality-tag ' + qCls + '">' + qName(e.quality) + '</span></td>';
        html += '<td>' + slotName(e.slot) + '</td>';
        html += '<td>+' + (e.enhance_level||0) + '</td>';
        html += '<td class="flex gap-8">';
        html += '<button class="btn btn-sm btn-secondary" onclick="doEquip(' + e.id + ')">穿戴</button>';
        html += '<button class="btn btn-sm btn-success" onclick="doEnhance(' + e.id + ')">强化</button></td></tr>';
    }
    html += '</table>';
    document.getElementById('bagContent').innerHTML = html;
}

function renderEquippedTable(items) {
    if (items.length === 0) return;
    var html = '<table class="data-table"><tr><th>名称</th><th>品质</th><th>强化</th><th>操作</th></tr>';
    for (var i = 0; i < items.length; i++) {
        var e = items[i];
        html += '<tr><td>' + e.name + '</td>';
        html += '<td><span class="quality-tag q' + e.quality + '">' + qName(e.quality) + '</span></td>';
        html += '<td>+' + (e.enhance_level||0) + '</td>';
        html += '<td><button class="btn btn-sm btn-secondary" onclick="doUnequip(' + e.id + ')">卸下</button></td></tr>';
    }
    html += '</table>';
    document.getElementById('equippedTable').innerHTML = html;
}

function doEquip(id) {
    showToast('穿戴中...', 'info');
    fetch(API_BASE + '/equipment/equip', {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({equip_id: id})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) { showToast('穿戴成功', 'success'); loadEquipment(); }
        else { showToast(d.message || '操作失败', 'error'); }
    })
    .catch(function() { showToast('网络异常', 'error'); });
}

function doUnequip(id) {
    showToast('卸下中...', 'info');
    fetch(API_BASE + '/equipment/unequip', {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({equip_id: id})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) { showToast('卸下成功', 'success'); loadEquipment(); }
        else { showToast(d.message || '操作失败', 'error'); }
    })
    .catch(function() { showToast('网络异常', 'error'); });
}

function doEnhance(id) {
    showToast('强化中...', 'info');
    fetch(API_BASE + '/equipment/enhance', {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({equip_id: id})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) {
            showToast(d.data.success ? '强化成功！+'+d.data.new_level : '强化失败', d.data.success ? 'success' : 'error');
            loadEquipment();
        } else { showToast(d.message || '操作失败', 'error'); }
    })
    .catch(function() { showToast('网络异常', 'error'); });
}
