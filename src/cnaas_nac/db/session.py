import os
import yaml
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def get_dbdata(config='/etc/cnaas-nac/db_config.yml'):
    if not os.path.exists('/etc/cnaas-nac/db_config.yml'):
        return {'hostname': 'localhost',
                'username': 'cnaas',
                'password': 'cnaas',
                'type': 'postgresql',
                'database': 'nac',
                'port': 5432}
    with open(config, 'r') as db_file:
        return yaml.safe_load(db_file)


def get_sqlalchemy_conn_str(**kwargs) -> str:
    db_data = get_dbdata(**kwargs)

    if 'CNAAS_DB_HOSTNAME' in os.environ:
        db_data['hostname'] = os.environ['CNAAS_DB_HOSTNAME']
    if 'CNAAS_DB_PORT' in os.environ:
        db_data['port'] = os.environ['CNAAS_DB_PORT']
    if 'CNAAS_DB_USERNAME' in os.environ:
        db_data['username'] = os.environ['CNAAS_DB_USERNAME']
    if 'CNAAS_DB_PASSWORD' in os.environ:
        db_data['password'] = os.environ['CNAAS_DB_PASSWORD']
    if 'CNAAS_DB_DATABASE' in os.environ:
        db_data['database'] = os.environ['CNAAS_DB_DATABSE']

    return (
        f"{db_data['type']}://{db_data['username']}:{db_data['password']}@"
        f"{db_data['hostname']}:{db_data['port']}/{db_data['database']}"
    )


def get_session(conn_str=''):
    if conn_str == '':
        conn_str = get_sqlalchemy_conn_str()

    engine = create_engine(conn_str, pool_size=50, max_overflow=0)
    Session = sessionmaker(bind=engine)

    return Session()


@contextmanager
def sqla_session(conn_str='', **kwargs):
    session = get_session(conn_str)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
