var API_BASE = '/game/jwt/api/v1';

var SIDEBAR_LINKS = [
    {href:'/game/jwt/battle.html', label:'历练'},
    {href:'/game/jwt/equipment.html', label:'装备'},
    {href:'/game/jwt/skills.html', label:'技能'},
    {href:'/game/jwt/meridians.html', label:'经脉'},
    {href:'/game/jwt/tasks.html', label:'任务'},
    {href:'/game/jwt/ranking.html', label:'排行'},
    {href:'/game/jwt/shop.html', label:'商城'},
    {href:'/game/jwt/friend.html', label:'好友'},
    {href:'/game/jwt/guild.html', label:'帮派'},
    {href:'/game/jwt/equip-guide.html', label:'装备说明'},
];

function checkAuth() {
    var t = localStorage.getItem('token');
    if (!t) { window.location.href = '/game/jwt/'; return false; }
    return true;
}

function handleLogout() {
    if (window._gcWs) { try { window._gcWs.close(); } catch (e) {} }
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('player_id');
    sessionStorage.removeItem('gcState');
    window.location.href = '/game/jwt/';
}

function showToast(msg, type) {
    var el = document.getElementById('toast');
    if (!el) { el = document.createElement('div'); el.id = 'toast'; el.className = 'toast'; document.body.appendChild(el); }
    el.textContent = msg;
    el.className = 'toast show ' + (type || 'info');
    setTimeout(function() { el.classList.remove('show'); }, 3000);
}

function showFriendNotice(msg) {
    var el = document.getElementById('friendNotice');
    if (!el) {
        el = document.createElement('div');
        el.id = 'friendNotice';
        el.style.cssText = 'position:fixed;top:60px;right:16px;z-index:10001;background:#8b1a1a;color:#c9a96e;padding:10px 14px;border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,.3);font-size:13px;display:none';
        document.body.appendChild(el);
    }
    el.textContent = msg;
    el.style.display = 'block';
    clearTimeout(window._friendNoticeTimer);
    window._friendNoticeTimer = setTimeout(function() { el.style.display = 'none'; }, 4000);
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
    var names = {1:'武器',2:'头盔',3:'衣甲',4:'腰带',5:'靴子',6:'项链'};
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
    lv = lv >= 4 ? 4 : lv;
    var colors = {1: '#9e9e9e', 2: '#4caf50', 3: '#9c27b0', 4: '#ffb300'};
    return colors[lv] || '#ffb300';
}


