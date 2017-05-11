#!/usr/bin/env python

import argparse
import re

from database import DatabaseConnection, DatabaseError

class EntityInserter(DatabaseConnection):

    def __init__(self):
        super().__init__()
        self.metabolomics_entity_tbl = self.get_table('metabolomics_entity')
        self.metabolomics_entity_info_tbl = self.get_table('metabolomics_entity_info')

    def insert_file(self, filename, id_column):
        trans = self.conn.begin()

        with open(filename, 'r') as f:

            idx_id_column = 0

            header_line = f.readline().strip()
            columns = header_line.split("\t")
            for i in range(len(columns)):
                if columns[i] == id_column:
                    idx_id_column = i
                    break

            columns.pop(idx_id_column)

            for line in f:
                values = line.strip().split("\t")
                id = values.pop( idx_id_column )
                metabolite = self._get(self.metabolomics_entity_tbl, {'name': id })
                if not metabolite:
                    raise DatabaseError("Can't find <{}> in database".format(id))
            
                ds = []
                for i in range(len(values)):
                    if re.match("^\s*$", values[i]):
                        continue
                    ds.append({
                            "metabolomics_entity_id": metabolite,
                            "name": columns[i],
                            "value": values[i]
                        })

                if ds:
                    self.conn.execute(self.metabolomics_entity_info_tbl.insert(), ds)

        trans.commit()

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert metabolomics entity info")
    parser.add_argument('--file', type=str, required=True, help="TSV containing info")
    parser.add_argument('--id', type=str, required=True, help="The name of the ID column")
    args = parser.parse_args()

    try:
        EntityInserter().insert_file(args.file, args.id)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
