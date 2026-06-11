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
for key in ["logged_in", "username", "role", "branch_id"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else None

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
# DASHBOARD (KPI)
# =====================================================
if menu == "Dashboard":

    st.title("📊 KPI Dashboard")

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

    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"
        df = pd.read_sql(base_query, engine, params={"branch_id": int(branch_id)})
    else:
        df = pd.read_sql(base_query, engine)

    row = df.iloc[0]

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

    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"
        df = pd.read_sql(base_query, engine, params={"branch_id": int(branch_id)})
    else:
        df = pd.read_sql(base_query, engine)

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
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO sales
                        (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
                        VALUES
                        (:branch, CURRENT_DATE, :name, :mobile, :product, :gross, 0, 'Open')
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
            "SELECT sale_id, name, mobile_number FROM sales WHERE branch_id=%(branch_id)s",
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
        st.success("Payment Added")
        st.rerun()

# =====================================================
# SALES REPORT
# =====================================================
elif menu == "Sales Report":

    st.title("📄 Sales Report")

    base_query = """
    SELECT s.*, b.branch_name
    FROM sales s
    JOIN branches b ON s.branch_id=b.branch_id
    """

    if role != "Super Admin":
        base_query += " WHERE s.branch_id=%(branch_id)s"
        df = pd.read_sql(base_query, engine, params={"branch_id": int(branch_id)})
    else:
        df = pd.read_sql(base_query, engine)

    st.dataframe(df)

# =====================================================
# PENDING PAYMENTS
# =====================================================
elif menu == "Pending Payments":

    st.title("⏳ Pending Payments")

    base_query = "SELECT * FROM sales WHERE pending_amount > 0"

    if role != "Super Admin":
        base_query += " AND branch_id=%(branch_id)s"
        df = pd.read_sql(base_query, engine, params={"branch_id": int(branch_id)})
    else:
        df = pd.read_sql(base_query, engine)

    st.dataframe(df)

# =====================================================
# PAYMENT DETAILS
# =====================================================
elif menu == "Payment Details":

    st.title("💳 Payment Details")

    if role == "Super Admin":
        df = pd.read_sql("SELECT * FROM payments", engine)
    else:
        df = pd.read_sql("""
            SELECT p.*
            FROM payments p
            JOIN sales s ON p.sale_id=s.sale_id
            WHERE s.branch_id=%(branch_id)s
        """, engine, params={"branch_id": int(branch_id)})

    st.dataframe(df)

# =====================================================
# PAYMENT ANALYSIS
# =====================================================
elif menu == "Payment Analysis":

    st.title("💳 Payment Method Analysis")

    if role == "Super Admin":
        df = pd.read_sql("""
            SELECT payment_method, SUM(amount_paid) total
            FROM payments
            GROUP BY payment_method
        """, engine)
    else:
        df = pd.read_sql("""
            SELECT p.payment_method, SUM(p.amount_paid) total
            FROM payments p
            JOIN sales s ON p.sale_id=s.sale_id
            WHERE s.branch_id=%(branch_id)s
            GROUP BY p.payment_method
        """, engine, params={"branch_id": int(branch_id)})

    st.bar_chart(df.set_index("payment_method"))
    st.dataframe(df)

# =====================================================
# OPEN VS CLOSE
# =====================================================
elif menu == "Open vs Close":

    st.title("📌 Open vs Close Sales")

    base_query = """
    SELECT status, COUNT(*) count
    FROM sales
    """

    if role != "Super Admin":
        base_query += " WHERE branch_id=%(branch_id)s"

    base_query += " GROUP BY status"

    if role != "Super Admin":
        df = pd.read_sql(base_query, engine, params={"branch_id": int(branch_id)})
    else:
        df = pd.read_sql(base_query, engine)

    st.bar_chart(df.set_index("status"))
    st.dataframe(df)

# =====================================================
# BRANCH PERFORMANCE
# =====================================================
elif menu == "Branch Performance":

    st.title("🏢 Branch Performance")

    df = pd.read_sql("""
        SELECT b.branch_name, SUM(s.gross_sales) total
        FROM sales s
        JOIN branches b ON s.branch_id=b.branch_id
        GROUP BY b.branch_name
    """, engine)

    st.bar_chart(df.set_index("branch_name"))
    st.dataframe(df)

# =====================================================
# SALES TREND
# =====================================================
elif menu == "Sales Trend":

    st.title("📈 Sales Trend")

    df = pd.read_sql("""
        SELECT date, SUM(gross_sales) total
        FROM sales
        GROUP BY date
        ORDER BY date
    """, engine)

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

    if option == "Top Sales":
        query = "SELECT * FROM sales ORDER BY gross_sales DESC LIMIT 10"
    elif option == "Open Sales":
        query = "SELECT * FROM sales WHERE status='Open'"
    elif option == "Closed Sales":
        query = "SELECT * FROM sales WHERE status='Close'"
    else:
        query = "SELECT * FROM sales WHERE pending_amount > 0"

    df = pd.read_sql(query, engine)
    st.dataframe(df)