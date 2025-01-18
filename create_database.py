import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# PostgreSQL connection details
DB_USER = "postgres"
DB_PASSWORD = "tiger"  # Change karo agar different hai
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "customer_support"

print("🔧 Creating database...")

try:
    # Connect to default 'postgres' database
    conn = psycopg2.connect(
        dbname="postgres",  # Default database
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    
    # Set isolation level for CREATE DATABASE
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database already exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    exists = cursor.fetchone()
    
    if exists:
        print(f" Database '{DB_NAME}' already exists!")
    else:
        # Create database
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(DB_NAME)
        ))
        print(f"Database '{DB_NAME}' created successfully!")
    
    cursor.close()
    conn.close()
    
    # Now test connection to new database
    print(f"\nTesting connection to '{DB_NAME}'...")
    test_conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    
    test_cursor = test_conn.cursor()
    test_cursor.execute("SELECT version();")
    version = test_cursor.fetchone()[0]
    print(f"Connection successful!")
    print(f" PostgreSQL version: {version.split(',')[0]}")
    
    test_cursor.close()
    test_conn.close()
    
except psycopg2.OperationalError as e:
    print(f"\n Connection Error:")
    print(f"Error: {e}")
    print("\n Possible fixes:")
    print("1. Check if PostgreSQL service is running")
    print("2. Verify username/password in the script")
    print("3. Check if PostgreSQL is installed on port 5432")
    
except Exception as e:
    print(f"\nUnexpected Error:")
    print(f"Error: {e}")