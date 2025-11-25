import psycopg2


conn_params = {
"dbname": "mydb",
"user": "postgres",
"password": "mypassword",
"host": "localhost",
"port": 5432
}


with psycopg2.connect(**conn_params) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM students;")
        result = cur.fetchone()
        print("Number of students:", result[0])