import psycopg2
import random
import string
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
conn_params = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "asdASD123",
    "host": "localhost",
    "port": 5432
}

# For reproducibility
random.seed(42)


# -----------------------------
# RANDOM GENERATOR FUNCTIONS
# -----------------------------
first_names = ["Anna", "John", "Maria", "Elias", "Sara", "Liam", "Noah", "Emma", "Oliver", "Sophia"]
last_names = ["Smith", "Miller", "Brown", "Williams", "Johnson", "Davis", "Garcia", "Martinez"]

skills = ["Python", "SQL", "Docker", "Kubernetes", "Linux", "Git", "Networking", "Machine Learning"]


def random_date(start_year=1995, end_year=2010):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def random_email(first, last):
    domain = random.choice(["gmail.com", "outlook.com", "yahoo.com"])
    return f"{first.lower()}.{last.lower()}@{domain}"


def random_grade():
    return round(random.uniform(1.0, 6.0), 2)


# -----------------------------
# POPULATION FUNCTIONS
# -----------------------------
def populate_students(cur, count):
    print(f"Inserting {count} students...")
    for _ in range(count):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        cur.execute(
            """
            INSERT INTO students (first_name, last_name, birthdate, email, grade)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (fn, ln, random_date(), random_email(fn, ln), random_grade())
        )


def populate_courses(cur, count):
    print(f"Inserting {count} courses...")
    for i in range(count):
        cur.execute(
            """
            INSERT INTO courses (course_name, credits, difficulty_level, price, start_date, metadata)
            VALUES (%s, %s, %s, %s, %s, '{}'::jsonb)
            """,
            (f"Course {i+1}", random.randint(1, 10), random.randint(1, 5),
             round(random.uniform(100, 1000), 2), random_date(2020, 2025))
        )


def populate_student_skills(cur):
    print("Inserting skills...")
    for skill_name in skills:
        cur.execute(
            "INSERT INTO student_skills (skill_name) VALUES (%s) ON CONFLICT DO NOTHING",
            (skill_name,)
        )


def populate_skill_mapping(cur):
    print("Mapping students to skills...")
    cur.execute("SELECT student_id FROM students")
    student_ids = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT skill_id FROM student_skills")
    skill_ids = [row[0] for row in cur.fetchall()]

    for sid in student_ids:
        num_skills = random.randint(1, 4)
        assigned = random.sample(skill_ids, num_skills)
        for sk in assigned:
            cur.execute(
                """
                INSERT INTO student_skill_map (student_id, skill_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (sid, sk)
            )


def populate_enrollments(cur):
    print("Creating enrollments...")
    cur.execute("SELECT student_id FROM students")
    students = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT course_id FROM courses")
    courses = [row[0] for row in cur.fetchall()]

    for s in students:
        enrolled_courses = random.sample(courses, random.randint(1, 5))
        for c in enrolled_courses:
            cur.execute(
                """
                INSERT INTO enrollments (student_id, course_id, enrolled_on)
                VALUES (%s, %s, current_date)
                """,
                (s, c)
            )


# -----------------------------
# MAIN EXECUTION
# -----------------------------
def run():
    student_count = int(input("How many students to generate? "))
    course_count = int(input("How many courses to generate? "))

    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            populate_students(cur, student_count)
            populate_courses(cur, course_count)
            populate_student_skills(cur)
            populate_skill_mapping(cur)
            populate_enrollments(cur)

    print("Done! Random data inserted successfully 👍")


if __name__ == "__main__":
    run()
