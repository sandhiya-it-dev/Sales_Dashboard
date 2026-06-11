CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    branch_admin_name VARCHAR(100) NOT NULL
);

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    branch_id INT,
    date DATE,
    name VARCHAR(100),
    mobile_number VARCHAR(15),
    product_name VARCHAR(30),
    gross_sales DECIMAL(12,2),
    received_amount DECIMAL(12,2),
    pending_amount DECIMAL(12,2)
    GENERATED ALWAYS AS (gross_sales - received_amount) STORED,
    status VARCHAR(10) CHECK (status IN ('Open', 'Close')),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
ALTER TABLE sales
ADD CONSTRAINT unique_mobile_number
UNIQUE (mobile_number);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(255),
    branch_id INT,
    role VARCHAR(20) CHECK (role IN ('Super Admin', 'Admin')),
    email VARCHAR(255) UNIQUE,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);

CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    sale_id INT,
    payment_date DATE,
    amount_paid DECIMAL(12,2),
    payment_method VARCHAR(10)
    CHECK (payment_method IN ('Cash', 'UPI', 'Card')),
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
);

CREATE OR REPLACE FUNCTION update_sales_payment()
RETURNS TRIGGER AS $$
BEGIN
UPDATE sales
SET
    received_amount =
    (SELECT COALESCE(SUM(amount_paid),0)
        FROM payments
        WHERE sale_id = NEW.sale_id),
    status =
    CASE
        WHEN gross_sales -
        (SELECT COALESCE(SUM(amount_paid),0)
         FROM payments
         WHERE sale_id = NEW.sale_id) <= 0
        THEN 'Close'
        ELSE 'Open'
        END
WHERE sale_id = NEW.sale_id;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
DROP FUNCTION update_sales_payment();

CREATE TRIGGER payment_insert_trigger
AFTER INSERT
ON payments
FOR EACH ROW
EXECUTE FUNCTION update_sales_payment();
DROP TRIGGER payment_insert_trigger ON payments;


-- Table relationship for branches total 4 branches have been inserted
INSERT INTO branches (branch_name ,branch_admin_name) 
VALUES ('Chennai','Prashanth'),('Bangalore','Sandhiya'),('Mumbai','Karthik'),('Hyderabad','Keerthana');
SELECT * FROM branches;

