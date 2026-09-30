import logging
import pandas as pd
import csv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract(filename):
    with open(filename, 'r') as f:
        data = list(csv.DictReader(f))
    logger.info("Row count: %s", len(data))
    return data

def clean_orders(df):
    df = df.drop_duplicates(subset="order_id")
    df["item"] = df["item"].str.strip().str.title()
    df["customer_name"] = df["customer_name"].str.strip().str.title()
    df = df.replace("", pd.NA)
    df = df.dropna(subset=["item","customer_name"])
    df["quantity"] = pd.to_numeric(df["quantity"], errors = 'coerce')
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors = 'coerce')
    df['order_date'] = pd.to_datetime(df['order_date'], errors = 'coerce', format = 'mixed')
    df["total_amount"] = df["quantity"] * df["unit_price"]
    logger.info("Row count: %s", len(df))
    return df

def validate(df):
    df["quantity"] = pd.to_numeric(df["quantity"], errors = 'coerce')
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors = 'coerce')
    invalid = (
        df["quantity"].isna() | df["unit_price"].isna() | (df["quantity"]<=0) | df["order_date"].isna()
    )
    errors_df = df[invalid].copy()
    def get_error_reason(row):
        reasons = []
        if pd.isna(row['quantity']):
            reasons.append("Missing quantity")
        if pd.isna(row['unit_price']):
            reasons.append("Missing unit_price")
        if row["quantity"]<=0:
            reasons.append("Invalid quantity")
        if pd.isna(row['order_date']):
            reasons.append("Missing order_date")
        return ", ".join(reasons)
    errors_df['error_reason'] = errors_df.apply(get_error_reason, axis=1)
    valid_df = df[~invalid].copy()
    logger.info("%s Valid rows and %s rejected rows", len(valid_df), len(errors_df))
    return errors_df, valid_df

def save_errors(errors, filename):
    os.makedirs('errors', exist_ok=True)
    errors.to_csv(f'errors/{filename}', index=False)
    logger.info("Saved %s errors to errors/%s", {len(errors)}, {filename})

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def load_to_postgres(df):
    load_dotenv()

    try:
        logging.info("Connecting to PostgreSQL")

        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        db_host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")

        print("USER:", db_user)
        print("HOST:", db_host)
        print("DATABASE:", db_name)

        engine = create_engine(
            f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:5432/{db_name}"
        )

        df.to_sql("orders", engine, if_exists="replace", index=False)

        logging.info("Loaded %s orders into PostgreSQL.", len(df))

    except Exception:
        logging.exception("Failed to connect to PostgreSQL.")
        raise

def run_pipeline():
    logger.info("=" * 40)
    logger.info("Pipeline started")
    
    raw = extract('/Users/Marydoris/Cleotha/Restaurant Chain Orders Pipeline/orders.csv')
    clean = clean_orders(pd.DataFrame(raw))
    error, valid = validate(clean)
    save_errors(error, "error.csv")
    load_to_postgres(valid)
    
    logger.info("Pipeline completed successfully")
    logger.info("=" * 40)

if __name__ == '__main__':
    run_pipeline()