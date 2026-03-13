import pandas as pd
import gurobipy as gp
from gurobipy import GRB


def load_data(file_path="meal_deal_data.xlsx"):
    df = pd.read_excel(file_path, sheet_name="Sheet1").copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("/", "_", regex=False)
    )

    df = df.rename(columns={
        "Individual_Price": "price",
        "Individual Price": "price",
        "EnergyCalories": "calories",
        "Energy(Calories)": "calories",
        "Fat_g": "fat",
        "Fat (g)": "fat",
        "Saturates_Fat_g": "sat_fat",
        "Saturates Fat (g)": "sat_fat",
        "Carbohydrates_g": "carbs",
        "Carbohydrates (g) ": "carbs",
        "Sugars_g": "sugar",
        "Sugars (g)": "sugar",
        "Fibre_g": "fibre",
        "Fibre (g)": "fibre",
        "Protein_g": "protein",
        "Protein (g)": "protein",
        "Salt_g": "salt",
        "Salt (g)": "salt",
        "Prime5.5GBP": "is_prime",
        "Prime(5.5GBP)": "is_prime",
        "Category": "category",
        "Item": "item",
        "Vegetarian": "vegetarian",
        "Vegan": "vegan",
        "Dairy": "dairy",
        "Gluten": "gluten",
        "Porks": "pork",
        "Beef": "beef",
        "Chicken": "chicken",
        "Fish": "fish",
        "Sweet": "sweet",
        "Salty": "salty",
        "Wrap": "wrap",
        "Sandwich": "sandwich",
        "Sushi": "sushi",
        "Bowl": "bowl",
        "Western": "western",
        "Asian": "asian",
        "Mediterranean": "mediterranean",
        "Indian": "indian",
        "Caribbean": "caribbean",
        "Caffeine": "caffeine",
    })

    df["category"] = df["category"].astype(str).str.strip().str.title()

    numeric_cols = [
        "price", "calories", "fat", "sat_fat", "carbs",
        "sugar", "fibre", "protein", "salt"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    binary_cols = [
        "is_prime", "vegetarian", "vegan", "dairy", "gluten",
        "pork", "beef", "chicken", "fish",
        "sweet", "salty",
        "wrap", "sandwich", "sushi", "bowl",
        "western", "asian", "mediterranean", "indian", "caribbean",
        "caffeine"
    ]
    for col in binary_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    mains = df[df["category"] == "Main"].reset_index(drop=True).copy()
    snacks = df[df["category"] == "Snack"].reset_index(drop=True).copy()
    drinks = df[df["category"] == "Drink"].reset_index(drop=True).copy()

    return mains, snacks, drinks


def solve_meal_deal(mains, snacks, drinks, params):
    if params is None:
        params = {}
        
    model = gp.Model("tesco_meal_deal")
    model.setParam("OutputFlag", 0)

    mains = mains.copy()
    snacks = snacks.copy()
    drinks = drinks.copy()

    M = mains.index.tolist()
    S = snacks.index.tolist()
    D = drinks.index.tolist()

    mains["other_protein"] = (
        mains[["pork", "beef", "chicken", "fish"]].sum(axis=1) == 0
    ).astype(int)

    snacks["sweet_and_salty"] = (
        (snacks["sweet"] == 1) & (snacks["salty"] == 1)
    ).astype(int)

    x = model.addVars(M, vtype=GRB.BINARY, name="main")
    y = model.addVars(S, vtype=GRB.BINARY, name="snack")
    z = model.addVars(D, vtype=GRB.BINARY, name="drink")

    model.addConstr(gp.quicksum(x[i] for i in M) == 1, name="one_main")
    model.addConstr(gp.quicksum(y[j] for j in S) == 1, name="one_snack")
    model.addConstr(gp.quicksum(z[k] for k in D) == 1, name="one_drink")

    total_calories = (
        gp.quicksum(mains.loc[i, "calories"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "calories"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "calories"] * z[k] for k in D)
    )

    total_protein = (
        gp.quicksum(mains.loc[i, "protein"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "protein"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "protein"] * z[k] for k in D)
    )

    total_sugar = (
        gp.quicksum(mains.loc[i, "sugar"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "sugar"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "sugar"] * z[k] for k in D)
    )

    total_fat = (
        gp.quicksum(mains.loc[i, "fat"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "fat"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "fat"] * z[k] for k in D)
    )

    total_carbs = (
        gp.quicksum(mains.loc[i, "carbs"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "carbs"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "carbs"] * z[k] for k in D)
    )

    total_salt = (
        gp.quicksum(mains.loc[i, "salt"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "salt"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "salt"] * z[k] for k in D)
    )

    total_individual_price = (
        gp.quicksum(mains.loc[i, "price"] * x[i] for i in M) +
        gp.quicksum(snacks.loc[j, "price"] * y[j] for j in S) +
        gp.quicksum(drinks.loc[k, "price"] * z[k] for k in D)
    )

    selected_main_is_prime = gp.quicksum(mains.loc[i, "is_prime"] * x[i] for i in M)

    regular_price = params.get("regular_price", 3.85)
    prime_price = params.get("prime_price", 5.50)

    meal_deal_price = regular_price + (prime_price - regular_price) * selected_main_is_prime
    total_savings = total_individual_price - meal_deal_price

    # dietary constraints
    if params.get("vegetarian_only", False):
        model.addConstr(gp.quicksum((1 - mains.loc[i, "vegetarian"]) * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum((1 - snacks.loc[j, "vegetarian"]) * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum((1 - drinks.loc[k, "vegetarian"]) * z[k] for k in D) == 0)

    if params.get("vegan_only", False):
        model.addConstr(gp.quicksum((1 - mains.loc[i, "vegan"]) * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum((1 - snacks.loc[j, "vegan"]) * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum((1 - drinks.loc[k, "vegan"]) * z[k] for k in D) == 0)

    if params.get("no_pork", False):
        model.addConstr(gp.quicksum(mains.loc[i, "pork"] * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum(snacks.loc[j, "pork"] * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum(drinks.loc[k, "pork"] * z[k] for k in D) == 0)

    if params.get("no_beef", False):
        model.addConstr(gp.quicksum(mains.loc[i, "beef"] * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum(snacks.loc[j, "beef"] * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum(drinks.loc[k, "beef"] * z[k] for k in D) == 0)

    if params.get("no_chicken", False):
        model.addConstr(gp.quicksum(mains.loc[i, "chicken"] * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum(snacks.loc[j, "chicken"] * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum(drinks.loc[k, "chicken"] * z[k] for k in D) == 0)

    if params.get("no_fish", False):
        model.addConstr(gp.quicksum(mains.loc[i, "fish"] * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum(snacks.loc[j, "fish"] * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum(drinks.loc[k, "fish"] * z[k] for k in D) == 0)

    if params.get("gluten_free", False):
        model.addConstr(gp.quicksum(mains.loc[i, "gluten"] * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum(snacks.loc[j, "gluten"] * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum(drinks.loc[k, "gluten"] * z[k] for k in D) == 0)

    if params.get("dairy_free", False):
        model.addConstr(gp.quicksum(mains.loc[i, "dairy"] * x[i] for i in M) == 0)
        model.addConstr(gp.quicksum(snacks.loc[j, "dairy"] * y[j] for j in S) == 0)
        model.addConstr(gp.quicksum(drinks.loc[k, "dairy"] * z[k] for k in D) == 0)

    # protein preference
    protein_pref = params.get("protein_preference", "any")
    if protein_pref == "pork":
        model.addConstr(gp.quicksum(mains.loc[i, "pork"] * x[i] for i in M) == 1)
    elif protein_pref == "beef":
        model.addConstr(gp.quicksum(mains.loc[i, "beef"] * x[i] for i in M) == 1)
    elif protein_pref == "chicken":
        model.addConstr(gp.quicksum(mains.loc[i, "chicken"] * x[i] for i in M) == 1)
    elif protein_pref == "fish":
        model.addConstr(gp.quicksum(mains.loc[i, "fish"] * x[i] for i in M) == 1)
    elif protein_pref == "others":
        model.addConstr(gp.quicksum(mains.loc[i, "other_protein"] * x[i] for i in M) == 1)

    # snack preference
    snack_pref = params.get("snack_preference", "no_preference")
    if snack_pref == "sweet":
        model.addConstr(gp.quicksum(snacks.loc[j, "sweet"] * y[j] for j in S) == 1)
    elif snack_pref == "salty":
        model.addConstr(gp.quicksum(snacks.loc[j, "salty"] * y[j] for j in S) == 1)
    elif snack_pref == "both":
        model.addConstr(gp.quicksum(snacks.loc[j, "sweet_and_salty"] * y[j] for j in S) == 1)

    # main type preference
    main_type_pref = params.get("main_type_preference", "no_preference")
    if main_type_pref == "wrap":
        model.addConstr(gp.quicksum(mains.loc[i, "wrap"] * x[i] for i in M) == 1)
    elif main_type_pref == "sandwich":
        model.addConstr(gp.quicksum(mains.loc[i, "sandwich"] * x[i] for i in M) == 1)
    elif main_type_pref == "sushi":
        model.addConstr(gp.quicksum(mains.loc[i, "sushi"] * x[i] for i in M) == 1)
    elif main_type_pref == "bowl":
        model.addConstr(gp.quicksum(mains.loc[i, "bowl"] * x[i] for i in M) == 1)

    # cuisine preference
    cuisine_pref = params.get("cuisine_preference", "no_preference")
    if cuisine_pref == "western":
        model.addConstr(gp.quicksum(mains.loc[i, "western"] * x[i] for i in M) == 1)
    elif cuisine_pref == "asian":
        model.addConstr(gp.quicksum(mains.loc[i, "asian"] * x[i] for i in M) == 1)
    elif cuisine_pref == "mediterranean":
        model.addConstr(gp.quicksum(mains.loc[i, "mediterranean"] * x[i] for i in M) == 1)
    elif cuisine_pref == "indian":
        model.addConstr(gp.quicksum(mains.loc[i, "indian"] * x[i] for i in M) == 1)
    elif cuisine_pref == "caribbean":
        model.addConstr(gp.quicksum(mains.loc[i, "caribbean"] * x[i] for i in M) == 1)

    # prime preference
    prime_pref = params.get("prime_preference", "no_preference")
    if prime_pref == "prime_only":
        model.addConstr(gp.quicksum(mains.loc[i, "is_prime"] * x[i] for i in M) == 1)
    elif prime_pref == "non_prime_only":
        model.addConstr(gp.quicksum((1 - mains.loc[i, "is_prime"]) * x[i] for i in M) == 1)

    # caffeine preference
    caffeine_pref = params.get("caffeine_preference", "no_preference")
    if caffeine_pref == "caffeine_only":
        model.addConstr(gp.quicksum(drinks.loc[k, "caffeine"] * z[k] for k in D) == 1)
    elif caffeine_pref == "no_caffeine":
        model.addConstr(gp.quicksum((1 - drinks.loc[k, "caffeine"]) * z[k] for k in D) == 1)

    # nutrition constraints
    if params.get("min_protein") is not None:
        model.addConstr(total_protein >= params["min_protein"])
    if params.get("max_protein") is not None:
        model.addConstr(total_protein <= params["max_protein"])

    if params.get("min_calories") is not None:
        model.addConstr(total_calories >= params["min_calories"])
    if params.get("max_calories") is not None:
        model.addConstr(total_calories <= params["max_calories"])

    if params.get("min_sugar") is not None:
        model.addConstr(total_sugar >= params["min_sugar"])
    if params.get("max_sugar") is not None:
        model.addConstr(total_sugar <= params["max_sugar"])

    if params.get("min_fat") is not None:
        model.addConstr(total_fat >= params["min_fat"])
    if params.get("max_fat") is not None:
        model.addConstr(total_fat <= params["max_fat"])

    if params.get("min_carbs") is not None:
        model.addConstr(total_carbs >= params["min_carbs"])
    if params.get("max_carbs") is not None:
        model.addConstr(total_carbs <= params["max_carbs"])

    if params.get("min_salt") is not None:
        model.addConstr(total_salt >= params["min_salt"])
    if params.get("max_salt") is not None:
        model.addConstr(total_salt <= params["max_salt"])

    if params.get("max_snack_calories") is not None:
        snack_calories = gp.quicksum(snacks.loc[j, "calories"] * y[j] for j in S)
        model.addConstr(snack_calories <= params["max_snack_calories"])

    if params.get("max_drink_calories") is not None:
        drink_calories = gp.quicksum(drinks.loc[k, "calories"] * z[k] for k in D)
        model.addConstr(drink_calories <= params["max_drink_calories"])

    # objective
    obj = params.get("objective", "max_protein")

    if obj == "max_protein":
        model.setObjective(total_protein, GRB.MAXIMIZE)
    elif obj == "min_sugar":
        model.setObjective(total_sugar, GRB.MINIMIZE)
    elif obj == "min_fat":
        model.setObjective(total_fat, GRB.MINIMIZE)
    elif obj == "min_carbs":
        model.setObjective(total_carbs, GRB.MINIMIZE)
    elif obj == "min_calories":
        model.setObjective(total_calories, GRB.MINIMIZE)
    elif obj == "min_salt":
        model.setObjective(total_salt, GRB.MINIMIZE)
    elif obj == "max_savings":
        model.setObjective(total_savings, GRB.MAXIMIZE)
    else:
        raise ValueError(f"Unknown objective: {obj}")

    model.optimize()

    if model.Status != GRB.OPTIMAL:
        return None

    selected_main_idx = [i for i in M if x[i].X > 0.5][0]
    selected_snack_idx = [j for j in S if y[j].X > 0.5][0]
    selected_drink_idx = [k for k in D if z[k].X > 0.5][0]

    selected_main = mains.loc[selected_main_idx]
    selected_snack = snacks.loc[selected_snack_idx]
    selected_drink = drinks.loc[selected_drink_idx]

    return {
        "main": selected_main["item"],
        "snack": selected_snack["item"],
        "drink": selected_drink["item"],
        "main_price": float(selected_main["price"]),
        "snack_price": float(selected_snack["price"]),
        "drink_price": float(selected_drink["price"]),
        "main_is_prime": int(selected_main["is_prime"]),
        "meal_deal_price": float(meal_deal_price.getValue()),
        "total_individual_price": float(total_individual_price.getValue()),
        "total_savings": float(total_savings.getValue()),
        "total_calories": float(total_calories.getValue()),
        "total_protein": float(total_protein.getValue()),
        "total_sugar": float(total_sugar.getValue()),
        "total_fat": float(total_fat.getValue()),
        "total_carbs": float(total_carbs.getValue()),
        "total_salt": float(total_salt.getValue()),
        "objective_used": obj,
        "objective_value": float(model.ObjVal),
    }
