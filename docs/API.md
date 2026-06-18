# UDMS API Reference

**Base URL:** `https://your-domain.com/api/v1`  
**Format:** All requests and responses use `application/json`  
**Authentication:** Bearer token (JWT) in `Authorization` header, except where noted

---

## Response Envelope

Every endpoint returns the same wrapper:

```json
{
  "success": true,
  "message": "Human-readable status",
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

`meta` is only present on paginated responses. On error, `data` is `null` and `success` is `false`.

---

## Error Codes

| HTTP | Code | Meaning |
|------|------|---------|
| 400 | `VALIDATION_ERROR` | Request body failed validation |
| 401 | `UNAUTHORIZED` | Missing or invalid access token |
| 401 | `TOKEN_EXPIRED` | Access token expired — refresh and retry |
| 403 | `FORBIDDEN` | Authenticated but insufficient role/permission |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Duplicate resource (e.g. username taken) |
| 422 | `UNPROCESSABLE` | Business rule violation |
| 423 | `ACCOUNT_LOCKED` | Too many failed logins — locked for 15 min |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |

```json
{
  "success": false,
  "message": "Invalid credentials",
  "data": null,
  "code": "UNAUTHORIZED"
}
```

---

## Role Hierarchy

| Role | Value | Description |
|------|-------|-------------|
| `PROVOST` | 0 | System administrator. Inherits all manager permissions when no active manager exists. |
| `DINING_MANAGER` | 1 | Manages dining operations, menus, expenses, customers. |
| `CUSTOMER` | 2 | Enrolled student — can register meals, view history. |
| `NON_CUSTOMER` | 3 | Unenrolled student — can submit enrollment requests. |

---

## Pagination

Paginated endpoints accept:

| Query Param | Type | Default | Description |
|-------------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `per_page` | int | 20 | Items per page (max 100) |

---

## Authentication

### POST `/auth/register`

Register a new account. Email verification is sent automatically.

**Access:** Public

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@university.edu",
  "password": "Secure@1234!",
  "full_name": "John Doe",
  "phone": "+8801712345678",
  "department": "Computer Science",
  "student_id": "CS-2024-001"
}
```

| Field | Required | Constraints |
|-------|----------|-------------|
| `username` | ✓ | 3–30 chars, alphanumeric + underscores |
| `email` | ✓ | Valid email, unique |
| `password` | ✓ | Min 8 chars, uppercase, lowercase, digit, special char |
| `full_name` | ✓ | 2–100 chars |
| `phone` | — | E.164 format |
| `department` | — | Max 100 chars |
| `student_id` | — | Max 50 chars |

**Response `201`:**
```json
{
  "success": true,
  "message": "Registration successful. Please verify your email.",
  "data": {
    "user_id": "usr_01HX3B2K9M",
    "username": "john_doe",
    "email": "john@university.edu",
    "role": "NON_CUSTOMER",
    "email_verified": false
  }
}
```

---

### POST `/auth/login`

Obtain access + refresh tokens.

**Access:** Public

**Request:**
```json
{
  "username": "john_doe",
  "password": "Secure@1234!"
}
```

`username` accepts either username or email address.

