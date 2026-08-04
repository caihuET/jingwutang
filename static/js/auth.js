const API_BASE = '/jwt/api/v1';

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.tab').forEach(function(tab) {
        tab.addEventListener('click', switchTab);
    });
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
});

function switchTab(e) {
    var tab = e.currentTarget;
    var target = tab.dataset.target;
    document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
    document.querySelectorAll('.tab-content').forEach(function(c) { c.classList.remove('active'); });
    tab.classList.add('active');
    document.getElementById(target).classList.add('active');
    hideError();
}

function showError(msg, isSuccess) {
    var el = document.getElementById('errorMsg');
    el.textContent = msg;
    el.style.color = isSuccess ? '#27ae60' : '#c0392b';
    el.classList.add('show');
}

function hideError() {
    var el = document.getElementById('errorMsg');
    el.textContent = '';
    el.classList.remove('show');
}

function showLoading() { document.getElementById('loadingOverlay').classList.add('show'); }
function hideLoading() { document.getElementById('loadingOverlay').classList.remove('show'); }

async function handleLogin(e) {
    e.preventDefault();
    hideError();
    var username = document.getElementById('loginUsername').value.trim();
    var password = document.getElementById('loginPassword').value;
    if (!username || !password) { showError('请输入用户名和密码'); return; }
    showLoading();
    try {
        var res = await fetch(API_BASE + '/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, password: password})
        });
        var data = await res.json();
        if (data.code === 0) {
            sessionStorage.removeItem('gcState');
            localStorage.removeItem('player_id');
            localStorage.setItem('token', data.data.token);
            localStorage.setItem('user_id', data.data.user_id);
            fetch(API_BASE + '/player/by_user?user_id=' + data.data.user_id, {headers: {'Authorization': 'Bearer ' + data.data.token}})
            .then(function(r) { return r.json(); })
            .then(function(pd) {
                if (pd.data && pd.data.player_id) {
                    localStorage.setItem('player_id', pd.data.player_id);
                    window.location.href = '/jwt/game.html';
                } else {
                    window.location.href = '/jwt/create.html';
                }
            })
            .catch(function() { showError('网络异常，请重试'); });
        } else {
            showError(data.message || '登录失败');
        }
    } catch (err) {
        showError('网络异常，请稍后重试');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    hideError();
    var username = document.getElementById('regUsername').value.trim();
    var password = document.getElementById('regPassword').value;
    var confirm = document.getElementById('regConfirm').value;
    if (!username || !password || !confirm) { showError('请填写所有字段'); return; }
    if (password !== confirm) { showError('两次输入的密码不一致'); return; }
    if (password.length < 4 || password.length > 12) { showError('密码长度需 4-12 位'); return; }
    showLoading();
    try {
        var res = await fetch(API_BASE + '/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: username, password: password})
        });
        var data = await res.json();
        if (data.code === 0) {
            hideError();
            document.querySelectorAll('.tab')[0].click();
            document.getElementById('loginUsername').value = username;
            document.getElementById('loginPassword').value = '';
            showError('注册成功，请登录', true);
        } else {
            showError(data.message || '注册失败');
        }
    } catch (err) {
        showError('网络异常，请稍后重试');
    } finally {
        hideLoading();
    }
}
