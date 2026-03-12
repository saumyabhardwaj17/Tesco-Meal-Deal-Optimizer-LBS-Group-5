import streamlit as st
from optimizer import load_data, solve_meal_deal
import base64


# ---------------- PAGE CONFIG ----------------

st.set_page_config(page_title="Tesco Meal Deal Optimizer", layout="centered", page_icon="🍽️")


# ---------------- BACKGROUND IMAGE ----------------

def add_bg():
    with open("bg.png", "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
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

st.markdown("""
<style>

/* Form Card */
div[data-testid="stForm"] {
    background-color: white;
    padding: 30px;
    border-radius: 14px;
    box-shadow: 0px 6px 20px rgba(0,0,0,0.15);
    margin-top: 20px;
}

/* Make inputs cleaner */
div[data-baseweb="select"] {
    background-color: #f8f9fb;
    border-radius: 8px;
}

/* Button styling */
button[kind="primary"] {
    background-color: #00539f;
    border-radius: 8px;
}

/* Headings spacing */
h2, h3 {
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "generated" not in st.session_state:
    st.session_state.generated = False

if "result" not in st.session_state:
    st.session_state.result = None

if "params" not in st.session_state:
    st.session_state.params = None


# ---------------- TITLE ----------------

st.markdown(
    """
    <div style="text-align:center; padding-top:40px; padding-bottom:20px;">
        <h1 style="font-size:48px;">Tesco Meal Deal Optimizer</h1>
        <p style="font-size:18px; color:#555;">
            Choose your preferences and generate an optimized Tesco meal deal.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------- FORM ----------------

st.markdown('<div class="form-card">', unsafe_allow_html=True)

with st.form("meal_form"):

    st.subheader("Optimization Goal")

    objective = st.selectbox(
        "",
        [
            "max_protein",
            "min_sugar",
            "min_fat",
            "max_savings"
        ]
    )

    st.subheader("Meal Style")

    meal_style = st.selectbox(
        "What type of meal do you want?",
        [
            "No preference",
            "High protein meal",
            "Healthy meal",
            "Light meal",
            "Low sugar meal"
        ]
    )

    st.subheader("Dietary Restrictions")

    col1, col2 = st.columns(2)

    with col1:
        vegetarian_only = st.checkbox("Vegetarian only")
        vegan_only = st.checkbox("Vegan only")
        no_pork = st.checkbox("No pork")
        no_beef = st.checkbox("No beef")

    with col2:
        no_chicken = st.checkbox("No chicken")
        no_fish = st.checkbox("No fish")
        gluten_free = st.checkbox("Gluten free")
        dairy_free = st.checkbox("Dairy free")

    button_col1, button_col2, button_col3 = st.columns([1,2,1])

    with button_col2:
        submitted = st.form_submit_button("Generate Optimal Meal")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- RUN OPTIMIZATION ----------------

if submitted:

    params = {
        "objective": objective,
        "meal_style": meal_style,
        "vegetarian_only": vegetarian_only,
        "vegan_only": vegan_only,
        "no_pork": no_pork,
        "no_beef": no_beef,
        "no_chicken": no_chicken,
        "no_fish": no_fish,
        "gluten_free": gluten_free,
        "dairy_free": dairy_free
    }

    mains, snacks, drinks = load_data()

    result = solve_meal_deal(mains, snacks, drinks, params)

    st.session_state.generated = True
    st.session_state.result = result
    st.session_state.params = params


# ---------------- SHOW USER SELECTIONS ----------------

if st.session_state.generated:

    params = st.session_state.params

    st.divider()
    st.subheader("Your Preferences")

    restrictions = []

    if params["vegetarian_only"]:
        restrictions.append("Vegetarian")

    if params["vegan_only"]:
        restrictions.append("Vegan")

    if params["dairy_free"]:
        restrictions.append("Dairy-Free")

    if params["gluten_free"]:
        restrictions.append("Gluten-Free")

    if params["no_pork"]:
        restrictions.append("No Pork")

    if params["no_beef"]:
        restrictions.append("No Beef")

    if params["no_chicken"]:
        restrictions.append("No Chicken")

    if params["no_fish"]:
        restrictions.append("No Fish")

    col1, col2, col3 = st.columns(3)

    def pref_card(title, value):
        st.markdown(
            f"""
            <div style="
                background:white;
                padding:15px;
                border-radius:10px;
                box-shadow:0px 3px 10px rgba(0,0,0,0.1);
                text-align:center;
            ">
            <p style="font-size:14px; color:#666; margin-bottom:4px;">{title}</p>
            <p style="font-size:18px; font-weight:600;">{value}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col1:
        pref_card("Goal", params["objective"].replace("_"," ").title())

    with col2:
        pref_card("Meal Style", params["meal_style"])

    with col3:
        pref_card("Restrictions", ", ".join(restrictions) if restrictions else "None")

# ---------------- RESULT SECTION ----------------

if st.session_state.generated:

    result = st.session_state.result

    if result is None:
        st.error("No feasible meal found with these preferences.")

    else:

        #st.success("Optimal Meal Deal Found")

        # ---------------- MEAL CARDS ----------------

        st.subheader("Your Optimized Meal Deal")

        col1, col2, col3 = st.columns(3)

        def meal_card(emoji, title, name, price):

            st.markdown(
                f"""
                <div style="
                    background-color:white;
                    padding:20px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                ">
                <h1>{emoji}</h1>
                <h4>{title}</h4>
                <p style="font-weight:bold;">{name}</p>
                <p style="font-size:18px;color:#2e7d32;">£{price}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col1:
            meal_card("🥪", "Main", result["main"], round(result["main_price"],2))

        with col2:
            meal_card("🍪", "Snack", result["snack"], round(result["snack_price"],2))

        with col3:
            meal_card("🥤", "Drink", result["drink"], round(result["drink_price"],2))


        # ---------------- NUTRITION ----------------
        
        # ---------------- NUTRITION ----------------

        st.subheader("🥗 Nutrition")

        n1, n2, n3, n4 = st.columns(4)

        def nutrition_card(title, value):

            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:18px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                ">
                    <p style="color:#666; margin-bottom:5px;">{title}</p>
                    <h2>{value}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with n1:
            nutrition_card("Calories", round(result["total_calories"],1))

        with n2:
            nutrition_card("Protein", round(result["total_protein"],1))

        with n3:
            nutrition_card("Sugar", round(result["total_sugar"],1))

        with n4:
            nutrition_card("Fat", round(result["total_fat"],1))


        # ---------------- PRICE BREAKDOWN ----------------

        st.subheader("💰 Price Summary")

        price_col1, price_col2 = st.columns(2)

        with price_col1:
            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:20px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                ">
                <p style="color:#666; margin-bottom:5px;">Total Individual Price</p>
                <h2>£{round(result['total_individual_price'],2)}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

        with price_col2:
            st.markdown(
                f"""
                <div style="
                    background:white;
                    padding:20px;
                    border-radius:12px;
                    text-align:center;
                    box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                ">
                <p style="color:#666; margin-bottom:5px;">Tesco Meal Deal Price</p>
                <h2>£{round(result['meal_deal_price'],2)}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )



        # ---------------- SAVINGS CARD ----------------

        st.markdown(
            f"""
            <div style="
                background:#e8f5e9;
                padding:20px;
                border-radius:12px;
                text-align:center;
                box-shadow:0px 4px 12px rgba(0,0,0,0.1);
                margin-top:20px;
            ">
                <p style="color:#2e7d32; margin-bottom:5px; font-weight:600;">
                Your Savings
                </p>
                <p1 style="color:#2e7d32; margin-bottom:5px; font-weight:600;">
                Savings = Individual Price - Meal Deal Price
                </p1>
                <h2 style="color:#2e7d32;">
                £{round(result['total_savings'],2)}
                </h2>
            </div>
            """,
            unsafe_allow_html=True
        )