/* 全局聊天窗（世界/帮派/私聊，WebSocket 实时） */
function initGlobalChat() {
    if (!localStorage.getItem('token')) { return; }
    if (location.pathname.indexOf('create.html') >= 0) { return; }
    if (location.pathname.indexOf('chat.html') >= 0) { return; }
    if (document.getElementById('globalChat')) { return; }
    window._gcPid = parseInt(localStorage.getItem('player_id')) || 1;
    window._gcChannel = 1;
    window._gcUnread = {1: 0, 2: 0, 3: 0};
    window._gcMsgs = {1: [], 2: []};
    window._gcPrivate = [];
    window._gcPrivateFriend = '';
    window._gcPrivateName = '';
    window._gcFriends = {};
    window._gcWs = null;
    window._gcPoll = null;

    var css = document.createElement('style');
    css.id = 'gcStyle';
    css.textContent =
        '.global-chat{position:fixed;left:212px;bottom:12px;width:480px;height:380px;background:white;border:1px solid #c9a96e;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,.25);display:flex;flex-direction:column;z-index:9999;overflow:hidden}' +
        '.gc-head{background:linear-gradient(90deg,#1a1a2e,#2c2c44);color:#c9a96e;padding:6px 10px;display:flex;align-items:center;gap:8px;flex-shrink:0}' +
        '.gc-head .gc-title{font-weight:700;font-size:13px;margin-right:auto}' +
        '.gc-tabs{display:flex;gap:2px}' +
        '.gc-tab{padding:3px 8px;font-size:11px;cursor:pointer;border-radius:4px;position:relative}' +
        '.gc-tab.active{background:rgba(201,169,110,.25);color:#fff}' +
        '.gc-badge{position:absolute;top:-4px;right:-4px;background:#e53935;color:#fff;font-size:9px;border-radius:8px;padding:0 4px;display:none}' +
        '.gc-min{cursor:pointer;font-size:14px;padding:0 4px}' +
        '.gc-body{flex:1;overflow-y:auto;padding:8px 10px;font-size:12px}' +
        '.gc-msg{margin-bottom:6px}' +
        '.gc-msg .head{color:#8b1a1a;font-size:11px}' +
        '.gc-msg .txt{color:#2c1810;word-break:break-all;white-space:pre-wrap}' +
        '.gc-msg.mine .head,.gc-msg.mine .txt{text-align:right}' +
        '.gc-empty{color:#999;font-size:12px;text-align:center;padding:20px 0}' +
        '.gc-input{display:flex;gap:6px;padding:6px;border-top:1px solid #d4c5a9;flex-shrink:0}' +
        '.gc-input input[type=text]{flex:1;padding:6px 8px;border:1px solid #d4c5a9;border-radius:6px;font-size:12px;outline:none}' +
        '.gc-input .btn{padding:6px 12px;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;background:linear-gradient(135deg,#8b1a1a,#5c0e0e);color:#c9a96e}' +
        '.gc-friend{padding:6px 10px;border-bottom:1px solid #d4c5a9;flex-shrink:0}' +
        '.gc-friend select{width:100%;padding:5px;border:1px solid #d4c5a9;border-radius:6px;font-size:12px}' +
        '.gc-hint{color:#c9a96e;font-size:11px}' +
        '.gc-friend-name{cursor:pointer;color:#1565c0}' +
        '.global-chat.gc-hide{display:none}' +
        '.gc-open-btn{position:fixed;left:212px;bottom:12px;padding:8px 16px;background:linear-gradient(90deg,#1a1a2e,#2c2c44);color:#c9a96e;border:1px solid #c9a96e;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer;z-index:9998;display:none}' +
        '.gc-open-badge{position:absolute;top:-4px;right:-4px;background:#e53935;color:#fff;font-size:10px;border-radius:8px;padding:0 5px;display:none;min-width:16px;text-align:center}' +
        '.friend-badge{background:#e53935;color:#fff;font-size:10px;border-radius:8px;padding:0 5px;margin-left:4px;display:inline-block;vertical-align:top}' +
        '@media(max-width:768px){' +
        '.global-chat{left:8px;right:8px;width:auto;bottom:8px;height:300px;max-height:45vh}' +
        '.gc-open-btn{left:8px;bottom:8px}' +
        '.gc-input input[type=text]{font-size:16px}' +
        '}';
    document.head.appendChild(css);

    var el = document.createElement('div');
    el.id = 'globalChat';
    el.className = 'global-chat';
    el.innerHTML =
        '<div class="gc-head"><span class="gc-title">江湖聊天</span>' +
        '<span class="gc-tabs"><span class="gc-tab active" data-ch="1">世界<span class="gc-badge"></span></span>' +
        '<span class="gc-tab" data-ch="2">帮派<span class="gc-badge"></span></span>' +
        '<span class="gc-tab" data-ch="3">私聊<span class="gc-badge"></span></span></span>' +
        '<span class="gc-min" onclick="gcToggle()">_</span></div>' +
        '<div class="gc-friend" id="gcFriendRow" style="display:none"><span class="gc-hint" id="gcFriendHint">私聊输入 /好友名 内容</span></div>' +
        '<div class="gc-body" id="gcBody"><div class="gc-empty">连接中...</div></div>' +
        '<div class="gc-input"><input type="text" id="gcInput" maxlength="200" placeholder="输入消息"><span class="btn" onclick="gcSend()">发送</span></div>';
    document.body.appendChild(el);
    var openBtn = document.createElement('button');
    openBtn.id = 'gcOpen';
    openBtn.className = 'gc-open-btn';
    openBtn.textContent = '江湖聊天';
    openBtn.onclick = function() { gcToggle(); };
    var openBadge = document.createElement('span');
    openBadge.id = 'gcOpenBadge';
    openBadge.className = 'gc-open-badge';
    openBtn.appendChild(openBadge);
    document.body.appendChild(openBtn);

    document.getElementById('gcInput').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') { gcSend(); }
    });
    document.getElementById('gcBody').addEventListener('click', function(e) {
        var target = e.target;
        if (target && target.className === 'gc-friend-name' && target.getAttribute('data-id')) {
            window._gcPrivateFriend = target.getAttribute('data-id');
            window._gcPrivateName = target.textContent;
            var hint = document.getElementById('gcFriendHint');
            if (hint) { hint.textContent = '发送给：' + target.textContent + '（可输入 /好友名 内容 切换）'; }
            document.getElementById('gcInput').placeholder = '发送给 ' + target.textContent;
            gcSave();
        }
    });
    var tabs = document.querySelectorAll('#globalChat .gc-tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].addEventListener('click', function() {
            gcSwitch(parseInt(this.getAttribute('data-ch')) || 1);
        });
    }
    var saved = gcLoadState();
    if (saved) {
        window._gcChannel = saved.channel || 1;
        window._gcMsgs = saved.msgs || {1: [], 2: []};
        window._gcPrivate = saved.private || [];
        window._gcPrivateFriend = saved.privateFriend || '';
        window._gcUnread = saved.unread || {1: 0, 2: 0, 3: 0};
        if (saved.collapsed) {
            el.classList.add('gc-hide');
            document.getElementById('gcOpen').style.display = 'block';
        }
        for (var t = 0; t < tabs.length; t++) {
            tabs[t].classList.toggle('active', parseInt(tabs[t].getAttribute('data-ch')) === window._gcChannel);
        }
        document.getElementById('gcFriendRow').style.display = window._gcChannel === 3 ? 'block' : 'none';
    }
    if (!saved && window.innerWidth <= 768) {
        el.classList.add('gc-hide');
        document.getElementById('gcOpen').style.display = 'block';
    }
    gcRender();
    gcBadge(1);
    gcBadge(2);
    gcBadge(3);
    gcLoadHistory();
    gcConnect();
    gcLoadFriends();
    refreshUnread();
    setInterval(function() {
        if (window._gcWs && window._gcWs.readyState === 1) {
            window._gcWs.send(JSON.stringify({action: 'ping'}));
        }
    }, 25000);
    setInterval(refreshUnread, 15000);
    setInterval(function() {
        if (!window._gcWs || window._gcWs.readyState !== 1 || window._gcChannel === 3) {
            gcLoadHistory();
        }
    }, 5000);
}

