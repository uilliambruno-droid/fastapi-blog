import databases
import sqlalchemy as sa

from src.config import settings

DATABASE_URL = settings.database_url

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

database = databases.Database(DATABASE_URL)
metadata = sa.MetaData()
engine = sa.create_engine(DATABASE_URL, connect_args=connect_args)
