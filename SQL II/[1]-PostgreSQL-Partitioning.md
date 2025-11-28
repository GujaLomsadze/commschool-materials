# !!!!!!!!! There are errors in examples (on purpose) :) enjoy !!!!!!!!!

# PostgreSQL Partitioning Options for `public.students`

This document explains how to apply **Range**, **List**, and **Hash**
partitioning to the `public.students` table, with example code for each.

------------------------------------------------------------------------

## Table Definition

``` sql
CREATE TABLE public.students
(
    student_id      serial PRIMARY KEY,
    first_name      varchar(50),
    last_name       varchar(50),
    birthdate       date,
    email           text,
    is_active       boolean   default true,
    registered_at   timestamp default now(),
    grade           numeric(4, 2),
    profile_picture bytea
);
```

------------------------------------------------------------------------

# Partitioning Strategies

PostgreSQL supports three main partitioning strategies:

1.  **Range Partitioning**
2.  **List Partitioning**
3.  **Hash Partitioning**

------------------------------------------------------------------------

# 1. Range Partitioning

``` sql
CREATE TABLE public.students (
    student_id      serial PRIMARY KEY,
    first_name      varchar(50),
    last_name       varchar(50),
    birthdate       date,
    email           text,
    is_active       boolean DEFAULT true,
    registered_at   timestamp DEFAULT now(),
    grade           numeric(4, 2),
    profile_picture bytea
) PARTITION BY RANGE (birthdate);

CREATE TABLE public.students_1980s PARTITION OF public.students
    FOR VALUES FROM ('1980-01-01') TO ('1990-01-01');

CREATE TABLE public.students_1990s PARTITION OF public.students
    FOR VALUES FROM ('1990-01-01') TO ('2000-01-01');

CREATE TABLE public.students_2000s PARTITION OF public.students
    FOR VALUES FROM ('2000-01-01') TO ('2010-01-01');
```

------------------------------------------------------------------------

# 2. List Partitioning

``` sql
CREATE TABLE public.students (
    student_id      serial PRIMARY KEY,
    first_name      varchar(50),
    last_name       varchar(50),
    birthdate       date,
    email           text,
    is_active       boolean DEFAULT true,
    registered_at   timestamp DEFAULT now(),
    grade           numeric(4, 2),
    profile_picture bytea
) PARTITION BY LIST (is_active);

CREATE TABLE public.students_active PARTITION OF public.students
    FOR VALUES IN (true);

CREATE TABLE public.students_inactive PARTITION OF public.students
    FOR VALUES IN (false);
```

------------------------------------------------------------------------

# 3. Hash Partitioning

``` sql
CREATE TABLE public.students (
    student_id      serial PRIMARY KEY,
    first_name      varchar(50),
    last_name       varchar(50),
    birthdate       date,
    email           text,
    is_active       boolean DEFAULT true,
    registered_at   timestamp DEFAULT now(),
    grade           numeric(4, 2),
    profile_picture bytea
) PARTITION BY HASH (student_id);

CREATE TABLE public.students_p0 PARTITION OF public.students
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE public.students_p1 PARTITION OF public.students
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE public.students_p2 PARTITION OF public.students
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE public.students_p3 PARTITION OF public.students
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

------------------------------------------------------------------------

# Recommendations

-   Use **Range Partitioning** when filtering by dates.
-   Use **List Partitioning** for boolean or categorical data.
-   Use **Hash Partitioning** for balanced distribution without natural
    keys.
