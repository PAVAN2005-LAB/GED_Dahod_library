# API & Endpoints Documentation

This document provides a comprehensive overview of the API endpoints, reports endpoints, and page routes available in the **GECDahod Library Management System**.

---

## 1. Authentication API Endpoints (JWT)

These endpoints are used for generating, refreshing, and verifying JSON Web Tokens (JWT) for API authentication.

### `POST /api/token/`
- **Description:** Get JWT access and refresh tokens. Includes custom error handling for invalid credentials.
- **Payload:**
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- **Responses:**
  - `200 OK`: Returns the access and refresh tokens.
  - `401 Unauthorized`: `"Login Failed: Invalid username or password..."`

### `POST /api/token/refresh/`
- **Description:** Get a new access token using a valid refresh token.
- **Payload:**
  ```json
  {
    "refresh": "your_refresh_token"
  }
  ```
- **Responses:**
  - `200 OK`: Returns the new access token.

### `POST /api/token/verify/`
- **Description:** Verify whether a given token is still valid.
- **Payload:**
  ```json
  {
    "token": "your_access_or_refresh_token"
  }
  ```
- **Responses:**
  - `200 OK`: Token is valid.
  - `401 Unauthorized`: Token is invalid or expired.

### `GET /api/sitemap/`
- **Description:** Returns a structured JSON map of all available API endpoints, report downloads, and public web routes across the system. This provides a general overview (conceptual sitemap) of the project structure and routes dynamically.
- **Responses:**
  - `200 OK`: A JSON object with grouped endpoints mapped to their URLs.

### `POST /api/register/`
- **Description:** Create a new user account.
- **Payload:**
  ```json
  {
    "username": "new_user",
    "email": "user@email.com",
    "password": "secure_password"
  }
  ```
- **Responses:**
  - `201 Created`: User registered successfully.
  - `400 Bad Request`: Validation errors (e.g., missing fields or duplicate username).

### `POST /api/login/`
- **Description:** Alias for `/api/token/`. Get JWT access and refresh tokens.

### `POST /api/logout/`
- **Description:** Blacklists the provided refresh token to securely log the user out. Requires Bearer Token authorization.
- **Payload:**
  ```json
  {
    "refresh": "your_refresh_token"
  }
  ```
- **Responses:**
  - `205 Reset Content`: Successfully logged out.
  - `400 Bad Request`: Invalid or no token provided.

### `POST /api/update-password/`
- **Description:** Allows an authenticated user to change their password securely. Requires Bearer Token authorization.
- **Payload:**
  ```json
  {
    "old_password": "current_password",
    "new_password": "new_secure_password"
  }
  ```
- **Responses:**
  - `200 OK`: Password updated successfully.
  - `400 Bad Request`: Incorrect old password.

### `DELETE /api/delete/`
- **Description:** Deletes the authenticated user's account entirely. Requires Bearer Token authorization.
- **Responses:**
  - `204 No Content`: Account deleted successfully.

---

## 2. Report Download Endpoints

These endpoints are used to download data reports in `.xlsx` (Excel) format. 
**Note:** All report endpoints require the user to be a staff member (logged into the admin panel).

### `GET /admin/reports/`
- **Description:** Renders the main custom Reports Dashboard page inside the admin panel.

### `GET /admin/reports/entry-exit/`
- **Description:** Downloads the Entry-Exit log report. Includes duration spent in the library.
- **Query Parameters (Filters):**
  - `date_from` (Optional, format `YYYY-MM-DD`): Filter logs from this date.
  - `date_to` (Optional, format `YYYY-MM-DD`): Filter logs up to this date.
  - `department` (Optional): Filter by student department.
- **Response:** Excel (`.xlsx`) file download.

### `GET /admin/reports/book-issues/`
- **Description:** Downloads the Book Issues and transactions report.
- **Query Parameters (Filters):**
  - `date_from` (Optional, format `YYYY-MM-DD`): Filter issues from this date.
  - `date_to` (Optional, format `YYYY-MM-DD`): Filter issues up to this date.
  - `department` (Optional): Filter by student department.
  - `status` (Optional): Needs to be one of `returned`, `pending`, or `overdue`.
- **Response:** Excel (`.xlsx`) file download.

### `GET /admin/reports/overdue-students/`
- **Description:** Downloads a report specifically for students with overdue books.
- **Query Parameters (Filters):**
  - `date_from` (Optional, format `YYYY-MM-DD`): Filter based on issue date.
  - `date_to` (Optional, format `YYYY-MM-DD`): Filter based on issue date.
  - `department` (Optional): Filter by student department.
- **Response:** Excel (`.xlsx`) file download.

---

## 3. Web Views & Dashboard Endpoints

### `GET, POST /kiosk/`
- **Description:** The Kiosk scanner interface used at the library entrance for student check-in/check-out.
- **Methods:**
  - `GET`: Renders the Kiosk scanner page.
  - `POST`: Submits barcode data for entry/exit logging.
- **POST Payload (Form Data):**
  - `barcode`: The student's Enrollment ID.
- **Behavior:** 
  - Validates formatting (alphanumeric only).
  - Toggles between checking IN and checking OUT based on current status.

### `GET, POST /renew/`
- **Description:** Public portal for students to search active book issues and submit renewal requests to the admin.
- **Methods:**
  - `GET`: Renders the Book Renewal form.
  - `POST`: Either looks up the book details (`action=lookup`) or submits the official renewal request to the database (`action=submit`).
- **POST Payload (Form Data):**
  - `enrollment_id`: Student's ID.
  - `access_code`: The specific Book barcode.
  - `action`: `lookup` or `submit`.

### `GET /dashboard/`
- **Description:** Admin-only dashboard showing real-time statistics, including students currently inside the library and total historical visits.
- **Access Control:** Requires staff member permissions. Redirects to `/admin/login/` if unauthorized.
