Restaurant Chain Orders Pipeline
A beginner-friendly ETL (Extract, Transform, Load) data pipeline
built with Python, Pandas, PostgreSQL, SQLAlchemy, and Pytest.

The project takes raw restaurant order data from a CSV file, cleans and
validates it, separates rejected records, and loads valid orders into
PostgreSQL for analysis.

Project Overview
The pipeline follows this flow:

CSV File
   ↓
Extract
   ↓
Clean
   ↓
Validate
   ├── Invalid records → errors/error.csv
   ↓
Valid records
   ↓
PostgreSQL
   ↓
SQL Analysis
Technologies Used
Python --- pipeline development

Pandas --- data cleaning and transformation

CSV --- source data format

PostgreSQL --- data storage

SQLAlchemy --- PostgreSQL connection

python-dotenv --- database environment variables

Pytest --- automated testing

Logging --- pipeline monitoring and debugging

Pipeline Steps
1. Extract
The extract() function reads the CSV file using csv.DictReader and
converts the records into a list.

It also logs the number of rows extracted.

def extract(filename):
    with open(filename, 'r') as f:
        data = list(csv.DictReader(f))
    logger.info("Row count: %s", len(data))
    return data
2. Clean
The clean_orders() function:

Removes duplicate order_id values

Removes extra spaces from item and customer_name

Converts text to title case

Replaces empty strings with missing values

Removes rows missing item or customer_name

Converts quantity and unit_price to numeric values

Converts order_date to datetime

Creates a total_amount column

total_amount = quantity × unit_price
3. Validate
The validate() function separates records into:

Valid records

Rejected records

A record is rejected when:

quantity is missing

unit_price is missing

quantity is less than or equal to zero

order_date is missing

Rejected records receive an error_reason explaining why they were
rejected.

4. Save Errors
Rejected records are saved to:

errors/error.csv
The errors directory is created automatically if it does not already
exist.

5. Load to PostgreSQL
Valid records are loaded into a PostgreSQL table named:

orders
Database credentials are loaded from environment variables using
python-dotenv.

Expected variables:

DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=orders_db
Do not commit your .env file or database password to GitHub.

6. Logging
The pipeline logs important events such as:

Pipeline start

Number of extracted rows

Number of cleaned rows

Number of valid and rejected rows

PostgreSQL connection

Number of orders loaded

Pipeline completion

Errors encountered during database loading

Logs are written to:

pipeline.log
and displayed in the terminal.

Testing
Pytest is used to test important parts of the cleaning and validation
process.

The tests check that:

Duplicate orders are removed

Missing items are removed

Quantity is converted to a numeric data type

total_amount is created

Negative quantities are rejected

Missing prices are rejected

Run the tests with:

pytest
SQL Analysis
After loading the valid orders into PostgreSQL, SQL queries are used to
analyze the data.

View all orders
SELECT * FROM orders;
Total revenue by branch
SELECT
    branch,
    SUM(total_amount) AS total_revenue
FROM orders
GROUP BY branch;
Item with the highest quantity sold
SELECT
    item,
    SUM(quantity) AS quantity
FROM orders
GROUP BY item
ORDER BY quantity DESC
LIMIT 1;
Revenue by payment method
SELECT
    payment_method,
    SUM(total_amount) AS revenue
FROM orders
GROUP BY payment_method;
Top 3 customers by total order value
The intended approach uses a CTE and ROW_NUMBER() to rank customers by
their total order value.

WITH ranked_orders AS (
    SELECT
        customer_name,
        SUM(total_amount) AS total_amount,
        ROW_NUMBER() OVER (
            ORDER BY SUM(total_amount) DESC
        ) AS rank
    FROM orders
    GROUP BY customer_name
)
SELECT *
FROM ranked_orders
WHERE rank <= 3;
Branches with an average order value above the overall average
SELECT
    branch,
    AVG(total_amount) AS avg_order_value
FROM orders
GROUP BY branch
HAVING AVG(total_amount) > (
    SELECT AVG(total_amount)
    FROM orders
);
Project Structure
A possible project structure is:

Restaurant Chain Orders Pipeline/
│
├── pipeline.py
├── orders.csv
├── .env
├── pipeline.log
├── errors/
│   └── error.csv
└── tests/
    └── test_pipeline.py
How to Run
1. Install dependencies
pip install pandas sqlalchemy psycopg python-dotenv pytest
2. Configure environment variables
Create a .env file:

DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=orders_db
3. Run the pipeline
python pipeline.py
4. Run tests
pytest
5. Query the PostgreSQL database
After the pipeline finishes successfully, connect to orders_db and run
the SQL analysis queries.

What I Practiced
This project helped me practice:

Building an ETL pipeline

Reading CSV data with Python

Pandas data cleaning

Handling missing and invalid data

Duplicate detection and removal

Data validation

Error reporting

Python logging

PostgreSQL integration

SQLAlchemy

Environment variables

Automated testing with Pytest

SQL aggregation

GROUP BY and HAVING

Subqueries

CTEs

Window functions and ROW_NUMBER()

Future Improvements
Possible improvements for a production-style version include:

Use if_exists="append" or an upsert strategy instead of replacing
the PostgreSQL table on every run

Add required-column validation

Add more comprehensive tests

Add data-quality checks for all important fields

Move the CSV path into configuration instead of hard-coding it

Add database connection handling and cleanup

Containerize the pipeline with Docker

Add orchestration with Airflow

