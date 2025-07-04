import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

def load_into_sqlite(tables):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    for name, data in tables.items():
        pd.DataFrame(data).to_sql(name, engine, index=False, if_exists='replace')
    return engine
