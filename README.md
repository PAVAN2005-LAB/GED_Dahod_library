# 📚 GECDahod Library System - Local Development

This is the **Local Development** branch. Use this branch for making code changes, testing new features, and debugging.

## 🛠️ Setup Instructions (Local)

1. **Clone the repository:**
   ```bash
   git clone -b local https://github.com/PAVAN2005-LAB/GED_Dahod_library.git
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Config:**
   Create a `.env` file (copy from `.env.example`) and ensure `DJANGO_DEBUG=True`.

5. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000` in your browser.

## 📁 Key Files
- `management/`: Main application logic.
- `config/`: Project settings.
- `templates/`: HTML files.
- `static/`: CSS and Assets.

---
**Note:** For the live college server, use the `production` branch.
