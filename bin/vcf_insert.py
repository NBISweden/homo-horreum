import sqlalchemy as sa
import argparse
import json
import re
import tqdm

class InserterError(Exception):
    pass

class VCFInserter(object):
    vcf_headers = [ 'chromosome', 'pos', 'identifier', 'ref', 'alt', 'qual', 'filter', 'info', 'format']

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

        person_var_ins = self.person_variant_tbl.insert()

        with open(filename, 'r') as f:
            pbar = tqdm.tqdm(total=719697, mininterval=1)
            fields = []
            persons = []

            for line in f:
                line = line.strip()
                pbar.update(1)
                if line.startswith('##'):
                    continue

                if line.startswith('#'):
                    fields = line.split("\t")
                    persons = self.get_persons(fields[9:])
                    continue

                data = line.split("\t")

                variant = self.insert_variant( data[:9] )

                person_variant_ds = [
                        {'person_id': persons[i], 'variant_id': variant, 'variant_type': data[i+9]  }
                        for i in range(len(persons))
                    ]

                self.conn.execute(person_var_ins, person_variant_ds)

            pbar.close()
        trans.commit()


    def get_persons(self, person_list):
        r = []
        pair_regex = re.compile(r"^(.*?)_\1$")
        for p in person_list:
            m = pair_regex.match(p)
            if m:
                r.append( self._get(self.person_tbl, {'identifier': m.groups()[0]}) )
            else:
                r.append( self._get(self.person_tbl, {'identifier': p }) )
        return r

    def insert_variant(self, vcf_line):
        res = self.conn.execute(self.variant_insert_stmt,
                { VCFInserter.vcf_headers[i]: vcf_line[i] for i in range(len(VCFInserter.vcf_headers)) }
            )
        return res.inserted_primary_key[0]

    def _get(self, table, info):
        s = table.select()
        for k, v in info.items():
            s = s.where( table.c[k] == v )
        r = self.conn.execute(s).fetchone()
        return r.id


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert an vcf data in the database")
    parser.add_argument('--file', type=str, required=True, help="VCF-file containing data")
    args = parser.parse_args()

    try:
        VCFInserter().parse_file(args.file)
    except InserterError as e:
        print("ERROR!: {}".format(e))
