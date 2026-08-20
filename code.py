#1. Importing libraries
import streamlit as st

import pandas as pd

import psycopg2 
#2. Importing your own functions
from db import get_connection

from db import get_all_branches, get_branch_name , get_all_products

from datetime import date

#3. Streamlit page configuration
st.set_page_config(
    page_title="Sales Management System",
    page_icon="📊",
    layout="wide"
)





# -----------------------------
# 4.SESSION STATE
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "branch_id" not in st.session_state:
    st.session_state.branch_id = None

if "email" not in st.session_state:
    st.session_state.email = ""

# =========================
# LOGIN PAGE
# =========================

if not st.session_state.logged_in:

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 700px !important;
            margin: 0 auto;
            padding-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title('Sales Management System')

    st.title('Welcome to the login page')

    st.html("""
    <div style="
        background: linear-gradient(135deg, #4FC3F7, #29B6F6);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.3);
    ">
        Please login to check the Customer Sales Report.
    </div>
    """)
    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT username, password, branch_id, role, email
            FROM users
            WHERE username = %s
            AND password = %s
            
            """,
            (username,password)
        )

        user = cur.fetchone()

        st.write("User result:", user)

        cur.close()
        conn.close()

        if user:

            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.branch_id = user[2]
            st.session_state.role = user[3]
            st.session_state.email = user[4]
            
        

            st.rerun()

        else:

            st.error("Invalid username or password")

# =========================
# AFTER LOGIN
# =========================

else:

    role = st.session_state["role"]
    branch_id = st.session_state["branch_id"]
    

    with st.sidebar:

        st.title("Navigation")

        option = st.radio ( 'Go to',
                        [
                "📊 Dashboard & Reports",
                "🗒️ Data Entry Workspace",
                "⚙️ Advanced SQL Engine"])

        st.markdown("---")

        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role}")

        if st.button("🚪 Logout",use_container_width=True):

            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = ""
            st.session_state.branch_id = None
            st.session_state.email = ""

            st.rerun()

    # =========================
    # MAIN PAGE
    # =========================

    # ==================================
    # DASHBOARD
    # ==================================

    if option == "📊 Dashboard & Reports":

        st.markdown(
        "<h1 style='text-align: left;'>📊 Student Enrollment Dashboard</h1>",
        unsafe_allow_html=True
    )

        st.subheader("🔍 Filter Controls")

        

        col1, col2,col3,col4=st.columns(4)  

        conn = get_connection()
        cur = conn.cursor()

        with col1:
            if role == "Super Admin":

                branch_list = ["All Branches"] + get_all_branches()

                branch = st.selectbox(
                    "🏢 Branch",
                    branch_list
                )

            else:

                branch = get_branch_name(branch_id)

                st.selectbox(
                    "🏢 Branch",
                    [branch],
                    disabled=True
                )

                        




        with col2:
            cur.execute("""
                    SELECT DISTINCT product_name
                FROM customer_sales
                ORDER BY product_name
                """)

            products = cur.fetchall()

            product_list = ["All Products"] + [row[0] for row in products]

            product = st.selectbox(
                    "📚 Product Name",
                        product_list
                    )

        with col3:
            start_date = st.date_input(
                        "Start Date",
                        value=date(2024, 1, 1),
                        
                    )

        with col4:
            end_date = st.date_input(
                                "End Date",
                                value=date(2024, 12, 30), 
                                min_value=start_date
                            )

# -----------------------------
# 💶 FINANCIAL SUMMARY
# -----------------------------

        st.subheader("💶 Financial Summary")

        # Base SQL query
        query = """
            SELECT
                COUNT(cs.sale_id),
                COALESCE(SUM(cs.gross_sales), 0),
                COALESCE(SUM(cs.received_amount), 0),
                COALESCE(SUM(cs.pending_amount), 0)
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
                
        """

        # Empty lists
        conditions = []
        values = []

        # Branch filter
        if branch != "All Branches":
            conditions.append("b.branch_name = %s")
            values.append(branch)

        # Product filter
        if product != "All Products":
            conditions.append("cs.product_name = %s")
            values.append(product)

        # Start Date filter
        if start_date:
            conditions.append("cs.date >= %s")
            values.append(start_date)

        # End Date filter
        if end_date:
            conditions.append("cs.date <= %s")
            values.append(end_date)

        # Add WHERE conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Execute query
        cur.execute(query, values)

        # Fetch result
        total_sales, total_gross, total_received, total_pending = cur.fetchone()

        # -----------------------------
        # DISPLAY FINANCIAL SUMMARY
        # -----------------------------

        col1, col2 = st.columns(2)

        col1.metric("🧾 Total Sales",total_sales)

        col2.metric( "💰 Gross Sales",f"₹{total_gross:,.2f}" )

        col1, col2 = st.columns(2)

        col1.metric("💵 Received",f"₹{total_received:,.2f}")

        col2.metric("⏳ Pending", f"₹{total_pending:,.2f}")

        # -----------------------------
        # 📚 BRANCH COURSE RECORD SUMMARY
        # -----------------------------
        
        st.subheader("📋 Branch Course Record Summary")
        
        detail_query = """
            SELECT
                cs.sale_id,
                b.branch_name,
                cs.customer_name,
                cs.mobile_number,
                cs.product_name,
                cs.date,
                cs.gross_sales,
                cs.received_amount,
                cs.pending_amount,
                cs.status
                
                
               
            FROM customer_sales cs
            JOIN branches b
                ON cs.branch_id = b.branch_id
                
                
        """

        if conditions:
            detail_query += " WHERE " + " AND ".join(conditions)

        detail_query += " ORDER BY cs.sale_id ASC"

        cur.execute(detail_query, values)

        records = cur.fetchall()

        columns = [
            "Sale ID",
            "Branch Name",
            "Student Name",
            "Mobile Number",
           "Product Name",
            "Joining Date",
            "Gross Sales",
            "Received Amount",
            "Pending Amount",
            "Status"
        ]

        df = pd.DataFrame(records, columns=columns)

        if df.empty:
            st.info("No data available for the selected filters.")
        else:
            st.dataframe(df, use_container_width=True)



    # ==================================
    # DATA ENTRY
    # ==================================

    elif option=="🗒️ Data Entry Workspace":
        st.title('🗒️ Operations Record Creator')

        tab1, tab2 = st.tabs(
            ["Add New Sales Entry", "Log Payment Split Details"]
        )

        with tab1:
            st.write("New Sale Generation")

            

            if role == "Super Admin":

                branch_list = get_all_branches()

                branch = st.selectbox(
                    "🏢 Select Target Branch",
                    branch_list
                )

            else:

                branch = get_branch_name(branch_id)

                st.selectbox(
                    "🏢 Select Target Branch",
                    [branch],
                    disabled=True
                             )
                
            col1,col2=st.columns(2)
            with col1:
                customer_name = st.text_input("Student Name")
            with col2:
                
                products = get_all_products()

                product_name = st.selectbox(
                    "Select Product Name",
                    products
                )
            col1,col2=st.columns(2)
            with col1:  
                customer_phone = st.text_input("Mobile Number")
            with col2:
                joining_date=st.text_input('Joining Date')
                conn = get_connection()
                cur = conn.cursor()

                cur.execute("""
                    SELECT gross_sales
                    FROM customer_sales
                    WHERE product_name = %s
                    LIMIT 1
                """, (product_name,))

                result = cur.fetchone()

                cur.close()
                conn.close()

                if result:
                    gross_sales = float(result[0])
                else:
                    gross_sales = 0.0

                st.number_input(
                    "💰 Gross Sales",
                    value=gross_sales,
                    disabled=False
                )
                

            if st.button("Publish Sale Entry"):

                if customer_name == "":
                    st.error("Please enter Student Name")

                elif customer_phone == "":
                    st.error("Please enter Mobile Number")

                elif gross_sales <= 0:
                    st.error("Please enter Gross Sales")

                else:

                    conn = get_connection()
                    cur = conn.cursor()

                    cur.execute("""
                        SELECT branch_id
                        FROM branches
                        WHERE branch_name = %s
                    """, (branch,))

                    branch_result = cur.fetchone()

                    if branch_result is None:

                        st.error("Branch not found")

                    else:

                        branch_id_value = branch_result[0]

                        cur.execute("""
                            INSERT INTO customer_sales
                            (
                                branch_id,
                                date,
                                customer_name,
                                mobile_number,
                                product_name,
                                gross_sales,
                                received_amount,
                                
                                status
                            )
                            VALUES (%s, %s, %s, %s, %s, %s,  %s, %s)
                        """, (
                            branch_id_value,
                            joining_date,
                            customer_name,
                            customer_phone,
                            product_name,
                            gross_sales,
                            0,
                            
                            "Open"
                        ))

                        conn.commit()

                        st.success("✅ Sale entry published successfully!")

                        cur.close()
                        conn.close()  

        with tab2:

            st.write("Post Payment Installment Split")

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                                SELECT
                                    sale_id,
                                    customer_name,
                                    mobile_number,
                                    product_name,
                                    pending_amount
                                FROM customer_sales
                                WHERE status = 'Open'
                                ORDER BY sale_id
                            """)

            sales = cur.fetchall()
            if not sales:
                st.info("No open sales available for payment.")

            else:

            

                sale_list = [
                     f"{row[0]} - {row[1]} - {row[2]} - {row[3]} - Pending ₹{row[4]:,.2f}"
                          for row in sales
]

                sale_details = st.selectbox(
                "🧾 Select Target Active Sale Asset",
                sale_list
                        )
                sale_id = int(sale_details.split(" - ")[0])


            
                payment_method = st.selectbox("💳 Payment Collection Channel",
                                                    ["Cash", "UPI", "Card"]
                                                )
                collected_amount = st.number_input(
                                "Collected Split Amount Balance",
                                min_value=0.0,
                                    step=100.0
                                            ) 
                payment_date=st.date_input('Payment Date')

            if st.button('Apply Payment Allocation'):

                if collected_amount <= 0:
                    st.error("Please enter a valid payment amount")

                else:

                    cur.execute("""
                        SELECT pending_amount
                        FROM customer_sales
                        WHERE sale_id = %s
                    """, (sale_id,))

                    pending_amount = cur.fetchone()[0]

                    if collected_amount > pending_amount:
                        st.error(
                            f"Payment cannot be greater than pending amount ₹{pending_amount:,.2f}"
                        )

                    else:

                        cur.execute("""
                            INSERT INTO payment_splits
                            (
                                sale_id,
                                payment_date,
                                amount_paid,
                                payment_method
                            )
                            VALUES (%s, %s, %s, %s)
                        """, (
                            sale_id,
                            payment_date,
                            collected_amount,
                            payment_method
                        ))

                        # 2. Get total amount received for this sale
                        cur.execute("""
                            SELECT COALESCE(SUM(amount_paid), 0)
                            FROM payment_splits
                            WHERE sale_id = %s
                        """, (sale_id,))

                        total_received = cur.fetchone()[0]

                        

                        # 3. Get gross sales
                        cur.execute("""
                            SELECT gross_sales
                            FROM customer_sales
                            WHERE sale_id = %s
                        """, (sale_id,))

                        gross_sales = cur.fetchone()[0]

                        

                        # 4. Check whether fully paid
                        if total_received == gross_sales:
                            status = "Close"
                        else:
                            status = "Open"

                        # 5. Update customer_sales
                        cur.execute("""
                            UPDATE customer_sales
                            SET received_amount = %s,
                                status = %s
                            WHERE sale_id = %s
                        """, (
                            total_received,
                            status,
                            sale_id
                        ))

                        # 6. Save everything
                        conn.commit()

                        st.success("Payment recorded successfully!")

                        
    # ==================================
    # SQL ENGINE
    # ==================================        

    elif option=="⚙️ Advanced SQL Engine":
        st.title('💻 Live SQL Business Analytics Engine')

        st.write('Select and execute any of the 20 mandatory verification queries to audit records from your tables')

        questions= ['1. Retrieve all records from the customer_sales table.',
                   '2. Retrieve all records from the branches table.',
                   '3. Retrieve all records from the payment_splits table.',
                   "4. Display all sales with status = 'Open'.",
                   '5.Calculate the total gross sales across all branches.',
                   '6. Calculate the total received amount across all sales.',
                   '7. Calculate the total pending amount across all sales.',
                   '8. Count the total number of sales per branch.',
                   '9. Retrieve sales details along with the branch name.',
                   '10. Retrieve sales details along with total payment received (using payment_splits).',
                   '11. Display sales along with payment method used.',
                   '12. Retrieve sales along with branch admin name.',
                   '13. Find sales where the pending amount is greater than 5000.',
                   '14. Retrieve top 3 highest gross sales.',
                   '15. Find the branch with highest total gross sales.']
        
        question=st.selectbox('Choose targeted predefined operational queries',
                            questions)

        conn = get_connection()
        cur = conn.cursor()

        query = ""
        params = ()
                

        if role == "Super Admin":
            branch_condition = ""
        else:
            branch_condition = "AND cs.branch_id = %s"
            params = (branch_id,)

        
                    
        if question == questions[0]:
            query = f"""
                        SELECT *
                        FROM customer_sales cs
                        WHERE 1=1
                        {branch_condition}
                        ORDER BY sale_id ASC
                    """

           

        elif question == questions[1]:

            if role == "Super Admin":
                query = """
                    SELECT *
                    FROM branches
                    ORDER BY branch_id ASC
                """
                params = ()

            else:
                query = """
                        SELECT *
                        FROM branches
                        WHERE branch_id = %s
                        ORDER BY branch_id ASC
                    """
                params = (branch_id,)

        elif question == questions[2]:

            if role == "Super Admin":
                query = """
                    SELECT
                    cs.branch_id,
                        ps.*
                        FROM payment_splits ps
                    JOIN customer_sales cs
                        ON ps.sale_id = cs.sale_id
                """
                params = ()

            else:
                query = """
                    SELECT
                    cs.branch_id,
                        ps.*
                        FROM payment_splits ps
                    JOIN customer_sales cs
                        ON ps.sale_id = cs.sale_id
                    WHERE cs.branch_id = %s
                """
                params = (branch_id,)

        elif question == questions[3]:
            query = f"""
                SELECT *
                FROM customer_sales cs
                WHERE status = 'Open'
                {branch_condition}
                ORDER BY sale_id ASC
            """

        elif question == questions[4]:

            if role == "Super Admin":

                query = """
                    SELECT
                        b.branch_name,
                        SUM(cs.gross_sales) AS total_gross_sales
                    FROM customer_sales cs
                    JOIN branches b
                        ON cs.branch_id = b.branch_id
                    GROUP BY b.branch_name

                    UNION ALL

                    SELECT
                        'TOTAL' AS branch_name,
                        SUM(gross_sales) AS total_gross_sales
                    FROM customer_sales
                """

                params = ()

            else:

                query = """
                        SELECT
                            b.branch_name,
                            SUM(cs.gross_sales) AS total_gross_sales
                        FROM customer_sales cs
                        JOIN branches b
                            ON cs.branch_id = b.branch_id
                        WHERE cs.branch_id = %s
                        GROUP BY b.branch_name
                    """

                params = (branch_id,)

            
            
        elif question == questions[5]:

            query = f"""
                    SELECT
                        SUM(received_amount) AS total_received_amount
                    FROM customer_sales cs
                    WHERE 1=1
                    {branch_condition}
                """

            if role == "Admin":
                params = (branch_id,)
            else:
                params = ()
            

        elif question == questions[6]:
            query = f"""
                SELECT SUM(pending_amount) AS total_pending_amount
                FROM customer_sales cs
                WHERE 1=1
                {branch_condition}
            """
        elif question == questions[7]:

            query = f"""
                        SELECT
                            cs.branch_id,
                            b.branch_name,
                            COUNT(*) AS total_sales
                        FROM customer_sales cs
                        JOIN branches b
                            ON cs.branch_id = b.branch_id
                        WHERE 1=1
                        {branch_condition}
                        GROUP BY cs.branch_id, b.branch_name
                        order by total_sales DESC
                    """

        elif question == questions[8]:

            query = f"""
                    SELECT
                        cs.*,
                        b.branch_name
                    FROM customer_sales cs
                    JOIN branches b
                        ON cs.branch_id = b.branch_id
                    WHERE 1=1
                    {branch_condition}
                    ORDER BY b.branch_name, cs.sale_id
                """
        elif question == questions[9]:

            query = f"""
                        SELECT
                            cs.*,
                            COALESCE(SUM(ps.amount_paid), 0) AS total_received
                        FROM customer_sales cs
                        LEFT JOIN payment_splits ps
                            ON cs.sale_id = ps.sale_id
                        WHERE 1=1
                        {branch_condition}
                        GROUP BY cs.sale_id
                        order by total_received DESC
                    """

            

        elif question == questions[10]:

            query = f"""
                    SELECT
                        cs.*,
                        ps.payment_method
                    FROM customer_sales cs
                    LEFT JOIN payment_splits ps
                        ON cs.sale_id = ps.sale_id
                    WHERE 1=1
                    {branch_condition}
                """

        elif question == questions[11]:

            query = f"""
                    SELECT
                        cs.sale_id,
                        cs.branch_id,
                        b.branch_admin_name,
                        u.username,
                        cs.date,
                        cs.product_name,
                        cs.gross_sales,
                        cs.received_amount,
                        cs.pending_amount,
                        cs.status
                    FROM customer_sales cs
                    JOIN branches b
                        ON cs.branch_id = b.branch_id
                    JOIN users u
                        ON cs.branch_id = u.branch_id
                    WHERE u.role = 'Admin'
                    {branch_condition}
                order by cs.sale_id
                """
        elif question == questions[12]:

            query = f"""
                    SELECT *
                    FROM customer_sales cs
                    WHERE pending_amount > 5000
                    {branch_condition}
                    order by pending_amount DESC
                """
        elif question == questions[13]:

            query = f"""
                    SELECT *
                    FROM customer_sales cs
                    WHERE 1=1
                    {branch_condition}
                    ORDER BY gross_sales DESC
                    LIMIT 3
                """
        elif question == questions[14]:

            query = f"""
                    SELECT
                        b.branch_name,
                        SUM(cs.gross_sales) AS total_gross_sales
                    FROM customer_sales cs
                    JOIN branches b
                        ON cs.branch_id = b.branch_id
                    WHERE 1=1
                    {branch_condition}
                    GROUP BY b.branch_name
                    ORDER BY total_gross_sales DESC
                    LIMIT 1
                """


        if st.button("Execute Query"):

            st.write("QUERY:", query)
            
            cur.execute(query, params)

            rows = cur.fetchall()

            columns = [desc[0] for desc in cur.description]

            df = pd.DataFrame(rows, columns=columns)

            if len(df.columns) == 1:
                st.dataframe(
                    df,
                    hide_index=True,
                    height=70,
                    width=300
                )
            else:
                st.dataframe(
                    df,
                    hide_index=True
                )

            cur.close()
            conn.close()