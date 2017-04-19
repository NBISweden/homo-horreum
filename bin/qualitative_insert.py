#!/usr/bin/env python
import sqlalchemy as sa
import argparse
import json

from database import DatabaseConnection, DatabaseError

class QualInserter(DatabaseConnection):
    def __init__(self):
        super().__init__()
        self.person_tbl = self.get_table('person')
        self.visit_tbl  = self.get_table('visit')
        self.m_val_tbl  = self.get_table('measurement_value')
        self.m_ent_tbl  = self.get_table('measurement_entity')

    def parse_file(self, filename):
        with open(filename, 'r') as f:
            fields_map = []
            for line in f:
                fields = line.strip("\n").split("\t")
                if line.startswith('#'):
                    fields[0] = fields[0][1:] # Remove comment sign from name
                    fields_map = fields
                    nfields = len(fields)
                    continue

                yield { fields_map[idx]: fields[idx] for idx in range(nfields) }

    def insert(self, filename):
        person_keys = {'ID': 'identifier', 'Group': 'group', 'Sex': 'sex'}
        visit_keys = {'Visit Code': 'visit_code', 'Visit Date': 'visit_date', 'Visit Comment': 'comment'}

        def extract_dict(d, keys):
            out = dict()
            for k,v in list(d.items()):
                if k in keys:
                    d.pop(k)
                    out[keys[k]] = v
            return out

        trans = self.conn.begin()

        for entry in self.parse_file(filename):
            person = extract_dict(entry, person_keys)
            visit  = extract_dict(entry, visit_keys)
            
            try:
                pid = self.get_or_create_person(person)
                vid = self.get_or_create_visit(pid, visit)
                self.insert_measurements(vid, entry)
            except DatabaseError as e:
                print("ERROR!: {}".format(e))
                print("Moving on")

        trans.commit()

    def insert_measurements(self, vid, entry):
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

    def get_or_create_visit(self, pid, visit):
        visit['person_id'] = pid
        return self.get_or_create(self.visit_tbl, visit)

    def get_or_create_person(self, person):
        if len(person) == 1:
            p = self._get(self.person_tbl, person)
            if not p:
                raise DatabaseError("Can't find any person with {}".format(json.dumps(person)))
            return p
        return self.get_or_create(self.person_tbl, person)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert an qualitative datat in the database")
    parser.add_argument('--file',   type=str, required=True, help="TSV file containing data")
    args = parser.parse_args()

    try:
        QualInserter().insert(args.file)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
