import sqlalchemy as sa
import argparse
import json
import re
import tqdm

class InserterError(Exception):
    pass

class VCFInserter(object):
    def __init__(self):
        engine = sa.create_engine('sqlite:///test.db', echo=False)
        self.engine = engine
        self.conn = engine.connect()
        metadata = sa.MetaData()

        self.person_tbl = sa.Table('person', metadata, autoload=True, autoload_with=engine)
        self.variant_tbl = sa.Table('variant', metadata, autoload=True, autoload_with=engine)
        self.person_variant_tbl =  sa.Table('person_variant', metadata, autoload=True, autoload_with=engine)

        self.variant_insert_stmt = self.variant_tbl.insert()


    def parse_file(self, filename):
        trans = self.conn.begin()
        variant_insert_stmt = self.variant_tbl.insert()
        vcf_headers = [ 'chromosome', 'pos', 'identifier', 'ref', 'alt', 'qual', 'filter', 'info']

        inserts = []

        with open(filename, 'r') as f:
            pbar = tqdm.tqdm(total=719697)
            fields = []
            person_of = {}
            for line in f:
                line = line.strip()
                pbar.update(1)
                if line.startswith('##'):
                    continue

                if line.startswith('#'):
                    fields = line.split("\t")
                    person_of = self.get_persons_of(fields[8:])
                    continue

                data = line.split("\t")

                variant = self.insert_variant( data[:8] )

                for idx in range(9,len(data)):
                    person = person_of[ fields[idx] ]
                    type = data[idx]
                    self.insert_person_variant(variant, person, type)
            pbar.close()
        trans.commit()

    def get_persons_of(self, person_list):
        r = {}
        pair_regex = re.compile(r"^(.*?)_\1$")
        for p in person_list:
            m = pair_regex.match(p)
            if m:
                r[p] = self._get(self.person_tbl, {'identifier': m.groups()[0]})
            else:
                r[p] = self._get(self.person_tbl, {'identifier': p })
        return r


    def insert_person_variant(self, variant, person, type):
        self._insert(self.person_variant_tbl,
                {
                    'person_id': person,
                    'variant_id': variant,
                    'variant_type': type,
                },
                return_primary_key=False
            )

    def insert_variant(self, vcf_line):
        vcf_headers = [ 'chromosome', 'pos', 'identifier', 'ref', 'alt', 'qual', 'filter', 'info']
        res = self.conn.execute(self.variant_insert_stmt,
                {
                    vcf_headers[i]: vcf_line[i] for i in range(len(vcf_headers))
                }
                )
        return res.inserted_primary_key[0]

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
    parser = argparse.ArgumentParser(description="Insert an vcf data in the database")
    parser.add_argument('--file',   type=str, required=True, help="TSV file containing data")
    args = parser.parse_args()

    try:
        VCFInserter().parse_file(args.file)
    except InserterError as e:
        print("ERROR!: {}".format(e))
