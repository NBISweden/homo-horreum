#!/usr/bin/env python
import sqlalchemy as sa
import argparse
import json

from database import DatabaseConnection, DatabaseError

class PersonInfoInserter(DatabaseConnection):
    def __init__(self):
        super().__init__()
        self.person_tbl = self.get_table('person')
        self.visit_tbl  = self.get_table('visit')
        self.m_val_tbl  = self.get_table('measurement_value')
        self.m_ent_tbl  = self.get_table('measurement_entity')

    def insert(self, file):
        visit_columns = [ 'visit_date', 'visit_code', 'visit_comment' ]

        trans = self.conn.begin()
        with open(file, 'r') as f:
            header_line = f.readline().strip()
            field_names = header_line.split("\t")
            nfields = len(field_names)

            idx_visit_columns = [ idx for idx in range(nfields) if field_names[idx] in visit_columns ]
            idx_others = [ idx for idx in range(nfields) if field_names[idx] not in visit_columns and idx!=0 ]

            for line in f:
                field_values = line.strip().split("\t")

                person = self.get_person(field_values[0])
                visit_ds = { field_names[idx]: field_values[idx] for idx in idx_visit_columns }

                vid = self.get_or_create_visit(person, visit_ds)

                entry = { field_names[idx]: field_values[idx] for idx in idx_others }
                self.insert_data(vid, entry)

        trans.commit()

    def get_person(self, identifier):
        print("GETTING: {}".format(identifier))
        return self._get(self.person_tbl, { 'identifier': identifier } )

    def get_or_create_visit(self, pid, visit):
        visit['person_id'] = pid

        if 'visit_comment' in visit:
            comment = visit.pop('visit_comment')
            visit['comment'] = comment

        return self.get_or_create(self.visit_tbl, visit)

    def insert_data(self, vid, entry):
        for key, value in entry.items():
            entity = self._get_entity(key)
            self._insert_value(vid, entity, value)

    def _get_entity(self, key):
        return self.get_or_create(self.m_ent_tbl, { 'name': key })

    def _insert_value(self, vid, entity, value):
        return self.get_or_create(self.m_val_tbl,
                { 
                    'visit_id': vid,
                    'measurement_entity_id': entity,
                    'value': value
                },
                return_primary_key=False
            )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add information about persons to the database")
    parser.add_argument('--file', type=str, required=True, help="TSV file with data")
    args = parser.parse_args()

    try:
        PersonInfoInserter().insert(args.file)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))