-- TABLE INSERT FOR SALES
INSERT INTO sales
(branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
VALUES
(1,'2026-06-01','Arun','9000000001','DataScience_course',50000,20000,'Open'),
(2,'2026-06-01','Priya','9000000002','Fullstack_Developer_course',60000,60000,'Close'),
(3,'2026-06-02','Karthik','9000000003','Machine_learning_course',70000,30000,'Open'),
(4,'2026-06-02','Divya','9000000004','Automation_testing_course',45000,45000,'Close'),
(1,'2026-06-03','Vijay','9000000005','DataScience_course',55000,25000,'Open'),
(2,'2026-06-03','Meena','9000000006','Fullstack_Developer_course',65000,65000,'Close'),
(3,'2026-06-04','Ravi','9000000007','Machine_learning_course',72000,40000,'Open'),
(4,'2026-06-04','Anitha','9000000008','Automation_testing_course',48000,48000,'Close'),
(1,'2026-06-05','Suresh','9000000009','DataScience_course',52000,52000,'Close'),
(2,'2026-06-05','Kavya','9000000010','Fullstack_Developer_course',62000,20000,'Open'),
(3,'2026-06-06','Mohan','9000000011','Machine_learning_course',80000,50000,'Open'),
(4,'2026-06-06','Lakshmi','9000000012','Automation_testing_course',43000,43000,'Close'),
(1,'2026-06-07','Ajith','9000000013','DataScience_course',51000,10000,'Open'),
(2,'2026-06-07','Nisha','9000000014','Fullstack_Developer_course',61000,61000,'Close'),
(3,'2026-06-08','Hari','9000000015','Machine_learning_course',78000,78000,'Close'),
(4,'2026-06-08','Pooja','9000000016','Automation_testing_course',47000,20000,'Open'),
(1,'2026-06-09','Manoj','9000000017','DataScience_course',53000,53000,'Close'),
(2,'2026-06-09','Deepa','9000000018','Fullstack_Developer_course',67000,30000,'Open'),
(3,'2026-06-10','Ganesh','9000000019','Machine_learning_course',76000,76000,'Close'),
(4,'2026-06-10','Sneha','9000000020','Automation_testing_course',49000,25000,'Open'),
(1,'2026-06-11','Raj','9000000021','DataScience_course',50000,15000,'Open'),
(2,'2026-06-11','Keerthi','9000000022','Fullstack_Developer_course',69000,69000,'Close'),
(3,'2026-06-12','Ashok','9000000023','Machine_learning_course',81000,40000,'Open'),
(4,'2026-06-12','Swathi','9000000024','Automation_testing_course',52000,52000,'Close'),
(1,'2026-06-13','Bala','9000000025','DataScience_course',54000,54000,'Close'),
(2,'2026-06-13','Renu','9000000026','Fullstack_Developer_course',63000,20000,'Open'),
(3,'2026-06-14','Prakash','9000000027','Machine_learning_course',79000,79000,'Close'),
(4,'2026-06-14','Shalini','9000000028','Automation_testing_course',46000,10000,'Open'),
(1,'2026-06-15','Dinesh','9000000029','DataScience_course',57000,30000,'Open'),
(2,'2026-06-15','Aarthi','9000000030','Fullstack_Developer_course',68000,68000,'Close'),
(3,'2026-06-16','Senthil','9000000031','Machine_learning_course',83000,50000,'Open'),
(4,'2026-06-16','Ramya','9000000032','Automation_testing_course',50000,50000,'Close'),
(1,'2026-06-17','Kumar','9000000033','DataScience_course',58000,58000,'Close'),
(2,'2026-06-17','Janani','9000000034','Fullstack_Developer_course',64000,25000,'Open'),
(3,'2026-06-18','Vasanth','9000000035','Machine_learning_course',85000,85000,'Close'),
(4,'2026-06-18','Bhavya','9000000036','Automation_testing_course',51000,30000,'Open'),
(1,'2026-06-19','Rakesh','9000000037','DataScience_course',56000,20000,'Open'),
(2,'2026-06-19','Preethi','9000000038','Fullstack_Developer_course',70000,70000,'Close'),
(3,'2026-06-20','Arvind','9000000039','Machine_learning_course',82000,60000,'Open'),
(4,'2026-06-20','Sindhu','9000000040','Automation_testing_course',53000,53000,'Close');

-- TABLE INSERT FOR USERS 
INSERT INTO users (username, password, branch_id, role, email)
VALUES
('user1','admin123',1,'Admin','user1@gmail.com'),
('user2','admin123',2,'Admin','user2@gmail.com'),
('user3','admin123',3,'Admin','user3@gmail.com'),
('user4','admin123',4,'Admin','user4@gmail.com'),
('user5','admin123',NULL,'Super Admin','user5@gmail.com'),
('user6','admin123',1,'Admin','user6@gmail.com'),
('user7','admin123',2,'Admin','user7@gmail.com'),
('user8','admin123',3,'Admin','user8@gmail.com'),
('user9','admin123',4,'Admin','user9@gmail.com'),
('user10','admin123',NULL,'Super Admin','user10@gmail.com'),
('user11','admin123',1,'Admin','user11@gmail.com'),
('user12','admin123',2,'Admin','user12@gmail.com'),
('user13','admin123',3,'Admin','user13@gmail.com'),
('user14','admin123',4,'Admin','user14@gmail.com'),
('user15','admin123',NULL,'Super Admin','user15@gmail.com'),
('user16','admin123',1,'Admin','user16@gmail.com'),
('user17','admin123',2,'Admin','user17@gmail.com'),
('user18','admin123',3,'Admin','user18@gmail.com'),
('user19','admin123',4,'Admin','user19@gmail.com'),
('user20','admin123',NULL,'Super Admin','user20@gmail.com');

-- TABLE INSERT FOR PAYMENT AND ALSO VERIFYING IF TRIGGER WORKS OR NOT 
INSERT INTO payments
(sale_id, payment_date, amount_paid, payment_method)
VALUES
(1,'2026-06-21',10000,'UPI'),
(1,'2026-06-22',20000,'Cash'),
(3,'2026-06-21',15000,'Card'),
(3,'2026-06-23',25000,'UPI'),
(5,'2026-06-21',30000,'Cash'),
(7,'2026-06-22',20000,'UPI'),
(7,'2026-06-24',12000,'Card'),
(10,'2026-06-21',42000,'Cash'),
(11,'2026-06-22',15000,'UPI'),
(13,'2026-06-22',20000,'Card'),
(13,'2026-06-25',21000,'Cash'),
(16,'2026-06-22',27000,'UPI'),
(18,'2026-06-23',18000,'Cash'),
(20,'2026-06-23',24000,'Card'),
(21,'2026-06-24',35000,'UPI'),
(23,'2026-06-24',41000,'Cash'),
(26,'2026-06-24',25000,'Card'),
(28,'2026-06-25',36000,'UPI'),
(29,'2026-06-25',15000,'Cash'),
(31,'2026-06-25',33000,'UPI'),
(34,'2026-06-26',20000,'Card'),
(36,'2026-06-26',21000,'Cash'),
(37,'2026-06-26',18000,'UPI'),
(39,'2026-06-26',22000,'Card'),
(2,'2026-06-21',60000,'Cash'),
(4,'2026-06-21',45000,'UPI'),
(6,'2026-06-21',65000,'Card'),
(8,'2026-06-21',48000,'Cash'),
(9,'2026-06-21',52000,'UPI'),
(12,'2026-06-21',43000,'Card'),
(14,'2026-06-21',61000,'Cash'),
(15,'2026-06-21',78000,'UPI'),
(17,'2026-06-21',53000,'Card'),
(19,'2026-06-21',76000,'Cash'),
(22,'2026-06-21',69000,'UPI'),
(24,'2026-06-21',52000,'Card'),
(25,'2026-06-21',54000,'Cash'),
(27,'2026-06-21',79000,'UPI'),
(30,'2026-06-21',68000,'Card');

-- VERIFY TRIGGER LOGIC 
SELECT
sale_id,
gross_sales,
received_amount,
pending_amount,
status
FROM sales
ORDER BY sale_id;

-- CHECK CLOSED SALES
SELECT *
FROM sales
WHERE status = 'Close';

-- CHECK PENDING SALES
SELECT *
FROM sales
WHERE pending_amount > 0;

--CHECK PAYMENT HISTORY FOR A SALE
SELECT *
FROM payments
WHERE sale_id = 1;
-- 1)Retrieve all records from the customer_sales table
SELECT * FROM sales;
--2)Retrieve all records from the branches table.
SELECT * FROM branches;
--3)Retrieve all records from the payments table.
SELECT * FROM payments;
--4)Retrieve all sales belonging to the Chennai branch.
SELECT sales.*
FROM sales
JOIN branches 
ON sales.branch_id = branches.branch_id
WHERE branches.branch_name = 'Chennai';
-- 5) Calculate the total gross sales across all branches
SELECT SUM(gross_sales) AS total_gross_sales
FROM sales;
-- 6)Calculate the total received amount across all sales
SELECT SUM(received_amount) AS total_received_amount
FROM sales;
--7)Calculate the total pending amount across all sales
SELECT SUM(pending_amount) AS total_pending_amount
FROM sales;
-- 8)Find the average gross sales amount
SELECT AVG(gross_sales) AS average_gross_sales
FROM sales;
--9)Retrieve sales details along with the branch name
SELECT
    sales.sale_id,
    sales.name,
    sales.product_name,
    sales.gross_sales,
    branches.branch_name
