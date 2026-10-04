// 健身热量记录控制推荐系统 —— 前端交互脚本

function postJSON(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    }).then(r => r.json());
}

function delJSON(url) {
    return fetch(url, { method: 'DELETE' }).then(r => r.json());
}

// 刷新当前页面
function reload() { window.location.reload(); }

// ---------------------------------------------------------------
// 饮食记录
// ---------------------------------------------------------------
function setupDiet() {
    const searchInput = document.getElementById('food-search');
    const list = document.getElementById('food-list');
    if (!searchInput || !list) return;

    // 搜索过滤
    searchInput.addEventListener('input', () => {
        const kw = searchInput.value.trim();
        document.querySelectorAll('#food-list .food-item').forEach(li => {
            const name = li.dataset.name;
            li.style.display = name.includes(kw) ? '' : 'none';
        });
    });

    // 添加食物
    list.addEventListener('click', (e) => {
        const btn = e.target.closest('.add-food-btn');
        if (!btn) return;
        const li = btn.closest('.food-item');
        const amount = parseFloat(li.querySelector('.amount-input').value);
        if (!amount || amount <= 0) { alert('请输入正确的克数'); return; }
        postJSON('/api/diet', { food_id: parseInt(li.dataset.id), amount_g: amount })
            .then(res => {
                if (res.error) { alert(res.error); return; }
                reload();
            });
    });

    // 删除记录
    document.getElementById('diet-records')?.addEventListener('click', (e) => {
        const btn = e.target.closest('.del-diet-btn');
        if (!btn) return;
        const id = btn.closest('.record-item').dataset.id;
        if (!confirm('确认删除这条饮食记录吗？')) return;
        delJSON('/api/diet/' + id).then(() => reload());
    });
}

// ---------------------------------------------------------------
// 运动记录
// ---------------------------------------------------------------
function setupExercise() {
    const searchInput = document.getElementById('exercise-search');
    const list = document.getElementById('exercise-list');
    if (!searchInput || !list) return;

    searchInput.addEventListener('input', () => {
        const kw = searchInput.value.trim();
        document.querySelectorAll('#exercise-list .food-item').forEach(li => {
            li.style.display = li.dataset.name.includes(kw) ? '' : 'none';
        });
    });

    list.addEventListener('click', (e) => {
        const btn = e.target.closest('.add-exercise-btn');
        if (!btn) return;
        const li = btn.closest('.food-item');
        const minutes = parseFloat(li.querySelector('.amount-input').value);
        if (!minutes || minutes <= 0) { alert('请输入正确的时长'); return; }
        postJSON('/api/exercise', { exercise_id: parseInt(li.dataset.id), minutes })
            .then(res => {
                if (res.error) { alert(res.error); return; }
                reload();
            });
    });

    document.getElementById('exercise-records')?.addEventListener('click', (e) => {
        const btn = e.target.closest('.del-exercise-btn');
        if (!btn) return;
        const id = btn.closest('.record-item').dataset.id;
        if (!confirm('确认删除这条运动记录吗？')) return;
        delJSON('/api/exercise/' + id).then(() => reload());
    });
}

document.addEventListener('DOMContentLoaded', () => {
    setupDiet();
    setupExercise();
});
