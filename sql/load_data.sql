COPY students
FROM '/data/students_dashboard.csv'
WITH (FORMAT csv, HEADER true);
