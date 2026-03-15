# GECDahod Library System - Production Server

This is the **Production** branch. This branch is configured to run on your college's local network server for real-world use.

## System Architecture

Here is the high-level architecture of the GECDahod Library System. It leverages Waitress as a production WSGI server and WhiteNoise for static files, making it a robust and self-contained solution for local network deployment.

```mermaid
graph TD
    %% User Interfaces
    Admin[Admin / Staff]
    Student[Student / Library User]
    Scanner[Kiosk Barcode Scanner]
    
    %% Middlewares and Routing
    Nginx[College Network Firewall / Intranet]
    Waitress[Waitress WSGI Server Port 800]
    
    %% Django Core
    subgraph Django Application
        DjangoRouter[URL Routing]
        WhiteNoise[WhiteNoise Static Files]
        Auth[JWT & Admin Auth]
        Views[Business Logic / Views]
        Reports[Reporting Engine Pandas]
        ORM[Django ORM]
    end

    %% Database & Storage
    DB[(SQLite Database)]
    Disk[File System Logs]

    %% Connections
    Student --> |View Dashboard| Nginx
    Admin --> |Access Admin Panel / Reports| Nginx
    Scanner --> |POST /kiosk Barcode| Nginx

    Nginx -.-> |HTTP Port 800| Waitress
    Waitress --> DjangoRouter
    DjangoRouter --> WhiteNoise
    DjangoRouter --> Auth
    Auth --> Views
    Views --> Reports
    Views --> ORM
    Reports -.-> |Generate .xlsx| ORM
    ORM <--> DB
    DB <--> Disk
    
    classDef ui fill:#4a90e2,stroke:#000,stroke-width:2px,color:#fff;
    classDef server fill:#f5a623,stroke:#000,stroke-width:2px,color:#fff;
    classDef app fill:#7ed321,stroke:#000,stroke-width:2px,color:#fff;
    classDef db fill:#9013fe,stroke:#000,stroke-width:2px,color:#fff;
    
    class Admin,Student,Scanner ui;
    class Nginx,Waitress server;
    class DjangoRouter,WhiteNoise,Auth,Views,Reports,ORM app;
    class DB,Disk db;
```

## Deployment Steps (College Server)

1. **Clone the Production branch:**
   ```bash
   git clone -b production https://github.com/PAVAN2005-LAB/GED_Dahod_library.git
   ```

2. **Setup Environment:**
   - Install dependencies: `pip install -r requirements.txt`
   - Create a `.env` file from `.env.example`.
   - **Crucial:** Set `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS=*`.

3. **Prepare Static Files & Database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. **Start the Server (Running on Port 800):**
   ```bash
   python run_server.py
   ```

## Accessing the System
Once the server is running, anyone on the college network can access it by visiting the server's IP address and port 800:
`http://[YOUR_SERVER_IP]:800`
 check your ip address by typing `ipconfig` in the command prompt.

---

## Bulk Import Data (Students & Books)

You can easily bulk import students and books from standard `.csv` files using our custom management command `import_data`. This is built for fast ingestion while automatically checking for and skipping duplicate entries.

### Import Students
*Expected CSV Headers: `enrollment_id`, `name`, `email`, `mobile_no`, `department`*
```bash
python manage.py import_data students /absolute/path/to/your/students.csv
```

### Import Books
*Expected CSV Headers: `access_code`, `title`, `author`, `shelf_location`*  
*(Note: `access_code` maps to Book ID in the database)*
```bash
python manage.py import_data books /absolute/path/to/your/books.csv
```

---

## API Endpoints Documentation

We provide a comprehensive REST API and dedicated Web endpoints for scanning, reports, and JWT authentication. 

**[Click here to read the full API Documentation](API_DOCS.md)**

---

## Key Production Features
- **Waitress Server**: Handles multiple users concurrently on Windows.
- **WhiteNoise Middleware**: Fast and efficient serving of CSS/JS/Images.
- **Port 800**: Standard access on port 800, freeing up default ports and bypassing standard admin restrictions for port 80.
- **Pandas Reporting**: Heavy data processing handled gracefully with Pandas generating `.xlsx` reports on the fly.

---
**Note:** For development and code changes, please use the `local` branch.