**Response `200`:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_01HX3B2K9M",
      "username": "john_doe",
      "email": "john@university.edu",
      "full_name": "John Doe",
      "role": "NON_CUSTOMER",
      "avatar_url": null,
      "email_verified": true,
      "is_active": true
    }
  }
}
```

The refresh token is set as an `HttpOnly; SameSite=Strict` cookie named `refresh_token`. It is not returned in the response body.

**Error `423` — Account locked:**
```json
{
  "success": false,
  "message": "Account locked due to too many failed attempts. Try again in 13 minutes.",
  "code": "ACCOUNT_LOCKED",
  "data": { "locked_until": "2025-03-15T10:45:00Z", "attempts": 5 }
}
```

---

### POST `/auth/refresh`

Exchange refresh token cookie for a new access token. Implements full rotation — the old refresh token is invalidated.

**Access:** Public (requires `refresh_token` cookie)

**Request:** No body needed.

**Response `200`:**
```json
{
  "success": true,
  "message": "Token refreshed",
  "data": {
    "access_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

---

### POST `/auth/logout`

Revoke the current refresh token.

**Access:** Authenticated

**Request:** No body needed.

**Response `200`:**
```json
{ "success": true, "message": "Logged out successfully", "data": null }
```

---

### POST `/auth/verify-email`

Confirm email address with OTP sent at registration.

**Access:** Public

**Request:**
```json
{
  "email": "john@university.edu",
  "otp": "482931"
}
```

OTPs are 6 digits, valid for 10 minutes, single-use.

**Response `200`:**
```json
{ "success": true, "message": "Email verified successfully", "data": null }
```

---

### POST `/auth/resend-verification`

Resend the email verification OTP. Rate-limited to 3 requests per hour.

**Access:** Public

**Request:**
```json
{ "email": "john@university.edu" }
```

**Response `200`:**
```json
{ "success": true, "message": "Verification email sent", "data": null }
```

---

### POST `/auth/forgot-password`

Initiate password reset. Always returns `200` to prevent email enumeration.

**Access:** Public

**Request:**
```json
{ "email": "john@university.edu" }
```

---

### POST `/auth/reset-password`

Complete password reset with OTP.

**Access:** Public

**Request:**
```json
{
  "email": "john@university.edu",
  "otp": "738201",
  "new_password": "NewSecure@5678!"
}
```

**Response `200`:**
```json
{ "success": true, "message": "Password reset successful", "data": null }
```

---

## Users

### GET `/users`

List all users with filtering and search.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number |
| `per_page` | int | Items per page |
| `search` | string | Search username, email, full name |
| `role` | string | Filter by role |
| `is_active` | bool | Filter by active status |
| `department` | string | Filter by department |
| `sort_by` | string | `created_at`, `username`, `full_name` (default: `created_at`) |
| `sort_order` | string | `asc`, `desc` (default: `desc`) |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": "usr_01HX3B2K9M",
      "username": "john_doe",
      "email": "john@university.edu",
      "full_name": "John Doe",
      "role": "CUSTOMER",
      "is_active": true,
      "email_verified": true,
      "department": "Computer Science",
      "student_id": "CS-2024-001",
      "phone": "+8801712345678",
      "avatar_url": null,
      "created_at": "2025-01-15T08:30:00Z",
      "last_login": "2025-03-14T11:22:00Z"
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 87, "total_pages": 5 }
}
```

---

### POST `/users`

Create a user directly (no email verification step).

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:** Same shape as `/auth/register`, plus:

```json
{
  "username": "new_student",
  "email": "new@university.edu",
  "password": "Temp@1234!",
  "full_name": "New Student",
  "role": "CUSTOMER"
}
```

`role` is optional; defaults to `NON_CUSTOMER`. `PROVOST` may assign any role. `DINING_MANAGER` may not create `PROVOST` accounts.

**Response `201`:** User object.

---

### GET `/users/{user_id}`

Get a single user's full profile.

**Access:** `PROVOST`, `DINING_MANAGER`, or the user themselves

**Response `200`:** User object (same as list item above).

---

### PATCH `/users/{user_id}`

Update user fields. Only provided fields are changed.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:**
```json
{
  "full_name": "John A. Doe",
  "department": "Software Engineering",
  "phone": "+8801798765432",
  "is_active": false
}
```

**Response `200`:** Updated user object.

---

### DELETE `/users/{user_id}`

Soft-delete a user account.

**Access:** `PROVOST` only

**Response `200`:**
```json
{ "success": true, "message": "User deleted", "data": null }
```

---

### POST `/users/{user_id}/assign-role`

Change a user's role.

**Access:** `PROVOST` only

**Request:**
```json
{ "role": "DINING_MANAGER" }
```

Valid transitions: `NON_CUSTOMER ↔ CUSTOMER`, `NON_CUSTOMER ↔ DINING_MANAGER`. `PROVOST` role can only be set by direct DB seeding.

**Response `200`:** Updated user object.

---

### POST `/users/{user_id}/suspend`

Suspend an active account.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:**
```json
{
  "reason": "Violation of dining conduct policy",
  "duration_days": 7
}
```

`duration_days` is optional — omit for indefinite suspension.

**Response `200`:**
```json
{ "success": true, "message": "User suspended", "data": { "suspended_until": "2025-03-22T00:00:00Z" } }
```

---

### POST `/users/{user_id}/activate`

Lift a suspension.

**Access:** `PROVOST`, `DINING_MANAGER`

**Response `200`:**
```json
{ "success": true, "message": "User activated", "data": null }
```

---

## Profile

### GET `/profile`

Get the authenticated user's own profile.

**Access:** Authenticated

**Response `200`:** Full user object.

---

### PATCH `/profile`

Update own profile fields.

**Access:** Authenticated

**Request:**
```json
{
  "full_name": "John Doe Jr.",
  "phone": "+8801712345678",
  "department": "Computer Science"
}
```

Username, email, and role cannot be changed through this endpoint.

---

### POST `/profile/change-password`

Change own password. Requires current password for verification.

**Access:** Authenticated

**Request:**
```json
{
  "current_password": "OldPass@1234!",
  "new_password": "NewPass@5678!",
  "confirm_password": "NewPass@5678!"
}
```

On success, all existing refresh tokens for the account are revoked.

**Response `200`:**
```json
{ "success": true, "message": "Password changed. Please log in again.", "data": null }
```

---

### POST `/profile/avatar`

Upload profile picture. Replaces any existing avatar.

**Access:** Authenticated  
**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Type | Constraints |
|-------|------|-------------|
| `avatar` | file | JPEG / PNG / WebP, max 2 MB |

**Response `200`:**
```json
{
  "success": true,
  "data": { "avatar_url": "/media/avatars/usr_01HX3B2K9M.webp" }
}
```

---

### DELETE `/profile/avatar`

Remove profile picture and revert to initials avatar.

**Access:** Authenticated

---

## Dining Operations

### GET `/dining/schedule`

Get the meal schedule (which meal types are served on which days).

**Access:** Authenticated

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "schedule": [
      {
        "day": "MONDAY",
        "meals": [
          { "type": "BREAKFAST", "start_time": "07:30", "end_time": "09:30", "enabled": true },
          { "type": "LUNCH",     "start_time": "12:00", "end_time": "14:30", "enabled": true },
          { "type": "DINNER",    "start_time": "19:00", "end_time": "21:00", "enabled": false }
        ]
      }
    ]
  }
}
```

