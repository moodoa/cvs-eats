from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
import pandas as pd
import random
import os
import json

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), 'products.json')
try:
    with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    products_df = pd.DataFrame(products_data)
    products_df = products_df.rename(columns={
        'name': '品名',
        'heat': '熱量(大卡)',
        'carbs': '碳水化合物(公克)',
        'protein': '蛋白質(公克)',
        'fat': '脂肪(公克)',
        'sat_fat': '飽和脂肪(公克)',
        'trans_fat': '反式脂肪(公克)',
        'sodium': '鈉(毫克)',
        'sugar': '糖(公克)'
    })
    numeric_cols = [
        '熱量(大卡)', '蛋白質(公克)', '脂肪(公克)', '飽和脂肪(公克)',
        '反式脂肪(公克)', '碳水化合物(公克)', '糖(公克)', '鈉(毫克)'
    ]
    for col in numeric_cols:
        products_df[col] = pd.to_numeric(products_df[col], errors='coerce').fillna(0)

except FileNotFoundError:
    print(f"Error: {PRODUCTS_FILE} not found. Please ensure products.json is generated.")
    products_df = pd.DataFrame()
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {PRODUCTS_FILE}. Check file format.")
    products_df = pd.DataFrame()

DAILY_ALLOWANCES = {
    '熱量(大卡)': 2000,
    '碳水化合物(公克)': 300,
    '蛋白質(公克)': 60,
    '脂肪(公克)': 65,
    '飽和脂肪(公克)': 20,
    '反式脂肪(公克)': 2.2,
    '鈉(毫克)': 2400,
    '糖(公克)': 50
}

TOLERANCE_PERCENTAGE = 0.10

RED_FLAG_NUTRIENTS = ['飽和脂肪(公克)', '反式脂肪(公克)', '糖(公克)', '鈉(毫克)']

def calculate_nutrition(meal_items):
    total_nutrition = {
        '熱量(大卡)': 0.0,
        '碳水化合物(公克)': 0.0,
        '蛋白質(公克)': 0.0,
        '脂肪(公克)': 0.0,
        '飽和脂肪(公克)': 0.0,
        '反式脂肪(公克)': 0.0,
        '鈉(毫克)': 0.0,
        '糖(公克)': 0.0
    }
    for item in meal_items:
        for key in total_nutrition.keys():
            total_nutrition[key] += item.get(key, 0.0)
    return total_nutrition

def check_exceedance(nutrition_data, user_requirements):
    exceedance_flags = {}
    for key, value in nutrition_data.items():
        user_target = user_requirements.get(key)
        
        if key in RED_FLAG_NUTRIENTS:
            exceedance_flags[key] = value > DAILY_ALLOWANCES.get(key, float('inf'))
        elif user_target is not None:
            if key == '蛋白質(公克)':
                lower_bound = user_target * (1 - TOLERANCE_PERCENTAGE)
                exceedance_flags[key] = value < lower_bound
            else:
                lower_bound = user_target * (1 - TOLERANCE_PERCENTAGE)
                upper_bound = user_target * (1 + TOLERANCE_PERCENTAGE)
                exceedance_flags[key] = not (lower_bound <= value <= upper_bound)
        else:
            exceedance_flags[key] = False
    return exceedance_flags

