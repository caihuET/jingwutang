var API_BASE = '/game/jwt/api/v1';

var SIDEBAR_LINKS = [
    {href:'/game/jwt/game.html', label:'江湖首页'},
    {href:'/game/jwt/player.html', label:'角色信息'},
    {href:'/game/jwt/equipment.html', label:'背包行囊'},
    {href:'/game/jwt/skills.html', label:'武学技能'},
    {href:'/game/jwt/meridians.html', label:'经脉修炼'},
    {href:'/game/jwt/battle.html', label:'闯荡江湖'},
    {href:'/game/jwt/tasks.html', label:'任务'},
    {href:'/game/jwt/ranking.html', label:'排行榜'},
    {href:'/game/jwt/shop.html', label:'商城'},
];

function checkAuth() {
    var t = localStorage.getItem('token');
    if (!t) { window.location.href = '/game/jwt/'; return false; }
    return true;
}

function handleLogout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    window.location.href = '/game/jwt/';
}

function showToast(msg, type) {
    var el = document.getElementById('toast');
    if (!el) { el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; document.body.appendChild(el); }
    el.textContent = msg;
    el.className = 'toast show ' + (type || 'info');
    setTimeout(function() { el.classList.remove('show'); }, 3000);
}

function showLoading(v) {
    var el = document.getElementById('pageLoading');
    var ct = document.getElementById('pageContent');
    if (el) el.style.display = v ? 'block' : 'none';
    if (ct) ct.style.display = v ? 'none' : 'block';
}

function qName(quality) {
    var names = {1:'普通',2:'优秀',3:'精良',4:'史诗',5:'传说'};
    return names[quality] || '未知';
}

function slotName(slot) {
    var names = {1:'武器',2:'防具',3:'饰品',4:'坐骑'};
    return names[slot] || '未知';
}

function loadSidebar() {
    var el = document.getElementById('sidebar');
    if (!el) return;
    var cur = window.location.pathname;
    var html = '';
    for (var i = 0; i < SIDEBAR_LINKS.length; i++) {
        var link = SIDEBAR_LINKS[i];
        var active = cur === link.href ? ' class="active"' : '';
        html += '<a href="' + link.href + '"' + active + '>' + link.label + '</a>';
    }
    el.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', loadSidebar);


function titleSpan(p) {
    if (!p || !p.title || !p.title.name) { return ''; }
    var lv = p.title.title_level || 1;
    var color = titleColor(lv);
    var glow = lv >= 3 ? 'text-shadow:0 0 6px ' + color + ';' : '';
    return ' <span class="title-tag" style="color:' + color + ';font-size:0.85em;' + glow + '">[' + p.title.name + ']</span>';
}


function renderTopPlayer(p) {
    return (p.name || '-') + ' Lv.' + (p.level || 1) + titleSpan(p);
}


function renderPlayerName(p) {
    return (p.name || '-') + titleSpan(p);
}


function titleColor(lv) {
    var colors = {1: '#9e9e9e', 2: '#4caf50', 3: '#9c27b0', 4: '#ffb300'};
    return colors[lv] || '#c9a96e';
}