---

### PUT `/dining/schedule`

Replace the full meal schedule.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:** Same structure as the GET response `data`.

---

### GET `/dining/menu`

Get the menu for a date range.

**Access:** Authenticated

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `from_date` | date | today | Start date `YYYY-MM-DD` |
| `to_date` | date | today | End date (max 30-day range) |

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "menus": [
      {
        "id": "mnu_01HX3C7P2N",
        "date": "2025-03-15",
        "meal_type": "LUNCH",
        "items": [
          { "name": "Rice", "description": "Steamed basmati", "is_available": true },
          { "name": "Chicken Curry", "description": null, "is_available": true }
        ],
        "note": "Special Eid menu"
      }
    ]
  }
}
```

---

### POST `/dining/menu`

Create a menu entry for a specific date and meal type.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:**
```json
{
  "date": "2025-03-15",
  "meal_type": "LUNCH",
  "items": [
    { "name": "Rice", "description": "Steamed basmati", "is_available": true },
    { "name": "Chicken Curry", "is_available": true }
  ],
  "note": "Special Eid menu"
}
```

Only one menu entry per (date, meal_type) pair is permitted.

**Response `201`:** Menu object.

---

### PATCH `/dining/menu/{menu_id}`

Update a menu entry.

**Access:** `PROVOST`, `DINING_MANAGER`

---

### DELETE `/dining/menu/{menu_id}`

Delete a menu entry.

**Access:** `PROVOST`, `DINING_MANAGER`

---

### GET `/dining/customers`

List all enrolled customers.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:** `page`, `per_page`, `search`, `sort_by`, `sort_order`

**Response `200`:** Paginated user objects.

---

### DELETE `/dining/customers/{user_id}`

Remove a customer from the dining program. Changes their role to `NON_CUSTOMER`.

**Access:** `PROVOST`, `DINING_MANAGER`

**Response `200`:**
```json
{ "success": true, "message": "Customer removed from dining program", "data": null }
```

---

## Meals

### GET `/meals/today`

Get meal availability for today with the authenticated customer's registration status for each.

**Access:** `CUSTOMER`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "date": "2025-03-15",
    "meals": [
      {
        "meal_type": "BREAKFAST",
        "serving_time": "07:30–09:30",
        "deadline": "2025-03-15T07:00:00Z",
        "deadline_passed": false,
        "registered": true,
        "registration_id": "reg_01HX4D8Q3P",
        "can_cancel": true,
        "menu": ["Bread", "Eggs", "Tea"]
      },
      {
        "meal_type": "LUNCH",
        "serving_time": "12:00–14:30",
        "deadline": "2025-03-15T11:00:00Z",
        "deadline_passed": false,
        "registered": false,
        "registration_id": null,
        "can_cancel": false,
        "menu": ["Rice", "Chicken Curry", "Dal"]
      }
    ]
  }
}
```

