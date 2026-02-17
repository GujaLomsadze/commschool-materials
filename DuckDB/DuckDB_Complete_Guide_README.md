# Installation

## Using pip

``` bash
pip install duckdb
```

------------------------------------------------------------------------

# Basic Python Usage

``` python
import duckdb

# In-memory database
con = duckdb.connect()

con.execute("CREATE TABLE test AS SELECT 42 AS value")
result = con.execute("SELECT * FROM test").fetchall()

print(result)
```

------------------------------------------------------------------------

# Persistent Database File

``` python
import duckdb

con = duckdb.connect("my_database.duckdb")

con.execute("CREATE TABLE example(id INTEGER, name VARCHAR)")
con.execute("INSERT INTO example VALUES (1, 'Alice')")

print(con.execute("SELECT * FROM example").fetchall())
```

------------------------------------------------------------------------

# Using DuckDB with Pandas

``` python
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

print(result)
result.to_csv("motherduck.csv", index=False)
```

DuckDB automatically recognizes Pandas DataFrames in scope.

------------------------------------------------------------------------

# Reading CSV Directly (No Import Required)

``` python
import duckdb

con = duckdb.connect()

df = con.execute("""
    SELECT ship_id, COUNT(*)
    FROM read_csv_auto('data.csv')
    GROUP BY ship_id
""").fetchdf()

print(df)
```

------------------------------------------------------------------------

# Reading Parquet Files

``` python
import duckdb

con = duckdb.connect()

df = con.execute("""
    SELECT *
    FROM read_parquet('data.parquet')
    WHERE SOG < 0.3
""").fetchdf()

print(df)
```

DuckDB performs predicate pushdown and only reads required columns.

------------------------------------------------------------------------

# Writing Parquet Files

``` python
con.execute("""
    COPY (SELECT * FROM my_table)
    TO 'output.parquet' (FORMAT 'parquet')
""")
```

------------------------------------------------------------------------

# Core SQL Features Supported

DuckDB supports:

-   SELECT
-   INSERT
-   UPDATE
-   DELETE
-   JOIN (INNER, LEFT, RIGHT, FULL)
-   GROUP BY
-   HAVING
-   ORDER BY
-   Window Functions
-   CTEs (WITH clauses)
-   Subqueries
-   Recursive queries
-   JSON functions
-   Aggregate functions
-   User-defined functions (UDFs)

Example with Window Function:

``` sql
SELECT
    ship_id,
    SOG,
    AVG(SOG) OVER (PARTITION BY ship_id) AS avg_per_ship
FROM my_table;
```

------------------------------------------------------------------------

# Transactions

``` python
con.execute("BEGIN TRANSACTION")
con.execute("INSERT INTO example VALUES (2, 'Bob')")
con.execute("COMMIT")
```

------------------------------------------------------------------------

# Concurrency Model

-   Multiple readers supported
-   Single writer
-   Multi-threaded execution
-   Single-node (not distributed)

------------------------------------------------------------------------

# When to Use DuckDB

Use DuckDB for:

-   Data analysis
-   Local analytics
-   Large CSV/Parquet processing
-   ETL pipelines
-   Data science workflows
-   Embedded analytics inside applications

------------------------------------------------------------------------

# When NOT to Use DuckDB

Avoid for:

-   High-frequency OLTP workloads
-   Web application backend databases
-   Distributed cluster workloads
-   Heavy concurrent writes

------------------------------------------------------------------------

# Performance Tips

-   Prefer Parquet over CSV
-   Select only required columns
-   Use WHERE filters early (predicate pushdown)
-   Use EXPLAIN to inspect query plans:

``` sql
EXPLAIN SELECT * FROM my_table;
```

------------------------------------------------------------------------

# Summary

DuckDB is:

-   Embedded
-   Columnar
-   Vectorized
-   Analytical (OLAP-focused)
-   Extremely fast for local analytics

It bridges the gap between Pandas and large-scale analytical databases.
