import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.flaskenv'))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations():
    url = os.environ["DATABASE_URL"]
    engine = create_engine(url)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=None,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

run_migrations()