function gcToggle() {
    var el = document.getElementById('globalChat');
    var openBtn = document.getElementById('gcOpen');
    if (!el) { return; }
    var hidden = el.classList.toggle('gc-hide');
    if (openBtn) { openBtn.style.display = hidden ? 'block' : 'none'; }
    if (!hidden) {
        gcLoadHistory();
        gcConnect();
    } else {
        var gcInput = document.getElementById('gcInput');
        if (gcInput) { gcInput.blur(); }
    }
    gcSave();
}

function gcSwitch(ch) {
    window._gcChannel = ch;
    var tabs = document.querySelectorAll('#globalChat .gc-tab');
    for (var i = 0; i < tabs.length; i++) {
        tabs[i].classList.toggle('active', parseInt(tabs[i].getAttribute('data-ch')) === ch);
    }
    document.getElementById('gcFriendRow').style.display = ch === 3 ? 'block' : 'none';
    if (ch === 3) { gcLoadFriends(); }
    gcBadge(ch);
    gcLoadHistory();
    gcSave();
}

function gcBadge(ch) {
    var tab = document.querySelector('#globalChat .gc-tab[data-ch="' + ch + '"] .gc-badge');
    if (!tab) { return; }
    var n = window._gcUnread[ch] || 0;
    tab.style.display = n > 0 ? 'inline-block' : 'none';
    tab.textContent = n > 99 ? '99+' : n;
}

function gcOpenBadge() {
    var badge = document.getElementById('gcOpenBadge');
    if (!badge) { return; }
    var n = window._gcUnread[3] || 0;
    badge.style.display = n > 0 ? 'inline-block' : 'none';
    badge.textContent = n > 99 ? '99+' : n;
}

function gcEscape(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function gcLoadFriends() {
    fetch('/game/jwt/api/v1/friend/list?player_id=' + window._gcPid, {headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}})
    .then(function(r) { return r.json(); })
    .then(function(d) {
        var friends = d.data && d.data.friends || [];
        window._gcFriends = {};
        for (var i = 0; i < friends.length; i++) {
            window._gcFriends[friends[i].name] = friends[i].player_id;
        }
    });
}

function gcLoadHistory() {
    var ch = window._gcChannel;
    var url = '/game/jwt/api/v1/chat/messages?channel=' + ch + '&player_id=' + window._gcPid;
    url += '&limit=20';
    fetch(url, {headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}})
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code !== 0) {
            document.getElementById('gcBody').innerHTML = '<div class="gc-empty">' + gcEscape(d.message || '加载失败') + '</div>';
            return;
        }
        var data = d.data || {};
        var list = data.messages || [];
        if (ch === 3) { window._gcPrivate = list; } else { window._gcMsgs[ch] = list; }
        window._gcUnread[ch] = 0;
        gcBadge(ch);
        gcRender();
        gcSave();
        gcMarkRead(ch, '');
    });
}