---

### POST `/meals/register`

Register for one or more meals.

**Access:** `CUSTOMER`

**Request:**
```json
{
  "date": "2025-03-15",
  "meal_types": ["LUNCH", "DINNER"]
}
```

Fails with `422` if the registration deadline for any requested meal has passed. Duplicate registrations for the same (date, meal_type) are silently ignored.

**Response `201`:**
```json
{
  "success": true,
  "message": "Registered for 2 meals",
  "data": {
    "registrations": [
      { "id": "reg_01HX4E9R4Q", "date": "2025-03-15", "meal_type": "LUNCH" },
      { "id": "reg_01HX4E9R4R", "date": "2025-03-15", "meal_type": "DINNER" }
    ]
  }
}
```

---

### DELETE `/meals/register/{registration_id}`

Cancel a meal registration.

**Access:** `CUSTOMER` (own registrations only)

Fails with `422` if the cancellation deadline has passed.

**Response `200`:**
```json
{ "success": true, "message": "Meal registration cancelled", "data": null }
```

---

### GET `/meals/history`

Get the authenticated customer's meal history.

**Access:** `CUSTOMER`

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `from_date` | date | Start date |
| `to_date` | date | End date |
| `meal_type` | string | Filter by meal type |
| `page` | int | Page number |
| `per_page` | int | Items per page |

**Response `200`:** Paginated list of registration objects.

---

### GET `/meals/history/{user_id}`

Get a specific customer's meal history.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:** Same as `/meals/history`.

---

### GET `/meals/summary`

Monthly meal summary for the authenticated customer.

**Access:** `CUSTOMER`

**Query Parameters:**

