import os
import json
from flask import Flask, render_template, request

app = Flask(__name__)


# формуємо абсолютні шляхи до JSON у папці data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cocktails_file = os.path.join(BASE_DIR, "data", "cocktails.json")
glass_file = os.path.join(BASE_DIR, "data", "glass.json")
ingredients_file = os.path.join(BASE_DIR, "data", "ingredients.json")
categories_file = os.path.join(BASE_DIR, "data", "categories.json")

# завантаження JSON коктейлів
with open(cocktails_file, "r", encoding="utf-8") as f:
    cocktail_list = json.load(f)

# поле image для зручності у шаблонах
for c in cocktail_list:
    if "image_webp" in c and c["image_webp"]:
        c["image"] = c["image_webp"]
    elif "image_jpg" in c and c["image_jpg"]:
        c["image"] = c["image_jpg"]
    else:
        c["image"] = "placeholder.webp"

# завантаження категорій
with open(categories_file, "r", encoding="utf-8") as f:
    category_list = json.load(f)

for cat in category_list:
    if not cat.get("image"):
        cat["image"] = "placeholder.webp"

# завантаження інгредієнтів
with open(ingredients_file, "r", encoding="utf-8") as f:
    ingredients_list = json.load(f)

for ing in ingredients_list:
    if not ing.get("image"):
        ing["image"] = "placeholder.webp"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/cocktails")
def cocktails_page():
    category = request.args.get("category")
    strength = request.args.get("strength")
    glass = request.args.get("glass")
    ingredient = request.args.get("ingredients")
    page = request.args.get("page", 1, type=int)   # номер сторінки
    per_page = 20                                  # кількість коктейлів на сторінку

    results = cocktail_list

    if category:
        results = [c for c in results if c["category"].lower() == category.lower()]
    if strength:
        results = [c for c in results if c["strength"].lower() == strength.lower()]
    if glass:
        results = [c for c in results if glass.lower() in c["glass"].lower()]
    if ingredient:
        ingredient = ingredient.lower()
        results = [
            c for c in results
            if any(ingredient in ing.lower() for ing in c["ingredients"])
        ]

# пагінація
    total = len(results)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    results_page = results[start:end]

    return render_template(
        "cocktails.html",
        cocktails=results_page,
        page=page,
        total_pages=total_pages
    )

    



@app.route("/cocktail/<name>")
def cocktail_detail(name):
    cocktail = next((c for c in cocktail_list if c["name"].lower() == name.lower()), None)
    return render_template("cocktail.html", cocktail=cocktail)


@app.route("/glass")
def glass_library():
    with open(glass_file, "r", encoding="utf-8") as f:
        glass_list = json.load(f)
    return render_template("glass.html", glass=glass_list)


@app.route("/glass/<name>")
def glass_detail(name):
    related_cocktails = [c for c in cocktail_list if c["glass"].lower() == name.lower()]

    with open(glass_file, "r", encoding="utf-8") as f:
        glass_list = json.load(f)
    glass_item = next((g for g in glass_list if g["name"].lower() == name.lower()), None)

    return render_template("glass_detail.html", glass=glass_item, cocktails=related_cocktails)


@app.route("/ingredients")
def ingredients_types():
    types = sorted(set(item["type"] for item in ingredients_list if item.get("type")))
    return render_template("ingredients_types.html", types=types)


@app.route("/ingredients/<type_name>")
def ingredients_by_type(type_name):
    filtered = [item for item in ingredients_list if item["type"].lower() == type_name.lower()]
    return render_template("ingredients_list.html", type_name=type_name, ingredients=filtered)


@app.route("/ingredient/<name>")
def ingredient_detail(name):
    ingredient = next((item for item in ingredients_list if item["name"].lower() == name.lower()), None)
    if not ingredient:
        return "Інгредієнт не знайдено", 404

    related_cocktails = [c for c in cocktail_list if any(name.lower() in ing.lower() for ing in c["ingredients"])]

    return render_template("ingredient_detail.html", ingredient=ingredient, cocktails=related_cocktails)


@app.route("/search/event", methods=["GET", "POST"])
def search_event():
    with open(categories_file, "r", encoding="utf-8") as f:
        category_list = json.load(f)

    results = []
    if request.method == "POST":
        query = request.form.get("event", "").lower()
        results = [c for c in cocktail_list if query in c["category"].lower()]
        return render_template("search_event.html", results=results, selected=query, categories=category_list)

    return render_template("search_event.html", categories=category_list)


@app.route("/category/<name>")
def category_detail(name):
    results = [c for c in cocktail_list if c["category"].lower() == name.lower()]
    return render_template("category_detail.html", category=name, cocktails=results)


@app.route("/search/glass", methods=["GET", "POST"])
def search_glass():
    results = []
    if request.method == "POST":
        query = request.form.get("glass", "").lower()
        results = [c for c in cocktail_list if query in c["glass"].lower()]
    return render_template("search_glass.html", results=results)


@app.route("/search/ingredients")
def search_ingredients():
    types = sorted(set(item["type"] for item in ingredients_list if item.get("type")))
    return render_template("search_ingredients.html", types=types)


if __name__ == "__main__":
    app.run(debug=True)