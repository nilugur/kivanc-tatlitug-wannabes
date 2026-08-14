# Kıvanç Tatlıtuğ Wannabes

A Django web application that helps users follow their diet and exercise plans. Users can log their meals and workouts, and the app tracks their daily and weekly caloric intake and expenditure based on personal information such as age, weight, height, and activity level. The app also gives clients personalized food recommendations based on other users with a similar profile.

The app supports two user roles:

- **Client** — logs meals and exercises, tracks daily and weekly calorie intake/burn, manages their own profile, sees personalized food recommendations on their dashboard, and can search for foods (via a live USDA FoodData Central lookup) and exercises when logging entries.
- **Dietitian** — has a specialty, and can view a list of their assigned clients along with each client's profile, daily meal/exercise breakdown, and calorie totals.

## Features

- Role-based registration and login (Client / Dietitian), with role-specific dashboards.
- **Meal Log** page — meals organized by type (Breakfast, Lunch, Dinner, Snack), with the ability to add, edit, and delete individual food items.
- **Add Exercise** page — log workouts with a searchable exercise list, with the ability to edit and delete entries.
- **Food search** — searches the local database first; if no match is found, it automatically searches the **USDA FoodData Central API** and saves the selected result as a new `Food` entry for future use (existing foods are reused rather than duplicated).
- **Exercise search** — searches the local `Exercise` database (exercises are curated and entered manually via the admin panel).
- Daily and **weekly** calorie summaries (consumed vs. burned) on the Client dashboard.
- **Personalized food recommendations** — using a collaborative-filtering approach (cosine similarity over age/gender/goal), the Client dashboard shows a "Recommended For You" section listing foods favored by other users with a similar profile over the last 7 days.
- **Dietitian client view** — a dietitian can open any of their clients' detail pages to see that client's profile, daily meal/exercise breakdown, and calorie totals for any selected date.
- Authorization checks — a client can only manage their own data, and a dietitian can only view their own assigned clients (attempting to access another dietitian's client returns a 403 Forbidden).
- Editable profile pages for both roles.

## Requirements

- Python 3.14+
- pip
- A free API key from [USDA FoodData Central](https://fdc.nal.usda.gov/api-guide.html) (required for the food search feature to fall back to when a food isn't already in the local database)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/nilugur/kivanc-tatlitug-wannabes.git
   cd kivanc-tatlitug-wannabes
   ```

2. **Create a virtual environment**

   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**

   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install the dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   This includes Django itself, plus `pandas` and `scikit-learn`, which are used for the food recommendation feature.

5. **Set up your USDA API key**

   Get a free API key from [fdc.nal.usda.gov/api-guide.html](https://fdc.nal.usda.gov/api-guide.html) (only an email address is required).

   In the project root (the same folder as `manage.py`), create a file named `.env` and add the following line, replacing the placeholder with your actual key:

   ```
   USDA_API_KEY=your_actual_api_key_here
   ```

   This file is listed in `.gitignore` and is never committed to version control — each person running the project needs to create their own `.env` file locally. Without a valid key here, food searches that fall back to the USDA API will fail (the local database search will still work normally).

6. **Apply the database migrations**

   ```bash
   python manage.py migrate
   ```

7. **Create an admin (superuser) account**

   ```bash
   python manage.py createsuperuser
   ```

   You'll be prompted for a username, email, and password. This account can be used to log in to the Django admin panel at `/admin/` to manage data such as foods and exercises.

8. **(Optional) Generate dummy data for recommendations**

   The "Recommended For You" feature compares a client against other users with a similar age/gender/goal, then surfaces the foods those similar users ate most often over the last 7 days. On a fresh database there usually isn't enough data for this to produce meaningful results, so a management command is included to generate realistic sample data:

   ```bash
   python manage.py generate_dummy_data
   ```

   This creates 60 sample client accounts with randomized-but-plausible profiles, and gives each of them a week's worth of meals and exercise logs, patterned according to their goal (weight loss/gain/maintenance) and activity level. It's safe to re-run — it clears out its own previously generated users first, so it won't create duplicates.

9. **Run the development server**

   ```bash
   python manage.py runserver
   ```

10. **Open the app**

    Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. You'll be redirected to the main tracker page, where you can register as a Client or Dietitian, or log in if you already have an account.

## Project structure

- `mysite/` — Django project settings and root URL configuration.
- `tracker/` — the main app, containing all models, views, forms, templates, and URLs for the tracker functionality.
  - `tracker/recommender.py` — the collaborative-filtering logic behind the food recommendations (builds a user feature matrix, computes similarity, and aggregates similar users' recent food choices).
  - `tracker/management/commands/generate_dummy_data.py` — management command that populates the database with sample users and activity data (see setup step 8).
- `.env` — (not committed) holds your local USDA API key. See step 5 above.

## Notes

- The project uses [Ruff](https://docs.astral.sh/ruff/) for linting (see `pyproject.toml`).
- Exercises are curated and added manually through the Django admin panel — the app does not query an external API for exercise data, since the project only requires an external calorie source for foods.
- Foods can be added either manually through the admin panel, or automatically the first time a user searches for and selects a food that comes from the USDA API (it's then saved locally and reused for future searches, without needing another API call).
- If you see errors related to food search failing unexpectedly (e.g. a `KeyError` on the USDA response), double check that your `.env` file exists and contains a valid `USDA_API_KEY` — a missing or invalid key causes the USDA API to reject the request.
- Food recommendations are recalculated on each dashboard load and only consider meals logged in the last 7 days, so they'll naturally shift over time as users (real or sample) log new meals.