| Param | Type | Default |
|-------|------|---------|
| `year` | int | Current year |
| `month` | int | Current month |

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "year": 2025,
    "month": 3,
    "total_meals": 42,
    "by_type": {
      "BREAKFAST": 12,
      "LUNCH": 20,
      "DINNER": 10
    },
    "total_cost": 6300.00,
    "by_day": [
      { "date": "2025-03-01", "meals": ["BREAKFAST", "LUNCH"] },
      { "date": "2025-03-02", "meals": ["LUNCH"] }
    ]
  }
}
```

---

## Enrollment Requests

### POST `/requests`

Submit an enrollment request (NON_CUSTOMER only).

**Access:** `NON_CUSTOMER`

**Request:**
```json
{
  "reason": "I am a full-time resident student and would like to enroll in the dining program.",
  "semester": "Spring 2025",
  "hall_name": "Shahjalal Hall"
}
```

Only one pending request per user is allowed at a time.

**Response `201`:**
```json
{
  "success": true,
  "data": {
    "id": "req_01HX5F0S5R",
    "status": "PENDING",
    "submitted_at": "2025-03-15T09:00:00Z"
  }
}
```

---

### GET `/requests`

List enrollment requests.

**Access:** `PROVOST`, `DINING_MANAGER` — all requests. `NON_CUSTOMER`, `CUSTOMER` — own requests only.

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `status` | string | `PENDING`, `APPROVED`, `REJECTED` |
| `page` | int | Page number |
| `per_page` | int | Items per page |
| `search` | string | Search by student name or ID (manager only) |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": "req_01HX5F0S5R",
      "user": {
        "id": "usr_01HX3B2K9M",
        "username": "john_doe",
        "full_name": "John Doe",
        "student_id": "CS-2024-001",
        "department": "Computer Science"
      },
      "reason": "I am a full-time resident student...",
      "semester": "Spring 2025",
      "hall_name": "Shahjalal Hall",
      "status": "PENDING",
      "submitted_at": "2025-03-15T09:00:00Z",
      "reviewed_at": null,
      "reviewed_by": null,
      "review_note": null,
      "payment": null
    }
  ]
}
```

---

### GET `/requests/{request_id}`

Get a single enrollment request.

**Access:** `PROVOST`, `DINING_MANAGER`, or request owner.

---

### POST `/requests/{request_id}/approve`

Approve an enrollment request. Changes the applicant's role to `CUSTOMER`.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:**
```json
{ "note": "Welcome to the dining program!" }
```

**Response `200`:**
```json
{
  "success": true,
  "message": "Request approved. Student enrolled as customer.",
  "data": { "request_id": "req_01HX5F0S5R", "status": "APPROVED" }
}
```

---

### POST `/requests/{request_id}/reject`

Reject an enrollment request.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:**
```json
{ "note": "Incomplete documentation provided." }
```

---

### POST `/requests/{request_id}/payment`

Attach payment proof to an enrollment request (before or after approval).

**Access:** Request owner only  
**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `amount` | ✓ | Payment amount (decimal) |
| `transaction_id` | ✓ | Bank/mobile-banking transaction reference |
| `payment_method` | ✓ | `CASH`, `BANK_TRANSFER`, `MOBILE_BANKING` |
| `receipt` | — | Receipt image (JPEG/PNG, max 5 MB) |
| `note` | — | Free-text note |

**Response `201`:**
```json
{
  "success": true,
  "data": {
    "id": "pay_01HX6G1T6S",
    "amount": 1500.00,
    "transaction_id": "TRX20250315001",
    "payment_method": "MOBILE_BANKING",
    "receipt_url": "/media/receipts/pay_01HX6G1T6S.jpg",
    "submitted_at": "2025-03-15T10:00:00Z"
  }
}
```

---

## Expenses

### GET `/expenses`

