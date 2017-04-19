#!/usr/bin/env python
import sqlalchemy as sa
import argparse
import json

from database import DatabaseConnection, DatabaseError

class PersonInserter(DatabaseConnection):
    def __init__(self):
        super().__init__()

        self.person_tbl = self.get_table('person')

    def insert_person(self, identifier, group, sex):
        self.get_or_create(self.person_tbl, {
                'identifier': identifier,
                'group': group,
                'sex': sex,
            }
        )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert a perons in the database")
    parser.add_argument('--identifier', type=str, required=True, help="Identifier for the person")
    parser.add_argument('--group', type=str, required=True, help="Experimental group")
    parser.add_argument('--sex', type=str, required=True, help="The sex")
    args = parser.parse_args()

    try:
        PersonInserter().insert_person(args.identifier, args.group, args.sex)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
