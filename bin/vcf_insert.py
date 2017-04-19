#!/usr/bin/env python

import sqlalchemy as sa
import argparse
import json
import re
import tqdm

from database import DatabaseConnection, DatabaseError

class VCFInserter(DatabaseConnection):
    vcf_headers = [ 'chromosome', 'pos', 'identifier', 'ref', 'alt', 'qual', 'filter', 'info', 'format']

    def __init__(self):
        super().__init__()

        self.person_tbl = self.get_table('person')
        self.variant_tbl = self.get_table('variant')
        self.person_variant_tbl =  self.get_table('person_variant')

        self.variant_insert_stmt = self.variant_tbl.insert()


    def parse_file(self, filename):
        trans = self.conn.begin()
        variant_insert_stmt = self.variant_tbl.insert()

        person_var_ins = self.person_variant_tbl.insert()

        max_variant_id = 0
        res = self.engine.execute("SELECT max(id) FROM variant")
        for row in res:
            if row[0] != None:
                max_variant_id = row[0]

        var_inserts = []
        link_inserts = []

        with open(filename, 'r') as f:
            #pbar = tqdm.tqdm(mininterval=1)
            fields = []
            persons = []

            for line in tqdm.tqdm(f, desc="Inserting vcf file", mininterval=1, unit=" rows", unit_scale=True):
                line = line.strip()
                if line.startswith('##'):
                    continue

                if line.startswith('#'):
                    fields = line.split("\t")
                    persons = self.get_persons(fields[9:])
                    continue

                data = line.split("\t")

                max_variant_id += 1
                variant_ds = { VCFInserter.vcf_headers[i]: data[i] for i in range(len(VCFInserter.vcf_headers)) }
                variant_ds['id'] = max_variant_id
                var_inserts.append(variant_ds)

                link_inserts.extend([
                        {'person_id': persons[i], 'variant_id': max_variant_id, 'variant_type': data[i+9]  }
                        for i in range(len(persons))
                    ])

                if len(var_inserts) > 1000:
                    self.conn.execute(self.variant_insert_stmt, var_inserts)
                    self.conn.execute(person_var_ins, link_inserts)
                    var_inserts = []
                    link_inserts = []

            if len(var_inserts) > 0:
                self.conn.execute(self.variant_insert_stmt, var_inserts)
                self.conn.execute(person_var_ins, link_inserts)
                var_inserts = []
                link_inserts = []

        trans.commit()


    def get_persons(self, person_list):
        r = []
        pair_regex = re.compile(r"^(.*?)_\1$")
        for p in person_list:
            m = pair_regex.match(p)
            try:
                if m:
                    r.append( self._get(self.person_tbl, {'identifier': m.groups()[0]}) )
                else:
                    r.append( self._get(self.person_tbl, {'identifier': p }) )
            except AttributeError as e:
                raise DatabaseError("Can't find {} in database".format(p))
        return r

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
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
