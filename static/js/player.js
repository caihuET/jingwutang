var API_BASE = '/game/jwt/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    var token = localStorage.getItem('token');
    if (!token) { window.location.href = '/game/jwt/'; return; }
    loadPlayerInfo();
});

function loadPlayerInfo() {
    showLoading(true);
    fetch(API_BASE + '/player/info?player_id=1', {
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

function showLoading(v) {
    document.getElementById('pageLoading').style.display = v ? 'block' : 'none';
    document.getElementById('pageContent').style.display = v ? 'none' : 'block';
}

function showToast(msg, type) {
    var el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast show ' + type;
    setTimeout(function() { el.classList.remove('show'); }, 3000);
}
