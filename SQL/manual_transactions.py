conn = psycopg2.connect(**conn_params)
cur = conn.cursor()




try:
cur.execute("UPDATE students SET grade = grade + 0.5;")
conn.commit() # Explicit commit
except Exception as e:
print("Error, rolling back", e)
conn.rollback()
finally:
cur.close()
conn.close()