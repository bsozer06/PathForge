import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def main():
    conn = psycopg2.connect(
        host=os.getenv('PGHOST', 'localhost'),
        port=os.getenv('PGPORT', '5432'),
        user=os.getenv('PGUSER', 'postgres'),
        password=os.getenv('PGPASSWORD', ''),
        dbname=os.getenv('PGDATABASE', 'osm')
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM roads;")
    count = cur.fetchone()[0]
    print(f"roads count: {count}")
    # sample: check geometry exists
    cur.execute("SELECT id FROM roads LIMIT 5;")
    rows = cur.fetchall()
    print(f"sample ids: {[r[0] for r in rows]}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
