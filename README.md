# Kıvanç Tatlıtuğ Wannabes

A Django web application that helps users follow their diet and exercise plans. Users can log their meals and workouts, and the app tracks their daily caloric intake and expenditure based on personal information such as age, weight, height, and activity level.

The app supports two user roles:

- **Client** — logs meals and exercises, tracks daily calorie intake/burn, and manages their own profile.
- **Dietitian** — has a specialty, and (in progress) can view a list of their assigned clients.

## Requirements

- Python 3.14+
- pip

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

5. **Apply the database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create an admin (superuser) account**

   ```bash
   python manage.py createsuperuser
   ```

   You'll be prompted for a username, email, and password. This account can be used to log in to the Django admin panel at `/admin/` to manage data such as foods and exercises.

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

8. **Open the app**

   Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. You'll be redirected to the main tracker page, where you can register as a Client or Dietitian, or log in if you already have an account.

## Project structure

- `mysite/` — Django project settings and root URL configuration.
- `tracker/` — the main app, containing all models, views, forms, templates, and URLs for the tracker functionality.

## Notes

- The project uses [Ruff](https://docs.astral.sh/ruff/) for linting (see `pyproject.toml`).
- Food and exercise entries are currently added manually through the Django admin panel.
