var API_BASE = '/game/jwt/api/v1';
var MONSTERS = {1:{name:'山贼甲',level:3,hp:60,exp:30,gold:15},2:{name:'山贼头目',level:5,hp:100,exp:60,gold:30},3:{name:'青云山贼',level:8,hp:150,exp:100,gold:45},4:{name:'山寇首领',level:12,hp:250,exp:180,gold:80}};

document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    renderMaps();
    document.getElementById('battleBtn').addEventListener('click', startBattle);
});

function renderMaps() {
    var html = '';
    for (var id in MONSTERS) {
        var m = MONSTERS[id];
        html += '<div class="map-card" data-id="' + id + '" onclick="selectMap(this)">';
        html += '<div class="map-name">' + m.name + '</div>';
        html += '<div class="map-info">Lv.' + m.level + ' | HP:' + m.hp + '</div>';
        html += '<div class="map-info">经验:' + m.exp + ' 金币:' + m.gold + '</div>';
        html += '</div>';
    }
    document.getElementById('mapGrid').innerHTML = html;
}

function selectMap(el) {
    document.querySelectorAll('.map-card').forEach(function(c) { c.classList.remove('selected'); });
    el.classList.add('selected');
    document.getElementById('battleBtn').disabled = false;
    document.getElementById('selectedMapId').value = el.dataset.id;
}

function startBattle() {
    var mapId = document.getElementById('selectedMapId').value;
    if (!mapId) { showToast('请选择目标', 'error'); return; }
    showLoading(true);
    document.getElementById('battleResult').style.display = 'none';
    fetch(API_BASE + '/battle/pve', {
        method: 'POST',
        headers: {'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({map_id: parseInt(mapId)})
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showLoading(false);
        if (data.code === 0) { renderResult(data.data); }
        else { showToast(data.message || '战斗失败', 'error'); }
    })
    .catch(function() { showLoading(false); showToast('网络异常', 'error'); });
}

function renderResult(r) {
    document.getElementById('battleResult').style.display = 'block';
    var resultEl = document.getElementById('battleResultText');
    resultEl.textContent = r.result === 'win' ? '胜 利' : '败 北';
    resultEl.style.color = r.result === 'win' ? '#2ecc71' : '#e74c3c';
    document.getElementById('battleRounds').textContent = r.rounds || '-';
    document.getElementById('battleExp').textContent = r.exp_gained || 0;
    document.getElementById('battleGold').textContent = r.gold_gained || 0;
    document.getElementById('staminaCost').textContent = r.stamina_consumed || 10;
    renderBattleLog(r.log || []);
}

function renderBattleLog(log) {
    var html = '';
    for (var i = 0; i < log.length; i++) {
        var rd = log[i];
        html += '<div class="round-header">— 第 ' + rd.round + ' 回合 —</div>';
        for (var j = 0; j < (rd.actions || []).length; j++) {
            var a = rd.actions[j];
            var line = '<div class="action">' + a.actor + ' 使出『' + a.skill + '』';
            if (a.dodged) { line += '，<span class="dodge">被 ' + a.target + ' 闪避</span>'; }
            else {
                line += '，对 ' + a.target + ' 造成 <span class="dmg">' + a.damage + '</span> 点伤害';
                if (a.critical) { line += ' <span class="crit">【暴击】</span>'; }
            }
            line += '</div>';
            html += line;
        }
    }
    document.getElementById('battleLog').innerHTML = html || '<div class="action">没有战斗记录</div>';
}