List dining expense records.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `from_date` | date | Start date |
| `to_date` | date | End date |
| `category` | string | Expense category |
| `search` | string | Search by title or description |
| `page` | int | Page number |
| `per_page` | int | Items per page |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": "exp_01HX7H2U7T",
      "title": "March Grocery — Week 2",
      "category": "GROCERIES",
      "amount": 45000.00,
      "date": "2025-03-10",
      "description": "Rice, vegetables, oil",
      "receipt_url": "/media/receipts/exp_01HX7H2U7T.jpg",
      "created_by": {
        "id": "usr_02HX1A1B1C",
        "username": "diningmgr",
        "full_name": "Dining Manager"
      },
      "created_at": "2025-03-10T14:00:00Z"
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 34, "total_pages": 2 }
}
```

**Expense categories:** `GROCERIES`, `UTILITIES`, `SALARIES`, `MAINTENANCE`, `EQUIPMENT`, `MISCELLANEOUS`

---

### POST `/expenses`

Create an expense record.

**Access:** `PROVOST`, `DINING_MANAGER`  
**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `title` | ✓ | Short title |
| `category` | ✓ | Expense category |
| `amount` | ✓ | Amount (decimal, > 0) |
| `date` | ✓ | `YYYY-MM-DD` |
| `description` | — | Free-text description |
| `receipt` | — | Receipt image (JPEG/PNG, max 5 MB) |

**Response `201`:** Expense object.

---

### GET `/expenses/{expense_id}`

Get a single expense record.

**Access:** `PROVOST`, `DINING_MANAGER`

---

### PATCH `/expenses/{expense_id}`

Update an expense record.

**Access:** `PROVOST`, `DINING_MANAGER`

---

### DELETE `/expenses/{expense_id}`

Delete an expense record.

**Access:** `PROVOST` only

---

### GET `/expenses/summary`

Aggregate expense totals grouped by category for a date range.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:** `from_date`, `to_date`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "from_date": "2025-03-01",
    "to_date": "2025-03-31",
    "total": 285000.00,
    "by_category": {
      "GROCERIES": 180000.00,
      "SALARIES": 60000.00,
      "UTILITIES": 25000.00,
      "MAINTENANCE": 12000.00,
      "EQUIPMENT": 8000.00,
      "MISCELLANEOUS": 0.00
    }
  }
}
```

---

## Reports

### GET `/reports/overview`

High-level operational summary for a period.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | `monthly` | `weekly`, `monthly`, `yearly` |
| `year` | int | Current year | |
| `month` | int | Current month | Required when `period=monthly` |
| `week` | int | — | ISO week number; required when `period=weekly` |

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "period": "monthly",
    "year": 2025,
    "month": 3,
    "income": {
      "total": 125000.00,
      "from_payments": 125000.00,
      "customer_count": 83
    },
    "expenses": {
      "total": 285000.00,
      "by_category": { "GROCERIES": 180000.00, "SALARIES": 60000.00 }
    },
    "net": -160000.00,
    "meals": {
      "total_served": 2490,
      "by_type": { "BREAKFAST": 720, "LUNCH": 1020, "DINNER": 750 }
    },
    "trends": [
      { "date": "2025-03-01", "income": 4200.00, "expenses": 9800.00, "meals": 86 }
    ]
  }
}
```

---

### GET `/reports/income`

Detailed income breakdown.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:** `from_date`, `to_date`, `page`, `per_page`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "total": 125000.00,
    "records": [
      {
        "date": "2025-03-15",
        "student": "John Doe (CS-2024-001)",
        "amount": 1500.00,
        "method": "MOBILE_BANKING",
        "transaction_id": "TRX20250315001"
      }
    ]
  },
  "meta": { "page": 1, "per_page": 20, "total": 83 }
}
```

---

### GET `/reports/meal-count`

