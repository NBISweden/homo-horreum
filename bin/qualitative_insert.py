import sqlalchemy as sa
import argparse

class qual_inserter(object):
    def __init__(self):
        engine = sa.create_engine('sqlite:///test.db', echo=False)
        self.engine = engine
        metadata = sa.MetaData()

        self.person_tbl = sa.Table('person', metadata, autoload=True, autoload_with=engine)
        self.visit_tbl  = sa.Table('visit',  metadata, autoload=True, autoload_with=engine)
        self.m_val_tbl = sa.Table('measurement_value', metadata, autoload=True, autoload_with=engine)
        self.m_exp_tbl = sa.Table('measurement_experiment', metadata, autoload=True, autoload_with=engine)
        self.m_ent_tbl = sa.Table('measurement_entity', metadata, autoload=True, autoload_with=engine)

    def insert(self, filename):
        ## Redo this algorithm as follows:
# 1. every row gets turned into a hash with the header value as key for each
# entity
# 2. Some of the keys are special, they are easy to take care of immidiately
# and insert the correct data.
# 3. all the unknown stuff is filtered and inserted as fields

        with open(filename, 'r') as f:
            for line in f:
                (person, *fields) = line.split("\t")
                if line.startswith('#'):
                    fields_map = self.get_fields_map_for(fields)
                    continue
                p = self.get_person(person)
                self.insert_values(p, fields_map, fields)

    def get_person(self, id):
        person_sel = self.person_tbl.select(self.person_tbl.c.identifier == person)
        person = self.engine.execute(person_sel).fetchone()

        if person:
            return person

        sys.stderr.write("Can't find anyone in the database with the id {}\n".format(person))
        sys.exit(1)

    def insert_values(self, person, fields_map, fields):
        pass

    def get_fields_map_for(self, fields):
        return [ self._get_or_create_entity(f) for f in fields ]

    def _get_or_create_entity(self, f):
        tbl = self.m_ent_tbl
        sel = tbl.select(tbl.c.name == f)
        res = self.engine.execute(sel).fetchone()
        if res:
            print("FOUND IT")
            return res

        ins = tbl.insert().values(name=f, unit='NA')
        self.engine.execute(ins)

        res = self.engine.execute(sel).fetchone()
        if res:
            print("CREATING")
            return res

        raise Error("WTF??")
            
    

if __name__ == '__main__':
    #parser = argparse.ArgumentParser(description="Insert an qualitative datat in the database")
    #parser.add_argument('--file',   type=str, required=True, help="TSV file containing data")
    #args = parser.parse_args()

    #qual_inserter().insert(args.file)
    res = qual_inserter()._get_or_create_entity("Hello2")
    print(res)
