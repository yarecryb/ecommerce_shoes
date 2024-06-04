from faker import Faker
import pandas as pd
from sqlalchemy import create_engine
import random

fake = Faker()

# Connection details with SSL disabled
engine = create_engine('postgresql://postgres:postgres@localhost:54323/your_database?sslmode=disable')

# Function to test database connection
def test_connection():
    import psycopg2
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="54323",

        )
        print("Connection successful")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        raise

# Test database connection
test_connection()

# Functions to generate fake data
def generate_users(n):
    users = []
    for _ in range(n):
        users.append({
            'username': fake.user_name(),
            'email': fake.email(),
            'password': fake.password(),
            'full_name': fake.name(),
            'wallet': round(random.uniform(0, 1000), 2)
        })
    return users

def generate_catalog(n, user_ids):
    catalog = []
    for _ in range(n):
        catalog.append({
            'title': fake.word(),
            'brand': fake.company(),
            'size': str(random.choice(['S', 'M', 'L', 'XL'])),
            'price': round(random.uniform(10, 500), 2),
            'user_id': random.choice(user_ids),
            'quantity': random.randint(1, 100)
        })
    return catalog

def generate_catalog_ledger(n, user_ids, catalog_ids):
    ledger = []
    for _ in range(n):
        ledger.append({
            'customer_id': random.choice(user_ids),
            'catalog_id': random.choice(catalog_ids),
            'quantity': random.randint(1, 10)
        })
    return ledger

def generate_carts(n, user_ids, catalog_ids):
    carts = []
    for _ in range(n):
        carts.append({
            'bought': fake.boolean(),
            'catalog_id': random.choice(catalog_ids) if fake.boolean() else None,
            'user_id': random.choice(user_ids)
        })
    return carts

def generate_cart_items(n, cart_ids, catalog_ids):
    items = []
    for _ in range(n):
        items.append({
            'cart_id': random.choice(cart_ids),
            'catalog_id': random.choice(catalog_ids),
            'quantity': random.randint(1, 10)
        })
    return items

def bulk_insert(table_name, data):
    df = pd.DataFrame(data)
    df.to_sql(table_name, engine, if_exists='append', index=False)

# Generate and load data
user_data = generate_users(100000)
bulk_insert('users', user_data)

user_ids = pd.read_sql('SELECT id FROM users', engine)['id'].tolist()
catalog_data = generate_catalog(100000, user_ids)
bulk_insert('catalog', catalog_data)

catalog_ids = pd.read_sql('SELECT id FROM catalog', engine)['id'].tolist()
ledger_data = generate_catalog_ledger(500000, user_ids, catalog_ids)
bulk_insert('catalog_ledger', ledger_data)

cart_data = generate_carts(100000, user_ids, catalog_ids)
bulk_insert('carts', cart_data)

cart_ids = pd.read_sql('SELECT cart_id FROM carts', engine)['cart_id'].tolist()
cart_item_data = generate_cart_items(1000000, cart_ids, catalog_ids)
bulk_insert('cart_items', cart_item_data)
