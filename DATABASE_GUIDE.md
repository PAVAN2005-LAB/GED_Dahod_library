# 🗄️ Database Schema & Configuration Guide

This document outlines the core database schema for the GECDahod Library Management System and provides instructions on how to migrate from the default SQLite database to a production-ready database like MySQL or PostgreSQL.

---

## 🏗️ Core Database Schema

The system uses Django's ORM. Below is an overview of the primary models/tables used in the application.

### 1. `Student` Table
Represents a student registered in the library system.
- **`enrollment_id`** (Primary Key, CharField): 12-digit unique enrollment ID/barcode.
- **`name`** (CharField): Full name of the student.
- **`email`** (EmailField): Student's email address.
- **`mobile_no`** (CharField): 10-digit mobile number.
- **`department`** (CharField): Department choices (Computer, EC, Civil, Electrical, Mechanical).

### 2. `Book` Table
Represents a physical book in the library inventory.
- **`access_code`** (Primary Key, CharField): Unique barcode/Access Code for the book.
- **`title`** (CharField): Title of the book.
- **`author`** (CharField, Optional): Author's name.
- **`isbn_no`** (CharField, Optional): Standard ISBN number.
- **`pages`** (IntegerField, Optional): Total pages in the book.
- **`edition`** (CharField, Optional): Edition details (e.g., "3rd Edition").
- **`allocated_department`** (CharField, Optional): Assigned department for the book.
- **`shelf_location`** (CharField): Physical location/shelf identifier.
- **`status`** (CharField): Current status (`Available` or `Issued`).
- **`current_holder`** (ForeignKey to `Student`, Optional): The student who currently holds the book.

### 3. `LibraryLog` Table
Tracks student entry/exit from the physical library premises.
- **`id`** (Primary Key): Auto-incremented ID.
- **`student`** (ForeignKey to `Student`): The student entering/exiting.
- **`entry_time`** (DateTimeField): Timestamp when the student entered (auto-generated).
- **`exit_time`** (DateTimeField, Optional): Timestamp when the student exited.

### 4. `Transaction` Table
Tracks book issue/return transactions.
- **`id`** (Primary Key): Auto-incremented ID.
- **`student`** (ForeignKey to `Student`): The student who borrowed the book.
- **`book`** (ForeignKey to `Book`): The book being borrowed.
- **`issue_date`** (DateTimeField): Timestamp when the book was issued.
- **`due_date`** (DateTimeField): Deadline for returning the book (defaults to 15 days from issue).
- **`returned`** (BooleanField): Status flag indicating if the book has been returned.

### 5. `RenewRequest` Table
Tracks student requests to renew an issued book.
- **`id`** (Primary Key): Auto-incremented ID.
- **`transaction`** (ForeignKey to `Transaction`): The active transaction to be renewed.
- **`request_date`** (DateTimeField): Timestamp of the request.
- **`status`** (CharField): Current status of the request (`Pending`, `Approved`, `Rejected`).

---

## ⚙️ Switching to Another Database

By default, the project is configured to use **SQLite** (`db.sqlite3`), which is great for development and small-scale deployments. For larger deployments, you may want to use a more robust database like MySQL or PostgreSQL.

To switch databases, you need to modify the `DATABASES` dictionary in your `config/settings.py` file and install the appropriate database driver.

### 🐘 Option 1: PostgreSQL (Recommended)

1. **Install the PostgreSQL driver:**
   ```bash
   pip install psycopg2-binary
   ```
   *(Note: Ensure you add this to your `requirements.txt`)*

2. **Update `config/settings.py`:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'library_db',
           'USER': 'your_postgres_user',
           'PASSWORD': 'your_postgres_password',
           'HOST': 'localhost',  # Or your database server IP
           'PORT': '5432',       # Default PostgreSQL port
       }
   }
   ```

### 🐬 Option 2: MySQL

1. **Install the MySQL driver:**
   ```bash
   pip install mysqlclient
   ```
   *(Note: Ensure you add this to your `requirements.txt`)*

2. **Update `config/settings.py`:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'library_db',
           'USER': 'your_mysql_user',
           'PASSWORD': 'your_mysql_password',
           'HOST': 'localhost',  # Or your database server IP
           'PORT': '3306',       # Default MySQL port
       }
   }
   ```

### 🔄 Applying Changes

After switching your database configuration:

1. Ensure the target database (`library_db` in the examples above) is actually created on your database server.
2. Run migrations to generate the tables in your new database:
   ```bash
   python manage.py migrate
   ```
3. (Optional) You will need to recreate your admin superuser, as the old database data won't transfer automatically:
   ```bash
   python manage.py createsuperuser
   ```
