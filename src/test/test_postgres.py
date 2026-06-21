import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

print("POSTGRES_HOST     =", os.getenv("POSTGRES_HOST"))
print("POSTGRES_PORT     =", os.getenv("POSTGRES_PORT"))
print("POSTGRES_DB       =", os.getenv("POSTGRES_DB"))
print("POSTGRES_USER     =", os.getenv("POSTGRES_USER"))
print("POSTGRES_PASSWORD =", os.getenv("POSTGRES_PASSWORD"))

try:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute("SELECT version();")

    result = cursor.fetchone()

    print("\nConnected Successfully!")
    print(result[0])

    cursor.close()
    conn.close()

except Exception as e:
    print("\nConnection Failed!")
    print(e)