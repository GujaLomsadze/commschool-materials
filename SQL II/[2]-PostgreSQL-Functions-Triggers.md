# !!!!!!!!! There are errors in examples (on purpose) :) enjoy !!!!!!!!!

# PostgreSQL Function Template Examples

This document provides template code for creating PostgreSQL functions
using PL/pgSQL.\
You can use these templates to build your own logic inside PostgreSQL.

------------------------------------------------------------------------

## 1. Basic Function Template

``` sql
CREATE OR REPLACE FUNCTION example_basic_function(param1 integer)
RETURNS integer AS $$
BEGIN
    -- Your logic here
    RETURN param1 * 2;
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 2. Function That Inserts Data

``` sql
CREATE OR REPLACE FUNCTION add_student(
    p_first_name text,
    p_last_name text,
    p_birthdate date
)
RETURNS void AS $$
BEGIN
    INSERT INTO students(first_name, last_name, birthdate)
    VALUES (p_first_name, p_last_name, p_birthdate);
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 3. Function With Conditional Logic

``` sql
CREATE OR REPLACE FUNCTION check_student_status(p_student_id int)
RETURNS text AS $$
DECLARE
    active_status boolean;
BEGIN
    SELECT is_active INTO active_status
    FROM students
    WHERE student_id = p_student_id;

    IF active_status THEN
        RETURN 'Active';
    ELSE
        RETURN 'Inactive';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 4. Function Returning a Table

``` sql
CREATE OR REPLACE FUNCTION get_students_by_grade(min_grade numeric)
RETURNS TABLE(
    student_id int,
    first_name text,
    last_name text,
    grade numeric
) AS $$
BEGIN
    RETURN QUERY
    SELECT student_id, first_name, last_name, grade
    FROM students
    WHERE grade >= min_grade;
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 5. Function With Error Handling

``` sql
CREATE OR REPLACE FUNCTION safe_update_email(p_student_id int, p_email text)
RETURNS text AS $$
BEGIN
    BEGIN
        UPDATE students
        SET email = p_email
        WHERE student_id = p_student_id;

        RETURN 'Email updated successfully';
    EXCEPTION WHEN others THEN
        RETURN 'Error updating email';
    END;
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 6. Function With Looping

``` sql
CREATE OR REPLACE FUNCTION loop_example(n int)
RETURNS int AS $$
DECLARE
    total int := 0;
    i int := 1;
BEGIN
    WHILE i <= n LOOP
        total := total + i;
        i := i + 1;
    END LOOP;

    RETURN total;
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 7. Trigger Function Template

``` sql
CREATE OR REPLACE FUNCTION students_audit_trigger()
RETURNS trigger AS $$
BEGIN
    INSERT INTO students_audit(student_id, action, changed_at)
    VALUES (NEW.student_id, TG_OP, now());

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

------------------------------------------------------------------------

## 8. Example Trigger Using It

``` sql
CREATE TRIGGER trg_students_audit
AFTER INSERT OR UPDATE OR DELETE ON students
FOR EACH ROW
EXECUTE FUNCTION students_audit_trigger();
```

------------------------------------------------------------------------

# End of Document
