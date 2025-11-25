import psycopg2


conn = psycopg2.connect(
dbname="mydb",
user="postgres",
password="mypassword",
host="localhost",
port=5432
)


cur = conn.cursor()
cur.execute("SELECT version();")
print(cur.fetchone())


cur.close()
conn.close()