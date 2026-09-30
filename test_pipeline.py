import pytest
import pandas as pd
import numpy as np
from pipeline import clean_orders, validate

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'order_id': [1, 1, 2, 3],
        'branch': ['Lagos', 'Lagos', 'Abuja', 'Ibadan'],
        'item': ['Jollof Rice', 'Jollof Rice', 'Suya', None],
        'quantity': ['2', '2', '-1', '3'],
        'unit_price': ['2500', '2500', '1500', ''],
        'order_date': ['2024-01-05', '2024-01-05', '2024-01-06', '2024-01-07'],
        'customer_name': ['alice', 'alice', 'bob', 'charlie']
    })

def test_duplicates_removed(sample_df):
    cleaned = clean_orders(sample_df)
    assert cleaned['order_id'].is_unique

def test_missing_item_dropped(sample_df):
    cleaned = clean_orders(sample_df)
    assert cleaned['item'].isnull().sum() == 0

def test_quantity_is_numeric(sample_df):
    cleaned = clean_orders(sample_df)
    assert pd.api.types.is_numeric_dtype(cleaned['quantity'])

def test_total_amount_column_exists(sample_df):
    cleaned = clean_orders(sample_df)
    assert 'total_amount' in cleaned.columns

def test_validate_catches_negative_quantity(sample_df):
    cleaned = clean_orders(sample_df)
    error, valid = validate(cleaned)
    assert (valid['quantity'] > 0).all()

def test_validate_catches_missing_price(sample_df):
    cleaned = clean_orders(sample_df)
    error, valid = validate(cleaned)
    assert valid['unit_price'].isnull().sum() == 0