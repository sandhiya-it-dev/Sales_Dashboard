import streamlit as st
import pandas as pd
from sqlalchemy import text
from login import login
from project import get_connection

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Sales Dashboard", layout="wide")

engine = get_connection()

# ---------------- DB CHECK ----------------
try:
    with engine.connect():
        pass
except Exception as e:
    st.error(f"Database Error: {e}")
    st.stop()

# ---------------- SESSION INIT ----------------
for key in ["logged_in", "username", "role", "branch_id", "refresh_id"]:
    if key not in st.session_state:
        if key == "logged_in":
            st.session_state[key] = False
        elif key == "refresh_id":
            st.session_state[key] = 0
        else:
            st.session_state[key] = None

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    login()
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Sales Dashboard")
st.sidebar.success(f"{st.session_state.username} ({st.session_state.role})")

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

role = st.session_state.role
branch_id = st.session_state.branch_id
refresh_id = st.session_state.refresh_id  # reserved for future caching

# Safety: branch_id must be set for non-super-admin
if role != "Super Admin" and branch_id is None:
    st.error("branch_id not set for this user. Check users table / login().")
    st.stop()

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Dashboard",
        "Analytics",
        "Add Sales",
        "Add Payment",
        "Sales Report",
        "Pending Payments",
        "Payment Details",
        "Payment Analysis",
        "Open vs Close",
        "Branch Performance",
        "Sales Trend",
        "SQL Queries"
    ]
)

# =====================================================
# DATA LOADER FUNCTIONS
# =====================================================

def load_kpi(engine, role, branch_id):
    base_query = """
    SELECT
        COALESCE(SUM(gross_sales),0) total_sales,
        COALESCE(SUM(received_amount),0) total_received,
        COALESCE(SUM(pending_amount),0) total_pending,
        ROUND(
            COALESCE(
                SUM(pending_amount)*100.0 /
                NULLIF(SUM(gross_sales),0),
            0),2
        ) pending_percent
    FROM sales
    """
    params = {}
    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"
        params["branch_id"] = int(branch_id)
    return pd.read_sql(base_query, engine, params=params if params else None)

def load_analytics(engine, role, branch_id):
    base_query = """
    SELECT
        COUNT(*) total_sales,
        SUM(gross_sales) revenue,
        SUM(received_amount) received,
        SUM(pending_amount) pending,
        COUNT(CASE WHEN status='Open' THEN 1 END) open_sales,
        COUNT(CASE WHEN status='Close' THEN 1 END) close_sales
    FROM sales
    """
    params = {}
    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"
        params["branch_id"] = int(branch_id)
    return pd.read_sql(base_query, engine, params=params if params else None)

def load_sales_debug(engine):
    return pd.read_sql("""
        SELECT
            sale_id,
            gross_sales,
            received_amount,
            pending_amount,
            status
        FROM sales
        ORDER BY sale_id DESC
        LIMIT 10
    """, engine)

def load_sales_report(engine, role, branch_id):
    base_query = """
    SELECT s.*, b.branch_name
    FROM sales s
    JOIN branches b ON s.branch_id=b.branch_id
    """
    params = {}
    if role != "Super Admin":
        base_query += " WHERE s.branch_id=%(branch_id)s"
        params["branch_id"] = int(branch_id)
    return pd.read_sql(base_query, engine, params=params if params else None)

def load_pending_payments(engine, role, branch_id):
    base_query = "SELECT * FROM sales WHERE pending_amount > 0"
    params = {}
    if role != "Super Admin":
        base_query += " AND branch_id=%(branch_id)s"
        params["branch_id"] = int(branch_id)
    return pd.read_sql(base_query, engine, params=params if params else None)

def load_payment_details(engine, role, branch_id):
    if role == "Super Admin":
        return pd.read_sql("SELECT * FROM payments", engine)
    return pd.read_sql("""
        SELECT p.*
        FROM payments p
        JOIN sales s ON p.sale_id=s.sale_id
        WHERE s.branch_id=%(branch_id)s
    """, engine, params={"branch_id": int(branch_id)})

def load_payment_analysis(engine, role, branch_id):
    if role == "Super Admin":
        return pd.read_sql("""
            SELECT payment_method, SUM(amount_paid) total
            FROM payments
            GROUP BY payment_method
        """, engine)
    return pd.read_sql("""
        SELECT p.payment_method, SUM(p.amount_paid) total
        FROM payments p
        JOIN sales s ON p.sale_id=s.sale_id
        WHERE s.branch_id=%(branch_id)s
        GROUP BY p.payment_method
    """, engine, params={"branch_id": int(branch_id)})

