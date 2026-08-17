import psycopg2


def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="sales_db",
        user="postgres",
        password="admin",
        port="5432"
    )
    return conn



def get_branch_name(branch_id):
    
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT branch_name
        FROM branches
        WHERE branch_id = %s
    """, (branch_id,))

    branch = cur.fetchone()[0]

    cur.close()
    conn.close()

    return branch


def get_all_branches():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT branch_name
        FROM branches
        ORDER BY branch_id
    """)

    branches = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in branches]

def get_all_products():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT product_name
        FROM customer_sales
        WHERE product_name IS NOT NULL
        ORDER BY product_name
    """)

    products = [row[0] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return products