FROM sales 
JOIN branches 
ON sales.branch_id = branches.branch_id;
--10)Show branch-wise total gross sales
SELECT
    branches.branch_name,
    SUM(sales.gross_sales) AS total_gross_sales
FROM sales 
JOIN branches 
ON sales.branch_id = branches.branch_id
GROUP BY branches.branch_name
ORDER BY total_gross_sales DESC;
--11)Display sales along with payment method used
SELECT
    sales.sale_id,
    sales.name,
    sales.product_name,
    payments.payment_method,
    payments.amount_paid
FROM sales 
JOIN payments 
ON sales.sale_id = payments.sale_id;
--12)Retrieve sales along with branch admin name
SELECT
    sales.sale_id,
    sales.name,
    sales.product_name,
    sales.gross_sales,
    branches.branch_name,
    branches.branch_admin_name
FROM sales 
JOIN branches 
ON sales.branch_id = branches.branch_id;
--13)Find sales where the pending amount is greater than 5000
SELECT *
FROM sales
WHERE pending_amount > 5000;
--14)Retrieve top 3 highest gross sales
SELECT *
FROM sales
ORDER BY gross_sales DESC
LIMIT 3;
--15)Calculate payment method-wise total collection (Cash / UPI / Card)
SELECT
    payment_method,
    SUM(amount_paid) AS total_collection
FROM payments
GROUP BY payment_method;

