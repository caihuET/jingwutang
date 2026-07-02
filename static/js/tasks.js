var API_BASE = '/game/jwt/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    if (!checkAuth()) return;
    loadTasks();
    document.getElementById('taskTypeFilter').addEventListener('change', loadTasks);
});

function loadTasks() {
    showLoading(true);
    var taskType = document.getElementById('taskTypeFilter').value;
    var url = API_BASE + '/task/list?player_id=1';
    if (taskType) url += '&task_type=' + taskType;
    fetch(url, {headers: {'Authorization':'Bearer '+localStorage.getItem('token')}})
    .then(function(r) { return r.json(); })
    .then(function(data) {
        showLoading(false);
        if (data.code === 0) { renderTasks(data.data || []); }
        else { showToast(data.message || '鍔犺浇澶辫触', 'error'); }
    })
    .catch(function() { showLoading(false); showToast('缃戠粶寮傚父', 'error'); });
}

function renderTasks(tasks) {
    if (tasks.length === 0) {
        document.getElementById('taskList').innerHTML = '<div class="text-muted">鏆傛棤浠诲姟</div>';
        return;
    }
    var html = '';
    for (var i = 0; i < tasks.length; i++) {
        var t = tasks[i];
        var pct = t.target > 0 ? Math.round(t.progress / t.target * 100) : 0;
        var statusText = {'-1':'寰呴鍙?,'0':'杩涜涓?,'1':'鍙鍙?,'2':'宸插畬鎴?};
        var statusCls = {0:'locked',1:'active',2:'done'};
        html += '<div class="card">';
        html += '<div class="flex flex-center" style="justify-content:space-between">';
        html += '<div><div class="card-title" style="margin:0">' + t.name + '</div>';
        html += '<p style="font-size:12px;color:#6b5b4e;margin:4px 0">' + (t.description || '') + '</p></div>';
        html += '<span class="status-badge ' + (statusCls[t.status]||'locked') + '">' + (statusText[t.status]||'鏈煡') + '</span>';
        html += '</div>';
        html += '<div class="progress-bar" style="margin:8px 0"><div class="fill" style="width:' + pct + '%"></div></div>';
        html += '<div class="flex flex-center" style="justify-content:space-between">';
        html += '<span class="text-muted">杩涘害锛? + t.progress + '/' + t.target + '</span>';
        html += '<span class="text-muted">缁忛獙+' + (t.rewards&&t.rewards.exp||0) + ' 閲戝竵+' + (t.rewards&&t.rewards.gold||0) + '</span>';
        if (t.status === -1) { html += '<button class="btn btn-sm btn-p" style="padding:3px 10px;font-size:11px;cursor:pointer;background:linear-gradient(135deg,#8b1a1a,#5c0e0e);color:#c9a96e;border:none;border-radius:4px" onclick="acceptTask(null,' + t.task_id + ')">棰嗗彇浠诲姟</button>'; } if (t.status === 1) { html += '<button class="btn btn-sm btn-success" onclick="claimTask(' + t.id + ',' + t.task_id + ')">棰嗗彇濂栧姳</button>'; }
        html += '</div></div>';
    }
    document.getElementById('taskList').innerHTML = html;
}

function acceptTask(id,taskId){showToast('棰嗗彇涓?..','info');fetch('/game/jwt/api/v1/task/accept',{method:'POST',headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},body:JSON.stringify({task_id:taskId})}).then(function(r){return r.json()}).then(function(d){if(d.code===0){showToast('棰嗗彇鎴愬姛','success');loadTasks();}else{showToast(d.message||'棰嗗彇澶辫触','error');}}).catch(function(){showToast('缃戠粶寮傚父','error');});}function claimTask(id, taskId) {
    showToast('棰嗗彇涓?..', 'info');
    fetch(API_BASE + '/task/claim', {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({task_id: taskId})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) {
            showToast('棰嗗彇鎴愬姛锛佺粡楠?' + d.data.exp + ' 閲戝竵+' + d.data.gold, 'success');
            loadTasks();
        } else {
            showToast(d.message || '棰嗗彇澶辫触', 'error');
        }
    })
    .catch(function() { showToast('缃戠粶寮傚父', 'error'); });
}


