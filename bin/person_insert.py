import sqlalchemy as sa
import argparse
import json

class InserterError(Exception):
    pass

class PersonInserter(object):
    def __init__(self):
        engine = sa.create_engine('sqlite:///test.db', echo=False)
        self.engine = engine
        self.conn = engine.connect()
        metadata = sa.MetaData()

        self.person_tbl = sa.Table('person', metadata, autoload=True, autoload_with=engine)

    def insert_person(self, identifier, group, sex):
        self.get_or_create(self.person_tbl, {
                'identifier': identifier,
                'group': group,
                'sex': sex,
            }
        )

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

    def get_or_create(self, table, info, return_primary_key=True):
        r = self._get(table, info, return_primary_key)
        if r:
            return r
        try:
            return self._insert(table,info,return_primary_key)
        except sa.exc.SQLAlchemyError:
            raise InserterError("Could not create {} from {}".format(table.name, json.dumps(info)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert a perons in the database")
    parser.add_argument('--identifier', type=str, required=True, help="Identifier for the person")
    parser.add_argument('--group', type=str, required=True, help="Experimental group")
    parser.add_argument('--sex', type=str, required=True, help="The sex")
    args = parser.parse_args()

    try:
        PersonInserter().insert_person(args.identifier, args.group, args.sex)
    except InserterError as e:
        print("ERROR!: {}".format(e))

