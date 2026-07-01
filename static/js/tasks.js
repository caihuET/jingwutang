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
        else { showToast(data.message || '加载失败', 'error'); }
    })
    .catch(function() { showLoading(false); showToast('网络异常', 'error'); });
}

function renderTasks(tasks) {
    if (tasks.length === 0) {
        document.getElementById('taskList').innerHTML = '<div class="text-muted">暂无任务</div>';
        return;
    }
    var html = '';
    for (var i = 0; i < tasks.length; i++) {
        var t = tasks[i];
        var pct = t.target > 0 ? Math.round(t.progress / t.target * 100) : 0;
        var statusText = {0:'进行中',1:'可领取',2:'已完成'};
        var statusCls = {0:'locked',1:'active',2:'done'};
        html += '<div class="card">';
        html += '<div class="flex flex-center" style="justify-content:space-between">';
        html += '<div><div class="card-title" style="margin:0">' + t.name + '</div>';
        html += '<p style="font-size:12px;color:#6b5b4e;margin:4px 0">' + (t.description || '') + '</p></div>';
        html += '<span class="status-badge ' + (statusCls[t.status]||'locked') + '">' + (statusText[t.status]||'未知') + '</span>';
        html += '</div>';
        html += '<div class="progress-bar" style="margin:8px 0"><div class="fill" style="width:' + pct + '%"></div></div>';
        html += '<div class="flex flex-center" style="justify-content:space-between">';
        html += '<span class="text-muted">进度：' + t.progress + '/' + t.target + '</span>';
        html += '<span class="text-muted">经验+' + (t.rewards&&t.rewards.exp||0) + ' 金币+' + (t.rewards&&t.rewards.gold||0) + '</span>';
        if (t.status === 1) { html += '<button class="btn btn-sm btn-success" onclick="claimTask(' + t.id + ',' + t.task_id + ')">领取奖励</button>'; }
        html += '</div></div>';
    }
    document.getElementById('taskList').innerHTML = html;
}

function claimTask(id, taskId) {
    showToast('领取中...', 'info');
    fetch(API_BASE + '/task/claim', {
        method:'POST', headers:{'Content-Type':'application/json','Authorization':'Bearer '+localStorage.getItem('token')},
        body: JSON.stringify({task_id: taskId})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.code === 0) {
            showToast('领取成功！经验+' + d.data.exp + ' 金币+' + d.data.gold, 'success');
            loadTasks();
        } else {
            showToast(d.message || '领取失败', 'error');
        }
    })
    .catch(function() { showToast('网络异常', 'error'); });
}