Per-day / per-meal-type head count.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:** `from_date`, `to_date`, `meal_type`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "total": 2490,
    "rows": [
      { "date": "2025-03-01", "BREAKFAST": 72, "LUNCH": 84, "DINNER": 68, "total": 224 }
    ]
  }
}
```

---

### GET `/reports/export`

Download a report as PDF or Excel.

**Access:** `PROVOST`, `DINING_MANAGER`

**Query Parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✓ | `overview`, `income`, `expenses`, `meal-count` |
| `format` | string | ✓ | `pdf`, `xlsx` |
| `from_date` | date | ✓ | |
| `to_date` | date | ✓ | |

**Response:** Binary file download with appropriate `Content-Type` and `Content-Disposition` headers.

---

## Audit Log

### GET `/audit`

Browse the system audit trail.

**Access:** `PROVOST` only

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number |
| `per_page` | int | Items per page |
| `user_id` | string | Filter by actor |
| `action` | string | Filter by action type |
| `resource` | string | Filter by resource type |
| `from_date` | date | Start date |
| `to_date` | date | End date |
| `search` | string | Full-text search |

**Response `200`:**
```json
{
  "success": true,
  "data": [
    {
      "id": "aud_01HX8I3V8U",
      "actor": {
        "id": "usr_02HX1A1B1C",
        "username": "diningmgr",
        "role": "DINING_MANAGER"
      },
      "action": "USER_SUSPENDED",
      "resource": "USER",
      "resource_id": "usr_01HX3B2K9M",
      "detail": "Suspended for 7 days: Violation of dining conduct policy",
      "ip_address": "192.168.1.50",
      "user_agent": "Mozilla/5.0 ...",
      "created_at": "2025-03-15T11:30:00Z"
    }
  ],
  "meta": { "page": 1, "per_page": 20, "total": 1420 }
}
```

**Common `action` values:** `USER_CREATED`, `USER_UPDATED`, `USER_SUSPENDED`, `USER_ACTIVATED`, `ROLE_CHANGED`, `PASSWORD_CHANGED`, `LOGIN_SUCCESS`, `LOGIN_FAILED`, `REQUEST_APPROVED`, `REQUEST_REJECTED`, `EXPENSE_CREATED`, `EXPENSE_DELETED`, `MENU_UPDATED`, `SCHEDULE_UPDATED`, `SETTINGS_UPDATED`

---

## Settings

### GET `/settings`

Get system configuration.

**Access:** `PROVOST`, `DINING_MANAGER`

**Response `200`:**
```json
{
  "success": true,
  "data": {
    "meal_rates": {
      "BREAKFAST": 50.00,
      "LUNCH": 100.00,
      "DINNER": 75.00
    },
    "registration_deadlines": {
      "BREAKFAST": { "hours_before": 1, "cutoff_time": "07:00" },
      "LUNCH":     { "hours_before": 1, "cutoff_time": "11:00" },
      "DINNER":    { "hours_before": 1, "cutoff_time": "18:00" }
    },
    "cancellation_deadline_hours": 2,
    "enrollment_fee": 500.00,
    "max_failed_login_attempts": 5,
    "account_lockout_minutes": 15,
    "otp_expiry_minutes": 10,
    "updated_at": "2025-03-01T00:00:00Z",
    "updated_by": "provost"
  }
}
```

---

### PUT `/settings`

Replace system configuration. Only `PROVOST` may change security settings.

**Access:** `PROVOST`, `DINING_MANAGER`

**Request:** Partial or full settings object. Unrecognised keys are ignored.

```json
{
  "meal_rates": {
    "BREAKFAST": 55.00,
    "LUNCH": 110.00,
    "DINNER": 80.00
  },
  "enrollment_fee": 600.00
}
```

Security fields (`max_failed_login_attempts`, `account_lockout_minutes`, `otp_expiry_minutes`) require `PROVOST` role even if the caller is also a `DINING_MANAGER`.

**Response `200`:** Full updated settings object.

---

## Rate Limits

| Endpoint group | Limit |
|----------------|-------|
| `POST /auth/login` | 10 requests / 5 min per IP |
| `POST /auth/forgot-password` | 3 requests / hour per email |
| `POST /auth/resend-verification` | 3 requests / hour per email |
| `POST /reports/export` | 10 requests / hour per user |
| All other endpoints | 300 requests / min per authenticated user |

Rate limit headers are included on every response:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 297
X-RateLimit-Reset: 1710500460
```

When the limit is exceeded the server returns `429` with a `Retry-After` header.

---

## Webhooks *(optional feature)*

If configured, the system can POST event notifications to a URL of your choice.

**Supported events:**

| Event | Trigger |
|-------|---------|
| `request.approved` | Enrollment request approved |
| `request.rejected` | Enrollment request rejected |
| `user.suspended` | User account suspended |
| `expense.created` | New expense recorded |

Each webhook delivery is a `POST` with the following body:

```json
{
  "event": "request.approved",
  "timestamp": "2025-03-15T12:00:00Z",
  "data": { }
}
```

Deliveries are retried up to 3 times with exponential backoff on non-`2xx` responses.

---

## Changelog

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0 | 2025-01-01 | Initial release |