function gcRender() {
    var ch = window._gcChannel;
    var list = ch === 3 ? window._gcPrivate : (window._gcMsgs[ch] || []);
    var h = '';
    for (var i = 0; i < list.length; i++) {
        var m = list[i];
        var mine = m.sender_id === window._gcPid;
        var otherName = mine ? (m.receiver_name || '') : (m.sender_name || '');
        var otherId = mine ? (m.receiver_id || '') : (m.sender_id || '');
        var head = mine ? '我' : '<span class="gc-friend-name" data-id="' + otherId + '">' + gcEscape(otherName) + '</span>';
        if (mine && m.read) { head += ' 已读'; }
        h += '<div class="gc-msg' + (mine ? ' mine' : '') + '"><div class="head">' + head + ' ' + gcEscape(m.created_at || '') + '</div>' +
             '<div class="txt">' + gcEscape(m.content) + '</div></div>';
    }
    var box = document.getElementById('gcBody');
    box.innerHTML = h || '<div class="gc-empty">暂无消息</div>';
    box.scrollTop = box.scrollHeight;
}

function gcAddMsg(msg) {
    if (!msg || !msg.channel) { return; }
    var ch = msg.channel;
    if (ch === 3) {
        if (msg.sender_id !== window._gcPid && msg.receiver_id !== window._gcPid) { return; }
        window._gcPrivate.push(msg);
        if (window._gcChannel === 3) {
            gcRender();
            gcMarkRead(3, '');
        } else {
        window._gcUnread[3] = (window._gcUnread[3] || 0) + 1;
        gcBadge(3);
        gcOpenBadge();
        refreshUnread();
        }
        gcSave();
        return;
    }
    if (!window._gcMsgs[ch]) { window._gcMsgs[ch] = []; }
    window._gcMsgs[ch].push(msg);
    if (window._gcMsgs[ch].length > 100) { window._gcMsgs[ch].shift(); }
    if (window._gcChannel === ch) { gcRender(); }
    else {
        window._gcUnread[ch] = (window._gcUnread[ch] || 0) + 1;
        gcBadge(ch);
    }
    gcSave();
}

function gcLoadState() {
    try {
        var raw = sessionStorage.getItem('gcState');
        if (!raw) { return null; }
        var saved = JSON.parse(raw);
        return saved.pid === window._gcPid ? saved : null;
    } catch (e) { return null; }
}

function gcSave() {
    try {
        sessionStorage.setItem('gcState', JSON.stringify({
            pid: window._gcPid,
            channel: window._gcChannel,
            msgs: {
                1: (window._gcMsgs[1] || []).slice(-50),
                2: (window._gcMsgs[2] || []).slice(-50)
            },
            private: (window._gcPrivate || []).slice(-50),
            privateFriend: window._gcPrivateFriend,
            unread: window._gcUnread,
            collapsed: document.getElementById('globalChat').classList.contains('gc-hide')
        }));
    } catch (e) {}
}

function gcConnect() {
    if (window._gcWs && window._gcWs.readyState === 1) { return; }
    var proto = location.protocol === 'https:' ? 'wss://' : 'ws://';
    var token = encodeURIComponent(localStorage.getItem('token') || '');
    var url = proto + location.host + '/game/jwt/api/v1/ws/chat?token=' + token;
    var ws = new WebSocket(url);
    window._gcWs = ws;
    ws.onmessage = function(e) {
        try {
            var d = JSON.parse(e.data);
            if (d.type === 'chat') { gcAddMsg(d.data); }
            else if (d.type === 'pong') { return; }
            else if (d.type === 'error') { showFriendNotice(d.message || '发送失败'); }
            else if (d.type === 'friend_request') {
                refreshFriendBadge();
                showFriendNotice(d.name ? d.name + ' 申请加你为好友' : '收到新的好友申请');
                if (typeof window.onFriendRequest === 'function') { window.onFriendRequest(d); }
            }
            else if (d.type === 'friend_accepted') {
                updateFriendCount(1);
                showFriendNotice(d.name ? d.name + ' 已同意你的好友申请' : '好友申请已通过');
            }
        } catch (err) {}
    };
    ws.onopen = function() {
        window._gcRetry = 0;
    };
    ws.onclose = function() {
        var delay = Math.min(30000, 1000 * Math.pow(2, window._gcRetry || 0));
        window._gcRetry = (window._gcRetry || 0) + 1;
        setTimeout(gcConnect, delay);
    };
}

