document.addEventListener('DOMContentLoaded', () => {
    const recommendBtn = document.getElementById('recommend-btn');
    const reRecommendBtn = document.getElementById('re-recommend-btn');
    const recommendationResults = document.getElementById('recommendation-results');

    const nutrientInputs = {
        calories: '熱量(大卡)',
        carbohydrates: '碳水化合物(公克)',
        protein: '蛋白質(公克)',
        fat: '脂肪(公克)',
        saturated_fat: '飽和脂肪(公克)',
        trans_fat: '反式脂肪(公克)',
        sodium: '鈉(毫克)',
        sugars: '糖(公克)'
    };

    const nutrientDisplayOrder = [
        '熱量(大卡)',
        '碳水化合物(公克)',
        '蛋白質(公克)',
        '脂肪(公克)',
        '飽和脂肪(公克)',
        '鈉(毫克)',
        '糖(公克)',
        '反式脂肪(公克)'
    ];

    const API_BASE_URL = '';

    recommendBtn.addEventListener('click', () => fetchRecommendations());
    reRecommendBtn.addEventListener('click', () => fetchRecommendations());

    async function fetchRecommendations() {
        const requirements = {};
        for (const key in nutrientInputs) {
            const inputElement = document.getElementById(key);
            const value = parseFloat(inputElement.value);

            if (!isNaN(value)) {
                requirements[nutrientInputs[key]] = value;
            }
        }

        recommendationResults.innerHTML = '<p class="placeholder-text">正在為您生成推薦餐點...</p>';
        reRecommendBtn.style.display = 'none';

        try {
            const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ requirements })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayRecommendations(data);
            reRecommendBtn.style.display = 'block';

        } catch (error) {
            console.error('Error fetching recommendations:', error);
            recommendationResults.innerHTML = '<p class="placeholder-text error">載入推薦餐點失敗，請稍後再試。</p>';
        }
    }

    function displayRecommendations(data) {
        recommendationResults.innerHTML = '';

        if (data.error) {
            recommendationResults.innerHTML = `<p class="placeholder-text error">${data.error}</p>`;
            return;
        }

        const mealNames = ['早餐', '午餐', '晚餐'];

        data.meals.forEach((meal, index) => {
            const mealCategoryDiv = document.createElement('div');
            mealCategoryDiv.classList.add('meal-category');
            mealCategoryDiv.innerHTML = `<h3>${mealNames[index]}</h3>`;

            const mealItemsList = document.createElement('ul');
            mealItemsList.classList.add('meal-items');

            meal.items.forEach(item => {
                const mealItemLi = document.createElement('li');
                mealItemLi.classList.add('meal-item');
                mealItemLi.textContent = item['品名'];

                const tooltip = document.createElement('div');
                tooltip.classList.add('tooltip');
                let tooltipContent = `品名: ${item['品名']}\n價格: ${item['價格']}\n`;
                nutrientDisplayOrder.forEach(nutrientName => {
                    if (item[nutrientName] !== undefined) {
                        tooltipContent += `${nutrientName}: ${item[nutrientName]}\n`;
                    }
                });
                tooltip.textContent = tooltipContent;
                mealItemLi.appendChild(tooltip);
                mealItemsList.appendChild(mealItemLi);
            });

            mealCategoryDiv.appendChild(mealItemsList);

            const mealNutritionSummary = document.createElement('div');
            mealNutritionSummary.classList.add('nutrition-summary');
            mealNutritionSummary.innerHTML = `<h4>${mealNames[index]}營養總計:</h4>`;
            nutrientDisplayOrder.forEach(nutrientName => {
                if (meal.nutrition_summary[nutrientName] !== undefined) {
                    const p = document.createElement('p');
                    p.textContent = `${nutrientName}: ${meal.nutrition_summary[nutrientName].toFixed(1)}`;
                    if (meal.exceedance_flags[nutrientName]) {
                        p.classList.add('exceeded');
                    }
                    mealNutritionSummary.appendChild(p);
                }
            });
            mealCategoryDiv.appendChild(mealNutritionSummary);

            recommendationResults.appendChild(mealCategoryDiv);
        });

        const totalNutritionDiv = document.createElement('div');
        totalNutritionDiv.classList.add('total-nutrition-summary');
        totalNutritionDiv.innerHTML = `<h3>一日總營養總計:</h3>`;
        const totalNutritionGrid = document.createElement('div');
        totalNutritionGrid.classList.add('nutrition-summary-grid');

        nutrientDisplayOrder.forEach(nutrientName => {
            if (data.total_nutrition[nutrientName] !== undefined) {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('nutrition-summary-item');
                const p = document.createElement('p');
                p.textContent = `${nutrientName}: ${data.total_nutrition[nutrientName].toFixed(1)}`;
                if (data.total_exceedance_flags[nutrientName]) {
                    p.classList.add('exceeded');
                }
                itemDiv.appendChild(p);
                totalNutritionGrid.appendChild(itemDiv);
            }
        });
        totalNutritionDiv.appendChild(totalNutritionGrid);
        recommendationResults.appendChild(totalNutritionDiv);
    }
});