#!/usr/bin/env python

import sqlalchemy as sa
import argparse
import json
import re
import tqdm

from database import DatabaseConnection, DatabaseError

class MetaBolInserter(DatabaseConnection):

    def __init__(self):
        self.person_tbl = self.get_table('person')
        self.metabolomics_experiment_tbl = self.get_table('metabolomics_experiment')
        self.metabolomics_value_tbl = self.get_table('metabolomics_value')
        self.metabolomics_entity_tbl = self.get_table('metabolomics_entity')

    def insert_file(self, filename, note):
        trans = self.conn.begin()

        with open(filename, 'r') as f:

            header_line = f.readline()
            metabolites = header_line.split()[1:]
            db_metabolites = self.get_metabolites( metabolites )

            for line in f:
                (person, *values) = line.split()
                experiment = self.get_experiment(person, note)

                ds = [{"metabolomics_experiment_id": experiment, "metabolomics_entity_id": metabolites[i], "value": values[i]} for i in range(len(values))]

                self.conn.execute(self.metabolomics_value_tbl.insert(), ds)

        trans.commit()

    def get_metabolites(self, metabolites):
        ids = []
        for m in metabolites:
            ids.append( self.get_or_create(self.metabolomics_entity_tbl, {"name": m}) )
        return ids

    def get_experiment(self, person_id, note):
        person = self.get_person(person_id)
        if person == None:
            raise DatabaseError("Can't find person: {}".format(person_id))

        return self.get_or_create(self.metabolomics_experiment_tbl, {'person_id': person, 'note': note})

    def get_person(self, person_id):
        return self._get(self.person_tbl, {'identifier': person_id })

    def _get(self, table, info, return_primary_key=True):
        s = table.select()
        #print("TABLE: {} KEYS: {}".format(table, table.c.keys()))
        for k, v in info.items():
            #print("_get: {} {}".format( k, v) )
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
            raise DatabaseError("Could not create {} from {}".format(table.name, json.dumps(info)))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert an vcf data in the database")
    parser.add_argument('--file', type=str, required=True, help="VCF-file containing data")
    parser.add_argument('--note', type=str, required=True, help="Information about this metabolomics experiment")
    args = parser.parse_args()

    try:
        MetaBolInserter().insert_file(args.file, args.note)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