def load_open_vs_close(engine, role, branch_id):
    base_query = """
    SELECT status, COUNT(*) count
    FROM sales
    """
    params = {}
    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"
        params["branch_id"] = int(branch_id)
    base_query += " GROUP BY status"
    return pd.read_sql(base_query, engine, params=params if params else None)

def load_branch_performance(engine):
    return pd.read_sql("""
        SELECT b.branch_name, SUM(s.gross_sales) total
        FROM sales s
        JOIN branches b ON s.branch_id=b.branch_id
        GROUP BY b.branch_name
    """, engine)

def load_sales_trend(engine, role, branch_id):
    base_query = """
        SELECT date, SUM(gross_sales) total
        FROM sales
    """
    params = {}
    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"
        params["branch_id"] = int(branch_id)
    base_query += """
        GROUP BY date
        ORDER BY date
    """
    return pd.read_sql(base_query, engine, params=params if params else None)

def load_sql_query(engine, option, role, branch_id):
    params = {}
    if option == "Top Sales":
        if role == "Super Admin":
            query = "SELECT * FROM sales ORDER BY gross_sales DESC LIMIT 10"
        else:
            query = """
                SELECT * FROM sales
                WHERE branch_id=%(branch_id)s
                ORDER BY gross_sales DESC
                LIMIT 10
            """
            params["branch_id"] = int(branch_id)
    elif option == "Open Sales":
        query = "SELECT * FROM sales WHERE status='Open'"
        if role != "Super Admin":
            query += " AND branch_id=%(branch_id)s"
            params["branch_id"] = int(branch_id)
    elif option == "Closed Sales":
        query = "SELECT * FROM sales WHERE status='Close'"
        if role != "Super Admin":
            query += " AND branch_id=%(branch_id)s"
            params["branch_id"] = int(branch_id)
    else:  # Pending
        query = "SELECT * FROM sales WHERE pending_amount > 0"
        if role != "Super Admin":
            query += " AND branch_id=%(branch_id)s"
            params["branch_id"] = int(branch_id)

    return pd.read_sql(query, engine, params=params if params else None)

# =====================================================
# DASHBOARD (KPI)
# =====================================================
if menu == "Dashboard":
    st.title("📊 KPI Dashboard")

    df = load_kpi(engine, role, branch_id)
    row = df.iloc[0]

    st.caption("🕐 Data refreshed at: " + pd.Timestamp.now().strftime("%d %b %Y, %I:%M %p"))
    st.dataframe(df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"₹{row['total_sales']:,.0f}")
    c2.metric("Received", f"₹{row['total_received']:,.0f}")
    c3.metric("Pending", f"₹{row['total_pending']:,.0f}")
    c4.metric("Pending %", f"{row['pending_percent']}%")

# =====================================================
# ANALYTICS
# =====================================================
elif menu == "Analytics":
    st.title("📈 Business Analytics")

    df = load_analytics(engine, role, branch_id)
    st.write("Data refreshed at:", pd.Timestamp.now())

    st.subheader("Summary")
    st.dataframe(df)

