CREATE TABLE uni_students (
    student_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    department VARCHAR(50)
);

CREATE TABLE uni_courses (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100),
    credits INT,
    department VARCHAR(50)
);

CREATE TABLE uni_registrations (
    reg_id INT PRIMARY KEY,
    student_id INT,
    course_id INT,
    reg_date DATE,
    FOREIGN KEY (student_id) REFERENCES uni_students(student_id),
    FOREIGN KEY (course_id) REFERENCES uni_courses(course_id)
);

INSERT INTO uni_students VALUES
(1, 'Rahul', 'Sharma', 'rahul.sharma@uni.edu', 'CSE'),
(2, 'Priya', 'Menon', 'priya.menon@uni.edu', 'ECE'),
(3, 'Arjun', 'Reddy', 'arjun.reddy@uni.edu', 'MECH'),
(4, 'Sneha', 'Patil', 'sneha.patil@uni.edu', 'IT'),
(5, 'Vikram', 'Singh', 'vikram.singh@uni.edu', 'CSE');

INSERT INTO uni_courses VALUES
(101, 'Data Structures', 4, 'CSE'),
(102, 'Digital Electronics', 3, 'ECE'),
(103, 'Thermodynamics', 4, 'MECH'),
(104, 'Web Development', 3, 'IT'),
(105, 'AI Fundamentals', 4, 'CSE');

INSERT INTO uni_registrations VALUES
(1, 1, 101, '2025-01-10'),
(2, 2, 102, '2025-01-12'),
(3, 1, 105, '2025-01-15'),
(4, 4, 104, '2025-01-18'),
(5, 3, 103, '2025-01-20');



INSERT INTO uni_registrations (reg_id, student_id, course_id, reg_date)
VALUES (6, 5, 101, CURRENT_DATE);

SELECT s.first_name, s.last_name, c.course_name, c.credits
FROM uni_registrations r
JOIN uni_students s ON r.student_id = s.student_id
JOIN uni_courses c ON r.course_id = c.course_id
WHERE s.student_id = 1;

SELECT c.course_name, s.first_name, s.last_name, s.department
FROM uni_registrations r
JOIN uni_students s ON r.student_id = s.student_id
JOIN uni_courses c ON r.course_id = c.course_id
WHERE c.course_id = 101;

SELECT * FROM uni_students;
SELECT * FROM uni_courses;
SELECT * FROM uni_registrations;

