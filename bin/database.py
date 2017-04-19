import configparser
import sqlalchemy as sa

class DatabaseError(Exception):
    pass

class DatabaseConnection(object):
    def __init__(self):
        _config = configparser.ConfigParser()
        _config.read('alembic.ini')

        sqlalchemy_url = _config['alembic']['sqlalchemy.url']

        engine = sa.create_engine(sqlalchemy_url, echo=False)
        self.engine = engine
        self.conn = engine.connect()
        self.metadata = sa.MetaData()

    def get_table(self, table):
        return sa.Table(table, self.metadata, autoload=True, autoload_with=self.engine)

