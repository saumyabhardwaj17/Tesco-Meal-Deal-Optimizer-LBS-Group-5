import pandas as pd
import gurobipy as gp
from gurobipy import GRB


def load_data():

    df = pd.read_excel("Data Collection.xlsx")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )

    # Rename to model-friendly names
    df = df.rename(columns={
        "individual_price": "price",
        "energycalories": "calories",
        "fat_g": "fat",
        "carbohydrates_g": "carbs",
        "sugars_g": "sugar",
        "protein_g": "protein",
        "salt_g": "salt",
        "prime5.5gbp": "prime",
        "porks": "pork"
    })

    df["category"] = df["category"].str.lower()

    mains = df[df["category"] == "main"].copy()
    snacks = df[df["category"] == "snack"].copy()
    drinks = df[df["category"] == "drink"].copy()

    return mains, snacks, drinks


def solve_meal_deal(mains, snacks, drinks, params):

    m = gp.Model("meal_deal")

    x = m.addVars(mains.index, vtype=GRB.BINARY)
    y = m.addVars(snacks.index, vtype=GRB.BINARY)
    z = m.addVars(drinks.index, vtype=GRB.BINARY)

    # Select exactly one item per category
    m.addConstr(x.sum() == 1)
    m.addConstr(y.sum() == 1)
    m.addConstr(z.sum() == 1)

    # ---------------- DIETARY CONSTRAINTS ----------------

    # ---------- DIETARY CONSTRAINTS ----------

    def forbid(column, vars, data):
        for i in data.index:
            if data.loc[i, column] == 1:
                m.addConstr(vars[i] == 0)


    # Individual restrictions
    if params["dairy_free"]:
        forbid("dairy", x, mains)
        forbid("dairy", y, snacks)
        forbid("dairy", z, drinks)

    if params["gluten_free"]:
        forbid("gluten", x, mains)
        forbid("gluten", y, snacks)
        forbid("gluten", z, drinks)

    if params["no_pork"]:
        forbid("pork", x, mains)
        forbid("pork", y, snacks)
        forbid("pork", z, drinks)

    if params["no_beef"]:
        forbid("beef", x, mains)
        forbid("beef", y, snacks)
        forbid("beef", z, drinks)

    if params["no_chicken"]:
        forbid("chicken", x, mains)
        forbid("chicken", y, snacks)
        forbid("chicken", z, drinks)

    if params["no_fish"]:
        forbid("fish", x, mains)
        forbid("fish", y, snacks)
        forbid("fish", z, drinks)


    # Vegetarian rule
    if params["vegetarian_only"]:

        forbid("pork", x, mains)
        forbid("beef", x, mains)
        forbid("chicken", x, mains)
        forbid("fish", x, mains)

        forbid("pork", y, snacks)
        forbid("beef", y, snacks)
        forbid("chicken", y, snacks)
        forbid("fish", y, snacks)

        forbid("pork", z, drinks)
        forbid("beef", z, drinks)
        forbid("chicken", z, drinks)
        forbid("fish", z, drinks)


    # Vegan rule
    if params["vegan_only"]:

        forbid("pork", x, mains)
        forbid("beef", x, mains)
        forbid("chicken", x, mains)
        forbid("fish", x, mains)
        forbid("dairy", x, mains)

        forbid("pork", y, snacks)
        forbid("beef", y, snacks)
        forbid("chicken", y, snacks)
        forbid("fish", y, snacks)
        forbid("dairy", y, snacks)

        forbid("pork", z, drinks)
        forbid("beef", z, drinks)
        forbid("chicken", z, drinks)
        forbid("fish", z, drinks)
        forbid("dairy", z, drinks)

    # ---------------- NUTRITION TOTALS ----------------

    total_calories = (
        gp.quicksum(mains.loc[i, "calories"] * x[i] for i in mains.index)
        + gp.quicksum(snacks.loc[i, "calories"] * y[i] for i in snacks.index)
        + gp.quicksum(drinks.loc[i, "calories"] * z[i] for i in drinks.index)
    )

    total_protein = (
        gp.quicksum(mains.loc[i, "protein"] * x[i] for i in mains.index)
        + gp.quicksum(snacks.loc[i, "protein"] * y[i] for i in snacks.index)
        + gp.quicksum(drinks.loc[i, "protein"] * z[i] for i in drinks.index)
    )

    total_sugar = (
        gp.quicksum(mains.loc[i, "sugar"] * x[i] for i in mains.index)
        + gp.quicksum(snacks.loc[i, "sugar"] * y[i] for i in snacks.index)
        + gp.quicksum(drinks.loc[i, "sugar"] * z[i] for i in drinks.index)
    )

    total_fat = (
        gp.quicksum(mains.loc[i, "fat"] * x[i] for i in mains.index)
        + gp.quicksum(snacks.loc[i, "fat"] * y[i] for i in snacks.index)
        + gp.quicksum(drinks.loc[i, "fat"] * z[i] for i in drinks.index)
    )

    # ---------------- MEAL STYLE CONSTRAINTS ----------------

    if params["meal_style"] == "High protein meal":
        m.addConstr(total_protein >= 30)

    if params["meal_style"] == "Healthy meal":
        m.addConstr(total_fat <= 20)
        m.addConstr(total_sugar <= 20)

    if params["meal_style"] == "Light meal":
        m.addConstr(total_calories <= 600)

    if params["meal_style"] == "Low sugar meal":
        m.addConstr(total_sugar <= 10)

    # ---------------- PRICING ----------------

    individual_price = (
        gp.quicksum(mains.loc[i, "price"] * x[i] for i in mains.index)
        + gp.quicksum(snacks.loc[i, "price"] * y[i] for i in snacks.index)
        + gp.quicksum(drinks.loc[i, "price"] * z[i] for i in drinks.index)
    )

    prime_main = gp.quicksum(mains.loc[i, "prime"] * x[i] for i in mains.index)

    meal_price = 3.85 + prime_main * (5.50 - 3.85)

    savings = individual_price - meal_price

    # ---------------- OBJECTIVE ----------------

    if params["objective"] == "max_protein":
        m.setObjective(total_protein, GRB.MAXIMIZE)

    elif params["objective"] == "min_sugar":
        m.setObjective(total_sugar, GRB.MINIMIZE)

    elif params["objective"] == "min_fat":
        m.setObjective(total_fat, GRB.MINIMIZE)

    elif params["objective"] == "max_savings":
        m.setObjective(savings, GRB.MAXIMIZE)

    else:
        m.setObjective(total_calories, GRB.MINIMIZE)

    m.optimize()

    if m.status != GRB.OPTIMAL:
        return None

    main = mains.loc[[i for i in mains.index if x[i].X > 0.5]].iloc[0]
    snack = snacks.loc[[i for i in snacks.index if y[i].X > 0.5]].iloc[0]
    drink = drinks.loc[[i for i in drinks.index if z[i].X > 0.5]].iloc[0]

    return {
        "main": main["item"],
        "snack": snack["item"],
        "drink": drink["item"],

        # Individual item prices
        "main_price": float(main["price"]),
        "snack_price": float(snack["price"]),
        "drink_price": float(drink["price"]),

        # Nutrition
        "total_calories": float(total_calories.getValue()),
        "total_protein": float(total_protein.getValue()),
        "total_sugar": float(total_sugar.getValue()),
        "total_fat": float(total_fat.getValue()),

        # Pricing
        "meal_deal_price": float(meal_price.getValue()),
        "total_individual_price": float(individual_price.getValue()),
        "total_savings": float(savings.getValue()),
    }