function gcSend() {
    var input = document.getElementById('gcInput');
    var content = input.value.trim();
    if (!content) { return; }
    var ch = window._gcChannel;
    if (ch === 3) {
        var parsed = parsePrivateTarget(content);
        if (!parsed) { return; }
        content = parsed.content;
    }
    var body = {channel: ch, content: content, receiver_id: parsed ? parsed.receiver_id : undefined, receiver_name: parsed ? parsed.receiver_name : undefined};
    if (window._gcWs && window._gcWs.readyState === 1) {
        window._gcWs.send(JSON.stringify({action: 'send', channel: ch, content: content, receiver_id: body.receiver_id, receiver_name: body.receiver_name}));
        gcResetInput(input, ch);
        input.blur();
    } else {
        fetch('/game/jwt/api/v1/chat/send?player_id=' + window._gcPid, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem('token')},
            body: JSON.stringify(body)
        })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.code === 0) { gcResetInput(input, ch); gcLoadHistory(); input.blur(); }
            else { alert(d.message || '发送失败'); }
        })
        .catch(function() { alert('网络异常'); });
    }
}

function parsePrivateTarget(content) {
    var match = content.match(/^\/([^\s]+)\s+(.+)$/);
    if (match) {
        var name = match[1];
        var friendId = window._gcFriends && window._gcFriends[name];
        window._gcPrivateName = name;
        if (friendId) { window._gcPrivateFriend = String(friendId); }
        var hint = document.getElementById('gcFriendHint');
        if (hint) { hint.textContent = '发送给：' + name + '（可输入 /好友名 内容 切换）'; }
        return {receiver_id: friendId || null, receiver_name: name, content: match[2]};
    }
    if (!window._gcPrivateFriend) {
        showFriendNotice('请输入 /好友名 内容');
        return null;
    }
    return {receiver_id: parseInt(window._gcPrivateFriend), receiver_name: window._gcPrivateName, content: content};
}

function gcFriendNameById(id) {
    var name = '';
    for (var key in window._gcFriends) {
        if (String(window._gcFriends[key]) === String(id)) { name = key; break; }
    }
    return name;
}

function gcResetInput(input, ch) {
    if (ch === 3) {
        var name = window._gcPrivateName || gcFriendNameById(window._gcPrivateFriend);
        input.value = name ? '/' + name + ' ' : '';
    } else {
        input.value = '';
    }
}

function gcMarkRead(ch, friendId) {
    fetch('/game/jwt/api/v1/chat/read?player_id=' + window._gcPid, {
        method: 'POST',
        headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + localStorage.getItem('token')},
        body: JSON.stringify({channel: ch, friend_id: friendId || null})
    })
    .then(function(r) { return r.json(); })
    .then(function() { refreshUnread(); });
}

function refreshUnread() {
    fetch('/game/jwt/api/v1/chat/unread?player_id=' + window._gcPid, {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code !== 0) { return; }
        var data = d.data || {};
        window._gcUnread = {
            1: data.world || 0,
            2: data.guild || 0,
            3: Math.max(window._gcUnread[3] || 0, data.private_total || 0)
        };
        gcBadge(1);
        gcBadge(2);
        gcBadge(3);
        gcOpenBadge();
    });
}

function friendNav() {
    return document.querySelector('.nav-item[href$="friend.html"]');
}

function getFriendCount() {
    var nav = friendNav();
    if (!nav || !nav.childNodes[0]) { return 0; }
    var m = (nav.childNodes[0].textContent || '').match(/\((\d+)\)/);
    return m ? parseInt(m[1]) : 0;
}

function setFriendCount(n) {
    var nav = friendNav();
    if (!nav || !nav.childNodes[0]) { return; }
    var text = nav.childNodes[0].textContent.trim();
    if (text.indexOf('(') >= 0) { text = text.substring(0, text.indexOf('(')).trim(); }
    if (!text) { text = '好友'; }
    nav.childNodes[0].textContent = text + ' (' + n + ')';
}

function updateFriendCount(delta) {
    setFriendCount(Math.max(0, getFriendCount() + delta));
}

function getFriendBadge() {
    var el = document.getElementById('friendBadge');
    return el ? (parseInt(el.textContent) || 0) : 0;
}

