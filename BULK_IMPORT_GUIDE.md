# 📤 Bulk Data Import Guide

This guide explains how to import large amounts of Student and Book data into the GECDahod Library System using CSV files.

## 📋 1. Preparing your CSV Files

You must use a `.csv` format. You can create these in Microsoft Excel and use "Save As -> CSV (Comma delimited)".

### A. Student CSV Format
**File Name Example:** `students_data.csv`  
**Required Headers (First Row):**
- `enrollment_id`: Unique ID for the student (Primary Key)
- `name`: Full name
- `email`: College or personal email
- `mobile_no`: Contact number
- `department`: (e.g., Computer, Mechanical, Civil, Electrical)

**Example Row:**
`230180107045,Pavan Kumar,pavan@example.com,9876543210,Computer`

---

### B. Book CSV Format
**File Name Example:** `books_data.csv`  
**Required Headers (First Row):**
- `access_code`: Unique barcode/Access Code for the book (Primary Key)
- `title`: Name of the book
- `author`: Name of the author (Can be empty)
- `shelf_location`: Where the book is kept (e.g., A-1, CS-Section)

**Example Row:**
`BK-001,Introduction to Algorithms,Cormen,A-1`

## 🚀 2. Running the Import Commands

Open your terminal (PowerShell or CMD) in the project folder and run:

### Import Students
```powershell
python manage.py import_data students "C:\path\to\your\students.csv"
```

### Import Books
```powershell
python manage.py import_data books "C:\path\to\your\books.csv"
```

## ⚠️ Important Rules & Tips

1. **Duplicate Detection**: The system will automatically check if an `enrollment_id` or `access_code` already exists. It will skip duplicates and show a warning, so you don't have to worry about adding the same data twice.
2. **Exact Headers**: The first row of your CSV **must** match the headers mentioned above exactly (lowercase).
3. **Empty Values**: Ensure `enrollment_id` and `access_code` are never empty. Other fields like `author` can be blank if needed.
4. **Encoding**: If you have special characters, save your CSV with **UTF-8** encoding.

---
*For technical support, contact the system administrator.*
