# Sales Dashboard Project

## Overview

This project is an offline sales management dashboard built with Streamlit, PostgreSQL, SQLAlchemy, and Pandas. It supports login-based access, branch-level administration, KPI reporting, payment tracking, SQL-based reporting, and automatic sales status updates using a PostgreSQL trigger.

The application is designed to run fully on a local machine without cloud deployment, making it suitable for learning, demos, portfolio projects, and academic submissions.

## Tech Stack

- **Frontend:** Streamlit
- **Backend Logic:** Python
- **Database:** PostgreSQL
- **ORM / Connectivity:** SQLAlchemy
- **Data Handling:** Pandas
- **Environment Variables:** python-dotenv
- **Database Logic:** PL/pgSQL Trigger

## Project Structure

```text
project_folder/
├── app.py              # Main Streamlit dashboard
├── login.py            # Login page logic
├── project.py          # Database connection logic
├── .env                # Stores DB_URL for local database connection
├── requirements.txt
└── README.md
```

## Features

- User login with session-based authentication
- Role-based access control for Super Admin and Admin users
- Add sales records
- Add payment entries
- KPI dashboard with total sales, received amount, pending amount, and pending percentage
- Sales and payment reporting pages
- Branch-wise and date-wise analytics
- SQL reporting section for predefined queries
- Automatic payment status update using PostgreSQL trigger

## Role-Based Access

The project supports two user roles:

- **Super Admin** – can access data from all branches
- **Admin** – can access only the assigned branch data

This branch-level filtering is applied throughout the dashboard queries.

## Database Tables

### 1. branches
Stores branch master data.

- `branch_id` – Primary Key
- `branch_name`
- `branch_admin_name`

### 2. sales
Stores each sale record.

- `sale_id` – Primary Key
- `branch_id` – Foreign Key
- `date`
- `name` – Customer name
- `mobile_number`
- `product_name`
- `gross_sales`
- `received_amount`
- `pending_amount` – Generated column
- `status` – Open / Close

### 3. users
Stores login users.

- `user_id`
- `username`
- `password`
- `branch_id`
- `role`
- `email`

### 4. payments
Stores payment transactions.

- `payment_id`
- `sale_id`
- `payment_date`
- `amount_paid`
- `payment_method`

Supported payment methods:

- Cash
- UPI
- Card

## Trigger Logic

The PostgreSQL trigger function `update_sales_payment()` automatically updates the related sales record whenever a new payment is inserted.

It performs the following actions:

- Recalculates `received_amount`
- Updates `pending_amount`
- Changes `status` to `Close` when the pending amount becomes zero or less
- Keeps the sale as `Open` if payment is still pending

This ensures that key business logic is handled directly in the database.

## How the Application Works

### Database Connection

The `project.py` file loads the database URL from the `.env` file and creates a SQLAlchemy engine.

```python
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    db_url = os.getenv("DB_URL")
    engine = create_engine(db_url)
    return engine
```

### Login Flow

- User enters username and password using the Streamlit form
- App validates the credentials against the `users` table
- If valid, user details are stored in `st.session_state`
- The dashboard reloads and shows the main menu

Stored session values include:

- `logged_in`
- `user_id`
- `username`
- `role`
- `branch_id`

### Main Dashboard Pages

The sidebar includes the following pages:

- Dashboard
- Analytics
- Add Sales
- Add Payment
- Sales Report
- Pending Payments
- Payment Details
- Payment Analysis
- Open vs Close
- Branch Performance
- Sales Trend
- SQL Queries

## Installation and Setup

### Step 1: Install PostgreSQL

Install PostgreSQL locally and create a database:

```sql
CREATE DATABASE sales_dashboard;
```

### Step 2: Run SQL Script

Execute your schema and sample data SQL script in PostgreSQL. This should create:

- Tables
- Constraints
- Trigger function
- Trigger
- Sample data

### Step 3: Create `.env` File

Add the database connection string in your project folder:

```env
DB_URL=postgresql://postgres:yourpassword@localhost:5432/sales_dashboard
```

### Step 4: Install Required Packages

```bash
pip install streamlit pandas sqlalchemy psycopg2-binary python-dotenv
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

## Example Login

Use one of the inserted users from your sample data.

Example:

- **Admin User**
  - Username: `user1`
  - Password: `admin123`

- **Super Admin User**
  - Username: `user5`
  - Password: `admin123`

## Example User Flow

### Admin User

1. Logs in
2. Sees only assigned branch data
3. Adds a new sale
4. Adds a payment
5. Trigger updates the sale status and pending amount
6. Dashboard reflects the latest changes

### Super Admin User

1. Logs in
2. Sees all branch data
3. Compares branch performance
4. Reviews payment analysis
5. Checks sales trends and open vs close metrics

## Advantages

- Demonstrates integration of Python, SQL, and Streamlit
- Shows practical database-driven application development
- Includes role-based access control
- Uses PostgreSQL trigger logic for automation
- Easy to run offline on a local machine