def get_recommendations(user_requirements, num_meals=3, min_items_per_meal=1, max_items_per_meal=4):
    if products_df.empty:
        return {"error": "Product data not loaded."}

    all_recommendations = []
    all_products_list = products_df.to_dict(orient='records')

    for _ in range(num_meals):
        meal_items = []
        current_meal_nutrition = {key: 0.0 for key in DAILY_ALLOWANCES.keys()}
        selected_item_names_in_meal = set()
        
        best_meal_for_this_slot = []
        best_meal_nutrition_for_this_slot = {key: 0.0 for key in DAILY_ALLOWANCES.keys()}
        best_meal_score = -float('inf')

        num_combination_attempts = 10000

        found_strictly_valid_meal = False

        for _attempt in range(num_combination_attempts):
            temp_meal_items = []
            temp_meal_nutrition = {key: 0.0 for key in DAILY_ALLOWANCES.keys()}
            temp_selected_item_names = set()

            shuffled_products = list(all_products_list)
            random.shuffle(shuffled_products)

            for product in shuffled_products:
                if product['品名'] in temp_selected_item_names:
                    continue

                would_violate_strict_req = False
                hypothetical_nutrition_after_add = temp_meal_nutrition.copy()
                for key in hypothetical_nutrition_after_add.keys():
                    hypothetical_nutrition_after_add[key] += product.get(key, 0.0)

                for req_key, user_target in user_requirements.items():
                    if user_target is not None and req_key in hypothetical_nutrition_after_add:
                        current_val = hypothetical_nutrition_after_add[req_key]

                        if req_key == '蛋白質(公克)':
                            lower_bound = user_target * (1 - TOLERANCE_PERCENTAGE)
                            if current_val < lower_bound:
                                would_violate_strict_req = True
                                break
                        else:
                            lower_bound = user_target * (1 - TOLERANCE_PERCENTAGE)
                            upper_bound = user_target * (1 + TOLERANCE_PERCENTAGE)
                            if not (lower_bound <= current_val <= upper_bound):
                                would_violate_strict_req = True
                                break
                
                if would_violate_strict_req:
                    continue

                temp_meal_items.append(product)
                temp_selected_item_names.add(product['品名'])
                for key in temp_meal_nutrition.keys():
                    temp_meal_nutrition[key] += product.get(key, 0.0)
                
                if len(temp_meal_items) >= max_items_per_meal:
                    break
            
            current_meal_score = 0.0
            is_meal_strictly_valid = True

            for req_key, user_target in user_requirements.items():
                if user_target is not None and req_key in temp_meal_nutrition:
                    current_val = temp_meal_nutrition[req_key]
                    if req_key == '蛋白質(公克)':
                        lower_bound = user_target * (1 - TOLERANCE_PERCENTAGE)
                        if current_val < lower_bound:
                            is_meal_strictly_valid = False
                            break
                        current_meal_score += min(current_val, user_target)
                    else:
                        lower_bound = user_target * (1 - TOLERANCE_PERCENTAGE)
                        upper_bound = user_target * (1 + TOLERANCE_PERCENTAGE)
                        if not (lower_bound <= current_val <= upper_bound):
                            is_meal_strictly_valid = False
                            break
                        current_meal_score += 10
                
            if not is_meal_strictly_valid:
                continue

            for nutrient_key in RED_FLAG_NUTRIENTS:
                if nutrient_key not in user_requirements:
                    current_val = temp_meal_nutrition.get(nutrient_key, 0.0)
                    if current_val > DAILY_ALLOWANCES.get(nutrient_key, float('inf')):
                        current_meal_score -= (current_val - DAILY_ALLOWANCES[nutrient_key]) * 2.0

            current_meal_score += len(temp_meal_items) * 0.1

            current_meal_score += random.uniform(-0.00001, 0.00001)

            if current_meal_score > best_meal_score:
                best_meal_score = current_meal_score
                best_meal_for_this_slot = temp_meal_items
                best_meal_nutrition_for_this_slot = temp_meal_nutrition
                found_strictly_valid_meal = True
        
        if found_strictly_valid_meal:
            meal_items = best_meal_for_this_slot
            current_meal_nutrition = best_meal_nutrition_for_this_slot
        else:
            print(f"Warning: Could not find a meal strictly satisfying all user requirements after {num_combination_attempts} attempts. Falling back to random selection.")
            meal_items = []
            current_meal_nutrition = {key: 0.0 for key in DAILY_ALLOWANCES.keys()}
            selected_item_names_in_meal = set()
            fallback_candidates = list(all_products_list)
            random.shuffle(fallback_candidates)

            for _ in range(random.randint(min_items_per_meal, max_items_per_meal)):
                if not fallback_candidates:
                    break
                chosen_item = fallback_candidates.pop(0)
                if chosen_item['品名'] not in selected_item_names_in_meal:
                    meal_items.append(chosen_item)
                    selected_item_names_in_meal.add(chosen_item['品名'])
                    for key in current_meal_nutrition.keys():
                        current_meal_nutrition[key] += chosen_item.get(key, 0.0)

        all_recommendations.append({
            "items": meal_items,
            "nutrition_summary": current_meal_nutrition,
            "exceedance_flags": check_exceedance(current_meal_nutrition, user_requirements)
        })

    total_nutrition_all_meals = {k: 0.0 for k in DAILY_ALLOWANCES.keys()}
    for meal in all_recommendations:
        for key, value in meal['nutrition_summary'].items():
            total_nutrition_all_meals[key] += value

    total_exceedance_flags = check_exceedance(total_nutrition_all_meals, user_requirements)

    return {
        "meals": all_recommendations,
        "total_nutrition": total_nutrition_all_meals,
        "total_exceedance_flags": total_exceedance_flags
    }

@app.route('/api/recommendations', methods=['POST'])
def recommend_meals():
    user_requirements = request.json.get('requirements', {})
    recommendations = get_recommendations(user_requirements)
    return jsonify(recommendations)

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if ".." in path or path.startswith('/'):
        abort(404)
    return send_from_directory(FRONTEND_DIR, path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)