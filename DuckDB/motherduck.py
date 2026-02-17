import pandas as pd
import duckdb

df = pd.DataFrame({
    "ship_id": [1, 1, 2, 2],
    "SOG": [0.1, 0.5, 0.2, 0.3]
})

result = duckdb.query("""
    SELECT ship_id, AVG(SOG) AS avg_sog
    FROM df
    GROUP BY ship_id
""").to_df()

result.to_csv("motherduck.csv", index=False)
