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


CREATE TRIGGER payment_insert_trigger
AFTER INSERT
ON payments
FOR EACH ROW
EXECUTE FUNCTION update_sales_payment();
-- testing trigger function
INSERT INTO sales (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
VALUES (1, CURRENT_DATE, 'Test User', '9999999999', 'Python_course', 10000, 0, 'Open');

SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM sales;

INSERT INTO payments (sale_id, payment_date, amount_paid, payment_method)
VALUES (51, CURRENT_DATE, 10000, 'Cash');

SELECT sale_id, gross_sales, received_amount, pending_amount, status
FROM sales
WHERE sale_id = 51;

INSERT INTO sales (branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
VALUES (1, CURRENT_DATE, 'Test User', '9999999999', 'Python_course', 10000, 0, 'Open');

-- Table relationship for branches total 4 branches have been inserted
INSERT INTO branches (branch_name ,branch_admin_name) 
VALUES ('Chennai','Prashanth'),('Bangalore','Sandhiya'),('Mumbai','Karthik'),('Hyderabad','Keerthana');
SELECT * FROM branches;


select * from sales ;

-- TABLE INSERT FOR SALES
INSERT INTO sales
(branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
VALUES
(1, '2026-01-05', 'Arun Kumar',       '9841001001', 'DS',  15000, 0,     'Open'),
(1, '2026-01-10', 'Priya Rajan',      '9841002002', 'DA',  12000, 6000,  'Open'),
(1, '2026-01-15', 'Karthik Selvam',   '9841003003', 'BA',  10000, 10000, 'Close'),
(1, '2026-01-20', 'Divya Nair',       '9841004004', 'FSD', 18000, 9000,  'Open'),
(2, '2026-02-01', 'Rahul Menon',      '9841005005', 'DS',  15000, 0,     'Open'),
(2, '2026-02-05', 'Sneha Pillai',     '9841006006', 'DA',  12000, 12000, 'Close'),
(2, '2026-02-10', 'Vijay Anand',      '9841007007', 'BA',  10000, 5000,  'Open'),
(2, '2026-02-14', 'Meena Suresh',     '9841008008', 'FSD', 18000, 0,     'Open'),
(3, '2026-02-20', 'Suresh Babu',      '9841009009', 'DS',  15000, 15000, 'Close'),
(3, '2026-02-25', 'Lakshmi Ganesh',   '9841010010', 'DA',  12000, 4000,  'Open'),
(3, '2026-03-01', 'Naveen Raj',       '9841011011', 'BA',  10000, 10000, 'Close'),
(3, '2026-03-05', 'Anjali Mohan',     '9841012012', 'FSD', 18000, 8000,  'Open'),
(1, '2026-03-10', 'Deepak Sharma',    '9841013013', 'DS',  15000, 0,     'Open'),
(1, '2026-03-15', 'Kavitha Ravi',     '9841014014', 'DA',  12000, 12000, 'Close'),
(2, '2026-03-20', 'Manoj Krishnan',   '9841015015', 'BA',  10000, 3000,  'Open'),
(2, '2026-03-25', 'Pooja Venkat',     '9841016016', 'FSD', 18000, 18000, 'Close'),
(3, '2026-04-01', 'Ravi Chandran',    '9841017017', 'DS',  15000, 7000,  'Open'),
(1, '2026-04-05', 'Saranya Prasad',   '9841018018', 'DA',  12000, 0,     'Open'),
(2, '2026-04-10', 'Gopal Iyer',       '9841019019', 'BA',  10000, 10000, 'Close'),
(3, '2026-04-15', 'Nithya Balaji',    '9841020020', 'FSD', 18000, 9000,  'Open');

INSERT INTO sales
(branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
VALUES
(4, '2026-01-05', 'Maddy', '90190234561', 'DS',  15000, 0,     'Open'),
(4, '2026-01-10', 'Priya',  '00000000001', 'DA',  12000, 6000,  'Open'),
(4, '2026-01-15', 'Selvam', '09871345617', 'BA',  10000, 10000, 'Close');

-- table insert for users
INSERT INTO users
(username, password, branch_id, role, email)
VALUES
-- Super Admins (branch_id NULL because they manage all branches)
('superadmin1',  'Admin@123',  NULL, 'Super Admin', 'superadmin1@salesapp.com'),
('superadmin2',  'Admin@234',  NULL, 'Super Admin', 'superadmin2@salesapp.com'),

-- Branch Admins (one per branch)
('branch1_admin', 'Branch@123', 1,   'Admin', 'admin.branch1@salesapp.com'),
('branch2_admin', 'Branch@234', 2,   'Admin', 'admin.branch2@salesapp.com'),
('branch3_admin', 'Branch@345', 3,   'Admin', 'admin.branch3@salesapp.com'),
('branch4_admin', 'Branch@456', 4,   'Admin', 'admin.branch4@salesapp.com');

-- TABLE INSERT FOR PAYMENT AND ALSO VERIFYING IF TRIGGER WORKS OR NOT 
INSERT INTO payments (sale_id, payment_date, amount_paid, payment_method)
VALUES (55, CURRENT_DATE, 8500, 'UPI'),
(53,CURRENT_DATE,4000,'Card'),
(56,CURRENT_DATE,12000,'Cash'),
(58,CURRENT_DATE,5000,'Card'),
(61,CURRENT_DATE,8000,'UPI');
SELECT * FROM sales 
WHERE sale_id IN (55, 53, 56, 58, 61);

INSERT INTO payments (sale_id, payment_date, amount_paid, payment_method)
VALUES (55, CURRENT_DATE, 9500, 'UPI');

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

