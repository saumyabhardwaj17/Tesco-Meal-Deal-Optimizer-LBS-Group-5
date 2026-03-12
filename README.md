# Tesco Meal Deal Optimizer 🥪🍪🥤

- Made by Group 5, MAM LBS students for Decision Analytics course.

An interactive optimization tool that helps users build the **best Tesco meal deal** based on their dietary preferences and nutritional goals.

The app uses **mixed-integer optimization with Gurobi** to select the optimal combination of **one main, one snack, and one drink** from the Tesco meal deal dataset.

Users can specify dietary restrictions, meal style preferences, and optimization objectives, and the system computes the **optimal meal deal along with nutrition information and cost savings**.

---

# Features

### Optimization Objectives

The system can optimize meal deals based on:

* Maximize protein
* Minimize sugar
* Minimize fat
* Maximize savings

---

### Dietary Restrictions

Users can filter meals based on:

* Vegetarian
* Vegan
* Dairy-free
* Gluten-free
* No pork
* No beef
* No chicken
* No fish

---

### Meal Style Preferences

The optimizer can also adapt meals based on user goals:

* High protein meal
* Healthy meal
* Light meal
* Low sugar meal
* No preference

---

### Outputs

For each optimized meal deal, the app displays:

* Selected **Main, Snack, and Drink**
* Total **Calories**
* **Protein**
* **Sugar**
* **Fat**
* **Individual item prices**
* **Tesco meal deal price**
* **Total savings**

---

# Optimization Model

The system formulates the meal selection as a **Mixed Integer Programming (MIP)** problem.

Decision variables determine whether an item is selected.

Constraints ensure:

* Exactly **one main**
* Exactly **one snack**
* Exactly **one drink**
* Dietary restrictions are satisfied
* Nutritional bounds are respected

The model is solved using **Gurobi**.

---

### Tesco Meal Deal Pricing Logic

Tesco meal deal pricing depends **only on the main item**:

| Main Type    | Meal Deal Price |
| ------------ | --------------- |
| Regular Main | £3.85           |
| Prime Main   | £5.50           |

Savings are calculated as:

```
Savings = Total Individual Price − Meal Deal Price
```

---

# Tech Stack

* Python
* Streamlit
* Gurobi Optimizer
* Pandas
* NumPy

---

# Project Structure

```
tesco-meal-deal-optimizer
│
├── app.py
├── optimizer.py
├── requirements.txt
├── data.xlsx
├── bg.png
├── model.ipynb
└── README.md
```

# Future Improvements

* Add multiple optimized meal suggestions
* Include allergens and ingredient filtering
* Integrate real-time Tesco pricing
* Add calorie targets for users
* Expand to other retailers

---

# License

This project is for educational purposes.

---
