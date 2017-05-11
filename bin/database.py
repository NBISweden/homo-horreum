import configparser
import sqlalchemy as sa
import json

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

    def get_or_create(self, table, info, return_primary_key=True):
        r = self._get(table, info, return_primary_key)
        if r:
            return r
        try:
            return self._insert(table,info,return_primary_key)
        except sa.exc.SQLAlchemyError:
            raise DatabaseError("Could not create {} from {}".format(table.name, json.dumps(info)))

    def _get(self, table, info, return_primary_key=True):
        s = table.select()
        for k, v in info.items():
            s = s.where( table.c[k] == v )
        r = self.conn.execute(s).fetchone()

        if not return_primary_key:
            return None
        if r:
            return r.id
        return None

    def _insert(self, table, info, return_primary_key=True):
        res = self.conn.execute(table.insert(), [ info ])
        if not return_primary_key:
            return
        id = res.inserted_primary_key
        return id[0]