function setFriendBadge(n) {
    var nav = friendNav();
    if (!nav) { return; }
    var el = document.getElementById('friendBadge');
    if (!el) {
        el = document.createElement('span');
        el.id = 'friendBadge';
        el.className = 'friend-badge';
        nav.appendChild(el);
    }
    el.style.background = '#e53935';
    el.style.color = '#fff';
    el.style.fontSize = '10px';
    el.style.borderRadius = '8px';
    el.style.padding = '0 5px';
    el.style.marginLeft = '4px';
    el.style.display = n > 0 ? 'inline-block' : 'none';
    el.textContent = n > 99 ? '99+' : n;
}

function updateFriendBadge(delta) {
    setFriendBadge(Math.max(0, getFriendBadge() + delta));
}

function refreshFriendBadge() {
    var pid = parseInt(localStorage.getItem('player_id')) || 1;
    fetch('/game/jwt/api/v1/friend/requests?player_id=' + pid, {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        var count = d.code === 0 ? (d.data && d.data.requests || []).length : 0;
        if (typeof window._lastFriendRequestCount === 'number' && count > window._lastFriendRequestCount) {
            showFriendNotice('收到新的好友申请');
        }
        window._lastFriendRequestCount = count;
        setFriendBadge(count);
    });
}

function refreshFriendNav() {
    var nav = friendNav();
    if (!nav) { return; }
    var pid = parseInt(localStorage.getItem('player_id')) || 1;
    fetch('/game/jwt/api/v1/friend/list?player_id=' + pid, {
        headers: {'Authorization': 'Bearer ' + localStorage.getItem('token')}
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code !== 0) { return; }
        setFriendCount((d.data && d.data.friends || []).length);
    });
    refreshFriendBadge();
}

function initMobileNav() {
    var css = document.createElement('style');
    css.textContent =
        '.mobile-nav-btn{background:transparent;border:1px solid #c9a96e;color:#c9a96e;border-radius:4px;padding:4px 10px;font-size:16px;cursor:pointer;margin-right:10px;display:none}' +
        '.mobile-nav-mask{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:999;display:none}' +
        '@media(max-width:768px){' +
        '.mobile-nav-btn{display:inline-block}' +
        '.sidebar.mobile-open{display:flex !important;position:fixed;top:50px;left:0;bottom:0;width:200px;z-index:1000}' +
        '.mobile-nav-mask.show{display:block}' +
        '}';
    document.head.appendChild(css);
    var topbar = document.querySelector('.topbar');
    var sidebar = document.querySelector('.sidebar');
    if (!topbar || !sidebar || window.innerWidth > 768) { return; }
    var btn = document.createElement('button');
    btn.id = 'mobileNavBtn';
    btn.className = 'mobile-nav-btn';
    btn.textContent = '☰';
    btn.setAttribute('aria-label', '打开导航');
    topbar.insertBefore(btn, topbar.firstChild);
    var mask = document.createElement('div');
    mask.id = 'mobileNavMask';
    mask.className = 'mobile-nav-mask';
    document.body.appendChild(mask);
    function setOpen(open) {
        sidebar.classList.toggle('mobile-open', open);
        mask.classList.toggle('show', open);
    }
    btn.addEventListener('click', function() {
        setOpen(!sidebar.classList.contains('mobile-open'));
    });
    mask.addEventListener('click', function() { setOpen(false); });
    sidebar.addEventListener('click', function(e) {
        if (e.target && e.target.closest && e.target.closest('a')) { setOpen(false); }
    });
}

function checkSession() {
    var token = localStorage.getItem('token');
    if (!token) { return; }
    fetch('/game/jwt/api/v1/auth/check?token=' + encodeURIComponent(token))
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0 && d.data && d.data.valid === false) {
            localStorage.removeItem('token');
            localStorage.removeItem('user_id');
            localStorage.removeItem('player_id');
            sessionStorage.removeItem('gcState');
            window.location.href = '/game/jwt/';
        }
    })
    .catch(function() {});
}

document.addEventListener('DOMContentLoaded', initGlobalChat);
document.addEventListener('DOMContentLoaded', initMobileNav);
document.addEventListener('DOMContentLoaded', function() {
    checkSession();
    setInterval(checkSession, 60000);
});
document.addEventListener('DOMContentLoaded', function() {
    refreshFriendNav();
    setInterval(refreshFriendBadge, 15000);
});
