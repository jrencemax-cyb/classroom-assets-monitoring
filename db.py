import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="classroom_assets"
    )


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100),
        password VARCHAR(100),
        role VARCHAR(20)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        asset_name VARCHAR(100),
        quantity INT,
        status VARCHAR(20),
        classroom VARCHAR(50)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        asset_id INT,
        reported_by VARCHAR(100),
        issue TEXT
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()