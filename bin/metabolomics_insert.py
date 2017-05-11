#!/usr/bin/env python

import sqlalchemy as sa
import argparse
import json

from database import DatabaseConnection, DatabaseError

class MetaBolInserter(DatabaseConnection):

    def __init__(self):
        super().__init__()
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

                ds = [{"metabolomics_experiment_id": experiment, "metabolomics_entity_id": db_metabolites[i], "value": values[i]} for i in range(len(values))]

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert metabolomics data")
    parser.add_argument('--file', type=str, required=True, help="TSV with metabolomics data")
    parser.add_argument('--note', type=str, required=True, help="Information about this metabolomics experiment")
    args = parser.parse_args()

    try:
        MetaBolInserter().insert_file(args.file, args.note)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