# =====================================================
# ADD SALES
# =====================================================
elif menu == "Add Sales":
    st.title("➕ Add Sales")

    if role == "Super Admin":
        branches = pd.read_sql("SELECT * FROM branches", engine)
        branch = st.selectbox(
            "Branch",
            branches["branch_id"],
            format_func=lambda x: branches.loc[branches["branch_id"] == x, "branch_name"].iloc[0]
        )
    else:
        branch = branch_id
        st.info(f"Branch ID: {branch}")

    name = st.text_input("Customer Name")
    mobile = st.text_input("Mobile Number")
    product = st.text_input("Product Name")
    gross = st.number_input("Gross Sales", min_value=0.0)

    if st.button("Save Sale"):
        if len(mobile) != 10:
            st.error("Invalid mobile number")
        else:
            # IMPORTANT: do NOT insert into pending_amount (generated column)
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO sales
                        (
                           branch_id,
                           date,
                           name,
                           mobile_number,
                           product_name,
                           gross_sales,
                           received_amount,
                           status
                        )
                        VALUES
                        (
                            :branch,
                            CURRENT_DATE,
                            :name,
                            :mobile,
                            :product,
                            :gross,
                            0,
                            'Open'
                        )
                    """),
                    {
                        "branch": int(branch),
                        "name": name,
                        "mobile": mobile,
                        "product": product,
                        "gross": gross
                    }
                )
            st.success("Sale Added")
            st.session_state.refresh_id += 1
            st.rerun()

# =====================================================
# ADD PAYMENT
# =====================================================
elif menu == "Add Payment":
    st.title("💰 Add Payment")

    if role == "Super Admin":
        sales = pd.read_sql(
            "SELECT sale_id, name, mobile_number FROM sales",
            engine
        )
    else:
        sales = pd.read_sql(
            """
            SELECT sale_id, name, mobile_number
            FROM sales
            WHERE branch_id=%(branch_id)s
            """,
            engine,
            params={"branch_id": int(branch_id)}
        )

    sale_id = st.selectbox(
        "Sale ID",
        sales["sale_id"],
        format_func=lambda x: f"ID {x} - {sales.loc[sales['sale_id']==x,'name'].values[0]}"
    )

    amount = st.number_input("Amount", min_value=0.0)
    method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])

    if st.button("Add Payment"):
        try:
            # 1) Insert payment in a transaction (trigger runs here)
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO payments
                        (sale_id, payment_date, amount_paid, payment_method)
                        VALUES
                        (:sale_id, CURRENT_DATE, :amount, :method)
                    """),
                    {
                        "sale_id": int(sale_id),
                        "amount": amount,
                        "method": method
                    }
                )

            # 2) Immediately check what sales row looks like NOW
            sale_check = pd.read_sql(
                """
                SELECT
                    sale_id,
                    gross_sales,
                    received_amount,
                    pending_amount,
                    status
                FROM sales
                WHERE sale_id=%(sale_id)s
                """,
                engine,
                params={"sale_id": int(sale_id)}
            )

            st.subheader("Sales Row Immediately After Payment Insert")
            st.dataframe(sale_check)

            st.success("Payment Added Successfully")

            # 3) Bump refresh_id and rerun entire app
            st.session_state.refresh_id += 1
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

            payment_check = pd.read_sql(
                """
                SELECT *
                FROM payments
                WHERE sale_id=%(sale_id)s
                ORDER BY payment_id DESC
                LIMIT 5
                """,
                engine,
                params={"sale_id": int(sale_id)}
            )

            st.subheader("Latest Payments (on error)")
            st.dataframe(payment_check)

            sale_check = pd.read_sql(
                """
                SELECT
                    sale_id,
                    gross_sales,
                    received_amount,
                    pending_amount,
                    status
                FROM sales
                WHERE sale_id=%(sale_id)s
                """,
                engine,
                params={"sale_id": int(sale_id)}
            )

            st.subheader("Sales Record After Payment (on error)")
            st.dataframe(sale_check)

# =====================================================
# SALES REPORT
# =====================================================
elif menu == "Sales Report":
    st.title("📄 Sales Report")
    df = load_sales_report(engine, role, branch_id)
    st.dataframe(df)

# =====================================================
# PENDING PAYMENTS
# =====================================================
elif menu == "Pending Payments":
    st.title("⏳ Pending Payments")
    df = load_pending_payments(engine, role, branch_id)
    st.dataframe(df)

# =====================================================
# PAYMENT DETAILS
# =====================================================
elif menu == "Payment Details":
    st.title("💳 Payment Details")
    df = load_payment_details(engine, role, branch_id)
    st.dataframe(df)

# =====================================================
# PAYMENT ANALYSIS
# =====================================================
elif menu == "Payment Analysis":
    st.title("💳 Payment Method Analysis")
    df = load_payment_analysis(engine, role, branch_id)
    st.bar_chart(df.set_index("payment_method"))
    st.dataframe(df)

# =====================================================
# OPEN VS CLOSE
# =====================================================
elif menu == "Open vs Close":
    st.title("📌 Open vs Close Sales")
    df = load_open_vs_close(engine, role, branch_id)
    st.bar_chart(df.set_index("status"))
    st.dataframe(df)

# =====================================================
# BRANCH PERFORMANCE
# =====================================================
elif menu == "Branch Performance":
    st.title("🏢 Branch Performance")
    df = load_branch_performance(engine)
    st.bar_chart(df.set_index("branch_name"))
    st.dataframe(df)

# =====================================================
# SALES TREND
# =====================================================
elif menu == "Sales Trend":
    st.title("📈 Sales Trend")
    df = load_sales_trend(engine, role, branch_id)
    st.line_chart(df.set_index("date"))
    st.dataframe(df)

# =====================================================
# SQL QUERIES
# =====================================================
elif menu == "SQL Queries":
    st.title("🧠 SQL Queries")
    option = st.selectbox("Choose Query", [
        "Top Sales",
        "Open Sales",
        "Closed Sales",
        "Pending"
    ])
    df = load_sql_query(engine, option, role, branch_id)
    st.dataframe(df)