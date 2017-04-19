import random
import sqlalchemy as sa

def insert_persons(num=100):
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()
    person = sa.Table('person', metadata, autoload=True, autoload_with=engine)
    conn = engine.connect()
    insert = person.insert()
    trans = conn.begin()

    for i in range(num):
        person_identifier = "pt{:03}".format(i)
        conn.execute(insert,
                identifier=person_identifier,
                group = random.choice(['control', 'exp']),
                sex   = random.choice(['M','F'])
                )
    trans.commit()

if __name__ == '__main__':
    insert_persons(200)
