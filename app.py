import streamlit as st
from optimizer import load_data, solve_meal_deal
import base64

st.set_page_config(page_title="Tesco Meal Deal Optimizer", layout="centered")

# ---------- BACKGROUND ----------

def add_bg():
    with open("bg.png", "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
        }}

        .block-container {{
            background: rgba(255,255,255,0.92);
            padding: 2rem;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg()

# ---------- TITLE ----------

st.markdown(
"""
<div style="text-align:center">
<h1>Tesco Meal Deal Optimizer</h1>
<p style="color:#666">
Choose your preferences and generate an optimized Tesco meal deal.
</p>
</div>
""",
unsafe_allow_html=True
)

# ---------- FORM ----------

with st.form("meal_form"):

    st.subheader("Optimization Goal")
    st.caption("Optimization Goal determines what the model maximizes or minimizes.")

    objective = st.selectbox(
        "",
        [
            "Max Protein",
            "Min Sugar",
            "Min Fat",
            "Min Carbs",
            "Min Calories",
            "Min Salt",
            "Max Savings"
        ]
    )

    # ---------- PREFERENCES ----------

    st.subheader("Food Preferences")

    col1, col2 = st.columns(2)

    with col1:
        protein_preference = st.selectbox(
            "Protein Preference",
            ["No Preference", "Pork", "Beef", "Chicken", "Fish", "Others"]
        )

        snack_preference = st.selectbox(
            "Snack Preference",
            ["No Preference", "Sweet", "Salty", "Both"]
        )

        caffeine_preference = st.selectbox(
            "Drink Caffeine Preference",
            ["No Preference", "Caffeine Only", "No Caffeine"]
        )

    with col2:
        main_type_preference = st.selectbox(
            "Main Type",
            ["No Preference", "Wrap", "Sandwich", "Sushi", "Bowl"]
        )

        cuisine_preference = st.selectbox(
            "Cuisine",
            ["No Preference", "Western", "Asian", "Mediterranean", "Indian", "Caribbean"]
        )

        prime_preference = st.selectbox(
            "Prime Preference",
            ["No Preference", "Prime Only", "Non Prime Only"]
        )

    # ---------- DIETARY ----------

    st.subheader("Dietary Restrictions")

    col1, col2 = st.columns(2)

    with col1:
        vegetarian_only = st.checkbox("Vegetarian")
        vegan_only = st.checkbox("Vegan")
        no_pork = st.checkbox("No Pork")
        no_beef = st.checkbox("No Beef")

    with col2:
        no_chicken = st.checkbox("No Chicken")
        no_fish = st.checkbox("No Fish")
        gluten_free = st.checkbox("Gluten Free")
        dairy_free = st.checkbox("Dairy Free")

    # ---------- NUTRITION ----------

    st.subheader("Nutrition Constraints")

    col1, col2 = st.columns(2)

    with col1:
        min_protein = st.number_input("Minimum Protein (g)", 0.0, 200.0, 25.0, step=1.0)
        max_protein = st.number_input("Maximum Protein (g)", 0.0, 200.0, 100.0, step=1.0)

        min_calories = st.number_input("Minimum Calories (kcal)", 0.0, 2000.0, 0.0, step=10.0)
        max_calories = st.number_input("Maximum Calories (kcal)", 0.0, 2000.0, 800.0, step=10.0)

        min_sugar = st.number_input("Minimum Sugar (g)", 0.0, 200.0, 0.0, step=1.0)
        max_sugar = st.number_input("Maximum Sugar (g)", 0.0, 200.0, 40.0, step=1.0)

        min_fat = st.number_input("Minimum Fat (g)", 0.0, 200.0, 0.0, step=1.0)
        max_fat = st.number_input("Maximum Fat (g)", 0.0, 200.0, 35.0, step=1.0)

    with col2:
        min_carbs = st.number_input("Minimum Carbs (g)", 0.0, 300.0, 0.0, step=1.0)
        max_carbs = st.number_input("Maximum Carbs (g)", 0.0, 300.0, 120.0, step=1.0)

        min_salt = st.number_input("Minimum Salt (g)", 0.0, 10.0, 0.0, step=0.1)
        max_salt = st.number_input("Maximum Salt (g)", 0.0, 10.0, 2.0, step=0.1)

        max_snack_calories = st.number_input("Maximum Snack Calories (kcal)", 0.0, 1000.0, 300.0, step=10.0)
        max_drink_calories = st.number_input("Maximum Drink Calories (kcal)", 0.0, 1000.0, 150.0, step=10.0)

    submitted = st.form_submit_button("Generate Optimal Meal")


# ---------- CLEAN FUNCTION ----------

def clean(val):
    return val.lower().replace(" ", "_")


def none_if_default(value, default_max):
    return None if value == default_max else value


def zero_to_none_for_min(value):
    return None if value == 0 else value


# ---------- RUN OPTIMIZER ----------

if submitted:

    params = {
        "objective": clean(objective),

        "regular_price": 3.85,
        "prime_price": 5.50,

        "protein_preference": clean(protein_preference),
        "snack_preference": clean(snack_preference),
        "main_type_preference": clean(main_type_preference),
        "cuisine_preference": clean(cuisine_preference),
        "prime_preference": clean(prime_preference),
        "caffeine_preference": clean(caffeine_preference),

        "vegetarian_only": vegetarian_only,
        "vegan_only": vegan_only,
        "no_pork": no_pork,
        "no_beef": no_beef,
        "no_chicken": no_chicken,
        "no_fish": no_fish,
        "gluten_free": gluten_free,
        "dairy_free": dairy_free,

        "min_protein": zero_to_none_for_min(min_protein),
        "max_protein": none_if_default(max_protein, 100.0),

        "min_calories": zero_to_none_for_min(min_calories),
        "max_calories": none_if_default(max_calories, 800.0),

        "min_sugar": zero_to_none_for_min(min_sugar),
        "max_sugar": none_if_default(max_sugar, 40.0),

        "min_fat": zero_to_none_for_min(min_fat),
        "max_fat": none_if_default(max_fat, 35.0),

        "min_carbs": zero_to_none_for_min(min_carbs),
        "max_carbs": none_if_default(max_carbs, 120.0),

        "min_salt": zero_to_none_for_min(min_salt),
        "max_salt": none_if_default(max_salt, 2.0),

        "max_snack_calories": none_if_default(max_snack_calories, 300.0),
        "max_drink_calories": none_if_default(max_drink_calories, 150.0),
    }

    mains, snacks, drinks = load_data()
    result = solve_meal_deal(mains, snacks, drinks, params)

    if result is None:
        st.error("No feasible meal found with these preferences.")

    else:
        st.subheader("Optimized Meal Deal")

        col1, col2, col3 = st.columns(3)

        def meal_card(emoji, title, name, price):
            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:20px;
                    border-radius:14px;
                    text-align:center;
                    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                    overflow:hidden;
                ">
                <div style="font-size:32px;margin-bottom:6px;">
                    {emoji}
                </div>

                <p style="color:#666;margin:0;">
                {title}
                </p>

                <p style="
                    font-weight:600;
                    margin:8px 0;
                    line-height:1.4;
                    font-size:16px;
                    word-break:break-word;
                ">
                {name}
                </p>

                <p style="color:#2e7d32;font-size:18px;margin:0;">
                £{price}
                </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col1:
            meal_card("🥪", "Main", result["main"], round(result["main_price"], 2))
        with col2:
            meal_card("🍪", "Snack", result["snack"], round(result["snack_price"], 2))
        with col3:
            meal_card("🥤", "Drink", result["drink"], round(result["drink_price"], 2))

        # ---------- NUTRITION ----------

        st.subheader("Nutrition")

        n1, n2, n3, n4, n5, n6 = st.columns(6)

        def nutrition_card(title, value):
            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:18px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                    overflow:hidden;
                    min-height:120px;
                ">
                <p style="color:#666;margin-bottom:6px;">
                {title}
                </p>

                <h2 style="
                    margin:0;
                    font-size:22px;
                    word-break:break-word;
                ">
                {value}
                </h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with n1:
            nutrition_card("Calories", f"{round(result['total_calories'], 1)} kcal")
        with n2:
            nutrition_card("Protein", f"{round(result['total_protein'], 1)} g")
        with n3:
            nutrition_card("Sugar", f"{round(result['total_sugar'], 1)} g")
        with n4:
            nutrition_card("Fat", f"{round(result['total_fat'], 1)} g")
        with n5:
            nutrition_card("Carbs", f"{round(result['total_carbs'], 1)} g")
        with n6:
            nutrition_card("Salt", f"{round(result['total_salt'], 2)} g")

        # ---------- PRICE ----------

        st.subheader("Price")

        p1, p2 = st.columns(2)

        with p1:
            nutrition_card("Individual Price", f"£{round(result['total_individual_price'], 2)}")

        with p2:
            nutrition_card("Meal Deal Price", f"£{round(result['meal_deal_price'], 2)}")

        # ---------- SAVINGS ----------

        st.markdown(
            f"""
            <div style="
                background:#e8f5e9;
                padding:25px;
                border-radius:16px;
                text-align:center;
                margin-top:20px;
                box-shadow:0px 4px 12px rgba(0,0,0,0.1);
            ">
            <p style="color:#2e7d32;font-weight:600">
            Your Savings
            </p>

            <p style="color:#666">
            Savings = Individual Price − Meal Deal Price
            </p>

            <h1 style="color:#2e7d32">
            £{round(result['total_savings'], 2)}
            </h1>
            </div>
            """,
            unsafe_allow_html=True
        )
