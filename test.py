import psycopg2

try:
    conn = psycopg2.connect(
        dbname='cse3cax_webapp',
        user='postgres',
        password='postgres',
        host='3.106.202.172',
        port='5432'
    )
    print("Connection successful")
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
