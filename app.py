from flask import Flask, render_template, request
from itertools import chain, combinations
import json
import random

app = Flask(__name__)

with open('products.json', 'r', encoding='utf-8') as f:
    foods = json.load(f)

combo_cache = {}

MAX_COMBOS = 1000
MIN_ITEMS = 3
MAX_ITEMS = 8

def all_combos(items, min_items=MIN_ITEMS, max_items=MAX_ITEMS):
    return chain.from_iterable(combinations(items, r) for r in range(min_items, max_items + 1))

def get_fast_combos(protein_target, heat_limit, sodium_limit, max_samples=1000, min_items=3, max_items=8):  
    key = (protein_target, heat_limit, sodium_limit)
    if key in combo_cache:
        return combo_cache[key]

    filtered_foods = [f for f in foods if (f.get('protein') or 0) > 0]
    valid_combos = []
    attempts = 0
    max_attempts = max_samples * 10

    while len(valid_combos) < max_samples and attempts < max_attempts:
        attempts += 1
        combo_size = random.randint(min_items, max_items)
        combo = tuple(random.sample(filtered_foods, combo_size))

        total_protein = sum(f.get('protein', 0) or 0 for f in combo)
        total_heat = sum(f.get('heat', 0) or 0 for f in combo)
        total_sodium = sum(f.get('sodium', 0) or 0 for f in combo)
        total_sugar = sum(f.get('sugar', 0) or 0 for f in combo)
        total_trans_fat = sum(f.get('trans_fat', 0) or 0 for f in combo)

        if (total_protein >= protein_target and 
            total_heat <= heat_limit and 
            total_trans_fat == 0 and
            total_sodium <= sodium_limit):
            
            valid_combos.append({
                'items': combo,
                'total_protein': int(total_protein),
                'total_heat': int(total_heat),
                'total_sodium': int(total_sodium),
                'total_sugar': int(total_sugar)
            })

    combo_cache[key] = valid_combos
    return valid_combos


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    protein_target = None
    heat_limit = None
    sodium_limit = None
    combos_count = 0

    if request.method == 'POST':
        try:
            protein_target = float(request.form['protein_target'])
            heat_limit = float(request.form['heat_limit'])
            sodium_limit = float(request.form['sodium_limit'])
        except Exception:
            protein_target, heat_limit, sodium_limit = None, None, None

        if protein_target is not None and heat_limit is not None and sodium_limit is not None:
            combos = get_fast_combos(protein_target, heat_limit, sodium_limit)
            combos_count = len(combos)
            if combos:
                result = random.choice(combos)

    elif request.args.get("retry") == "1":
        try:
            protein_target = float(request.args.get("protein_target"))
            heat_limit = float(request.args.get("heat_limit"))
            sodium_limit = float(request.args.get("sodium_limit"))
        except Exception:
            protein_target, heat_limit, sodium_limit = None, None, None

        if protein_target is not None and heat_limit is not None and sodium_limit is not None:
            combos = combo_cache.get((protein_target, heat_limit, sodium_limit), [])
            combos_count = len(combos)
            if combos:
                result = random.choice(combos)

    if result:
        items = result['items']
        total_nutrition = {
            'heat': int(sum(f.get('heat',0) or 0 for f in items)),
            'protein': int(sum(f.get('protein',0) or 0 for f in items)),
            'fat': int(sum(f.get('fat',0) or 0 for f in items)),
            'sat_fat': int(sum(f.get('sat_fat',0) or 0 for f in items)),
            'trans_fat': int(sum(f.get('trans_fat',0) or 0 for f in items)),
            'sodium': int(sum(f.get('sodium',0) or 0 for f in items)),
            'sugar': int(sum(f.get('sugar',0) or 0 for f in items)),
        }
    else:
        total_nutrition = None

    return render_template('index.html',
                        result=result,
                        protein_target=protein_target,
                        heat_limit=heat_limit,
                        sodium_limit=sodium_limit,
                        combos_count=combos_count,
                        total_nutrition=total_nutrition)


if __name__ == '__main__':
    app.run(debug=False, port=5001)
