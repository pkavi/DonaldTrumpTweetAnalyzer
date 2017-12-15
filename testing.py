from sqlalchemy import create_engine
import pandas as pd
# see sqlalchemy docs for how to write this url for your database type:
engine = create_engine('postgresql+psycopg2://postgres:password@localhost/whatever')
print("dsadas")
df = pd.read_sql_query("SELECT postdate, rawText  FROM tweetsTable;", engine)
print(df.head())