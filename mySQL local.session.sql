CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    department VARCHAR(50),
    salary INT,
    hire_date DATE
);

INSERT INTO employees (emp_id, first_name, last_name, department, salary, hire_date) VALUES
(1, 'Amit', 'Sharma', 'HR', 45000, '2020-05-20'),
(2, 'Priya', 'Patel', 'Finance', 60000, '2021-02-10'),
(3, 'Ravi', 'Kumar', 'IT', 55000, '2019-08-14'),
(4, 'Neha', 'Reddy', 'Marketing', 48000, '2022-01-05'),
(5, 'Arjun', 'Singh', 'IT', 62000, '2020-09-12');


SELECT * FROM employees;

SELECT first_name, last_name, department FROM employees;

SELECT DISTINCT department FROM employees;

SELECT * FROM employees WHERE salary > 50000;

SELECT * FROM employees WHERE department = 'IT';

SELECT * FROM employees WHERE hire_date > '2020-01-01';

SELECT * FROM employees ORDER BY salary ASC;

SELECT * FROM employees ORDER BY salary DESC LIMIT 3;

SELECT COUNT(*) AS total_employees FROM employees;

SELECT AVG(salary) AS average_salary FROM employees;

SELECT MAX(salary) AS highest_salary FROM employees;

SELECT MIN(salary) AS lowest_salary FROM employees;

SELECT department, SUM(salary) AS total_salary_expenditure
FROM employees
GROUP BY department;

SELECT department
FROM employees
GROUP BY department
HAVING COUNT(*) > 1;

SELECT department, AVG(salary) AS average_salary
FROM employees
GROUP BY department;

SELECT YEAR(hire_date) AS hire_year, COUNT(*) AS employees_hired
FROM employees
GROUP BY YEAR(hire_date)
ORDER BY hire_year;

CREATE TABLE department (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL,
    location VARCHAR(50)
);


INSERT INTO department (dept_id, dept_name, location) VALUES
(1, 'HR', 'Hyderabad'),
(2, 'Finance', 'Mumbai'),
(3, 'IT', 'Bangalore'),
(4, 'Marketing', 'Chennai'),
(5, 'Operations', 'Delhi');

SELECT e.emp_id, e.first_name, e.last_name, e.department, d.location
FROM employees e
JOIN department d ON e.department = d.dept_name;

SELECT e.*
FROM employees e
JOIN department d ON e.department = d.dept_name
WHERE d.location = 'Bangalore';

SELECT e.*
FROM employees e
LEFT JOIN department d ON e.department = d.dept_name;

SELECT d.dept_name
FROM department d
LEFT JOIN employees e ON d.dept_name = e.department
WHERE e.emp_id IS NULL;

SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department;


SELECT *
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);


SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC
LIMIT 1;


SELECT *
FROM employees
ORDER BY hire_date DESC
LIMIT 1;


SELECT *
FROM employees
WHERE salary = (
    SELECT MAX(salary)
    FROM employees
    WHERE salary < (SELECT MAX(salary) FROM employees)
);


SELECT * 
FROM employees 
WHERE department = (SELECT department FROM employees WHERE first_name = 'Amit' AND last_name = 'Sharma');


UPDATE employees 
SET salary = salary * 1.10 
WHERE department = 'IT';


UPDATE employees 
SET department = 'Marketing' 
WHERE first_name = 'Ravi';


DELETE FROM employees 
WHERE salary < 40000;


ALTER TABLE employees 
ADD email VARCHAR(100);


UPDATE employees 
SET email = CONCAT(LOWER(first_name), '.', LOWER(last_name), '@example.com');


SELECT department, AVG(salary) AS avg_salary 
FROM employees 
GROUP BY department 
ORDER BY avg_salary DESC 
LIMIT 2;


SELECT d.location, COUNT(e.emp_id) AS employee_count 
FROM employees e 
JOIN departments d ON e.department = d.dept_name 
GROUP BY d.location;


SELECT COUNT(*) AS employee_count, SUM(salary) AS total_salary 
FROM employees;


SELECT * 
FROM employees 
WHERE first_name LIKE 'A%';


SELECT * 
FROM employees 
WHERE last_name LIKE '%a';


SELECT * 
FROM employees 
WHERE YEAR(hire_date) = 2020;


SELECT first_name, last_name, DATEDIFF(CURDATE(), hire_date) AS days_since_hire 
FROM employees;


SELECT UPPER(first_name) AS first_name, UPPER(last_name) AS last_name 
FROM employees;


SELECT CONCAT(first_name, ' ', last_name) AS full_name 
FROM employees;


SELECT * 
FROM employees 
WHERE salary BETWEEN 45000 AND 60000;


CREATE VIEW high_salary_employees AS 
SELECT * FROM employees 
WHERE salary > 55000;


SELECT * FROM high_salary_employees;


ALTER TABLE employees 
MODIFY department VARCHAR(50) NOT NULL;


DROP VIEW high_salary_employees;

ALTER TABLE employees RENAME TO staff;


CREATE TABLE employees_backup AS SELECT * FROM employees;


DELETE FROM employees;


DROP TABLE employees_backup;


CREATE INDEX idx_last_name ON employees(last_name);


DROP INDEX idx_last_name ON employees;

