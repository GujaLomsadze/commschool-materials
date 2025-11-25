# PostgreSQL Teaching Materials

## 1. Introduction to SQL

* SQL = Structured Query Language
* Used to create, read, update, and delete data (CRUD)

---

## 2. Creating Tables in PostgreSQL

Below are examples covering common PostgreSQL data types.

### Example: Create a simple `students` table

```sql
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    birthdate DATE,
    email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMP DEFAULT NOW(),
    grade NUMERIC(4,2),
    profile_picture BYTEA
);
```

### Example: Table with different data types

```sql
CREATE TABLE courses (
    course_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_name TEXT NOT NULL,
    credits INT CHECK (credits > 0),
    difficulty_level SMALLINT,
    price DOUBLE PRECISION,
    start_date DATE,
    metadata JSONB
);
```

---

## 3. Relations Between Tables

### One-to-Many Relation Example

```sql
CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    course_id UUID REFERENCES courses(course_id),
    enrolled_on DATE DEFAULT CURRENT_DATE
);
```

This shows:

* One student can have many enrollments.
* One course can have many enrollments.

### Many-to-Many Relation (Using Junction Table)

```sql
CREATE TABLE student_skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name TEXT UNIQUE NOT NULL
);

CREATE TABLE student_skill_map (
    student_id INT REFERENCES students(student_id),
    skill_id INT REFERENCES student_skills(skill_id),
    PRIMARY KEY(student_id, skill_id)
);
```

---

## 4. Simple Queries

### Select all columns

```sql
SELECT * FROM students;
```

### Select specific columns

```sql
SELECT first_name, last_name FROM students;
```

### Filter results using WHERE

```sql
SELECT *
FROM students
WHERE is_active = TRUE;
```

### Sorting results

```sql
SELECT *
FROM students
ORDER BY registered_at DESC;
```

### Limit results

```sql
SELECT * FROM students LIMIT 5;
```

---

## 5. Aggregation Queries

### Count rows

```sql
SELECT COUNT(*) FROM students;
```

### Group by Example

Count students per active status:

```sql
SELECT is_active, COUNT(*)
FROM students
GROUP BY is_active;
```

### Average grade of students

```sql
SELECT AVG(grade) AS average_grade
FROM students;
```

### Aggregation with filtering (HAVING)

```sql
SELECT is_active, COUNT(*)
FROM students
GROUP BY is_active
HAVING COUNT(*) > 5;
```

### Sum, Min, Max

```sql
SELECT
    SUM(credits) AS total_credits,
    MIN(credits) AS min_credits,
    MAX(credits) AS max_credits
FROM courses;
```

---

## 6. Joining Tables

### INNER JOIN

```sql
SELECT s.first_name, s.last_name, c.course_name
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN courses c ON e.course_id = c.course_id;
```

### LEFT JOIN

```sql
SELECT s.first_name, e.course_id
FROM students s
LEFT JOIN enrollments e ON s.student_id = e.student_id;
```

---

## 7. Insert, Update, Delete

### Insert a row

```sql
INSERT INTO students (first_name, last_name, birthdate, email, grade)
VALUES ('Anna', 'Smith', '2005-01-12', 'anna@example.com', 1.75);
```

### Update a row

```sql
UPDATE students
SET is_active = FALSE
WHERE student_id = 10;
```

### Delete a row

```sql
DELETE FROM students
WHERE student_id = 5;
```

---

## 8. Helpful PostgreSQL Functions

```sql
SELECT NOW();              -- Current timestamp
SELECT CURRENT_DATE;       -- Today's date
SELECT RANDOM();           -- Random number between 0 and 1
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI'); -- Format timestamps
```

---

