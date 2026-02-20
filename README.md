# 🚀 GECDahod Library System - Production Server

This is the **Production** branch. This branch is configured to run on your college's local network server for real-world use.

## 🏁 Deployment Steps (College Server)

1. **Clone the Production branch:**
   ```bash
   git clone -b production https://github.com/PAVAN2005-LAB/GED_Dahod_library.git
   ```

2. **Setup Environment:**
   - Install dependencies: `pip install -r requirements.txt waitress whitenoise`
   - Create a `.env` file from `.env.example`.
   - **Crucial:** Set `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS=*`.

3. **Prepare Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Start the Server (Admin Privileges required for Port 80):**
   ```bash
   python run_server.py
   ```

## 🌐 Accessing the System
Once the server is running, anyone on the college network can access it by visiting the server's IP address:
`http://[YOUR_SERVER_IP]`

## ⚙️ Key Production Features
- **Waitress Server**: Handles multiple users concurrently.
- **WhiteNoise Middleware**: Fast and efficient serving of CSS/JS/Images.
- **Port 80**: Standard web access (no need for `:8000`).

---
**Note:** For development and code changes, please use the `local` branch.
