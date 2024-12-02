import time
import psycopg2
from flask import Flask, request

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host='db',
        database='counter_db',
        user='user',
        password='password'
    )
    return conn

def get_hit_count():
    retries = 5
    while True:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO counter (datetime, client_info) VALUES (NOW(), %s) RETURNING id", (request.headers.get('User-Agent'),))
            conn.commit()
            cur.execute("SELECT COUNT(*) FROM counter")
            count = cur.fetchone()[0]
            cur.close()
            conn.close()
            return count
        except psycopg2.OperationalError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)