document.addEventListener('DOMContentLoaded', () => {
    const detail = document.getElementById('food-detail');
    const totalHtml = detail.innerHTML;

    function showDetail(el) {
        if (!el) {
            detail.innerHTML = totalHtml;
            return;
        }
        const name = el.dataset.name || '無名稱';
        const heat = el.dataset.heat || '未知';
        const protein = el.dataset.protein || '未知';
        const fat = el.dataset.fat || '未知';
        const sodium = el.dataset.sodium || '未知';
        const sugar = el.dataset.sugar || '未知';
        const satFat = el.dataset.sat_fat || '未知';
        const transFat = el.dataset.trans_fat || '未知';

        detail.innerHTML = `
            <h3>${name}</h3>
            <ul>
                <li>熱量: ${heat} kcal</li>
                <li>蛋白質: ${protein} g</li>
                <li>脂肪: ${fat} g (飽和脂肪: ${satFat} g, 反式脂肪: ${transFat} g)</li>
                <li>鈉含量: ${sodium} mg</li>
                <li>糖: ${sugar} g</li>
            </ul>
        `;
    }

    document.querySelectorAll('.food-card').forEach(card => {
        card.addEventListener('mouseenter', () => showDetail(card));
        card.addEventListener('focus', () => showDetail(card));
        card.addEventListener('mouseleave', () => showDetail(null));
        card.addEventListener('blur', () => showDetail(null));
    });
});
