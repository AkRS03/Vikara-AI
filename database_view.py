from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os
# Replace this with your Render DB connection string
load_dotenv()

# Create a connection engine
engine = create_engine(os.getenv('DATABASE_URL'))

# Read a table into a DataFrame
table_name = "tickets"
df = pd.read_sql_table(table_name, con=engine)

print(df)
