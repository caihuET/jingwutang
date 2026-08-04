var API_BASE = '/jwt/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    var token = localStorage.getItem('token');
    if (!token) { window.location.href = '/jwt/'; return; }
    loadPlayerInfo();
    loadTitles();
});

function loadPlayerInfo() {
    showLoading(true);
    fetch(API_BASE + '/player/info?player_id=' + (localStorage.getItem('player_id') || 1), {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showLoading(false);
        if (data.code === 0) {
            renderPlayer(data.data);
        } else {
            showToast(data.message || '加载失败', 'error');
        }
    })
    .catch(function() { showLoading(false); showToast('网络异常', 'error'); });
}

function renderPlayer(p) {
    document.getElementById('playerName').textContent = p.name || '未知少侠';
    var titleEl = document.getElementById('playerTitle');
    if (titleEl) { titleEl.innerHTML = titleSpan(p); }
    document.getElementById('playerLevel').textContent = p.level || '-';
    document.getElementById('playerHp').textContent = (p.hp || 0) + '/' + (p.max_hp || 0);
    document.getElementById('playerMp').textContent = (p.mp || 0) + '/' + (p.max_mp || 0);
    document.getElementById('playerStamina').textContent = p.stamina || '-';
    document.getElementById('playerExp').textContent = p.exp || 0;
    document.getElementById('playerGold').textContent = p.gold || 0;
    document.getElementById('playerIngot').textContent = p.ingot || 0;
    document.getElementById('playerRep').textContent = p.reputation || 0;
    document.getElementById('playerPower').textContent = p.combat_power || '-';
}


function loadTitles() {
    var el = document.getElementById('titleList');
    if (!el) { return; }
    el.textContent = '加载中...';
    fetch(API_BASE + '/title/list?player_id=' + (localStorage.getItem('player_id') || 1), {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code !== 0) { el.textContent = d.message || '加载失败'; return; }
        renderTitles(d.data || []);
    })
    .catch(function() { el.textContent = '网络异常'; });
}


function renderTitles(titles) {
    var el = document.getElementById('titleList');
    if (!el) { return; }
    if (titles.length === 0) { el.textContent = '暂无称号'; return; }
    var html = '';
    for (var i = 0; i < titles.length; i++) {
        var t = titles[i];
        var color = titleColor(t.title_level || 1);
        var btn = t.is_equipped
            ? '<span class="btn btn-g" style="padding:2px 10px;font-size:11px" onclick="unequipTitle(' + t.title_id + ')">卸下</span>'
            : '<span class="btn btn-p" style="padding:2px 10px;font-size:11px" onclick="equipTitle(' + t.title_id + ')">佩戴</span>';
        html += '<div class="inv-item"><span><b style="color:' + color + '">' + t.name + '</b>' + (t.is_equipped ? ' (已佩戴)' : '') + '</span>' + btn + '</div>';
    }
    el.innerHTML = html;
}


function equipTitle(titleId) {
    fetch(API_BASE + '/title/equip?player_id=' + (localStorage.getItem('player_id') || 1), {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem('token')},
        body: JSON.stringify({title_id: titleId})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) { showToast('佩戴成功', 'success'); loadTitles(); loadPlayerInfo(); }
        else { showToast(d.message || '佩戴失败', 'error'); }
    })
    .catch(function() { showToast('网络异常', 'error'); });
}


function unequipTitle(titleId) {
    fetch(API_BASE + '/title/unequip?player_id=' + (localStorage.getItem('player_id') || 1), {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem('token')},
        body: JSON.stringify({title_id: titleId})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) { showToast('卸下成功', 'success'); loadTitles(); loadPlayerInfo(); }
        else { showToast(d.message || '卸下失败', 'error'); }
    })
    .catch(function() { showToast('网络异常', 'error'); });
}

function showLoading(v) {
    document.getElementById('pageLoading').style.display = v ? 'block' : 'none';
    document.getElementById('pageContent').style.display = v ? 'none' : 'block';
}

function showToast(msg, type) {
    var el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast show ' + type;
    clearTimeout(window._toastTimer);
    window._toastTimer = setTimeout(function() { el.classList.remove('show'); }, 2000);
}
