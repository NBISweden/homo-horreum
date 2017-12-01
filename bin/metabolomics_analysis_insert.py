#!/usr/bin/env python

import sqlalchemy as sa
import argparse
import datetime
import json

from database import DatabaseConnection, DatabaseError

class AnalysisInserter(DatabaseConnection):

    def __init__(self):
        super().__init__()
        self.metabolomics_entity_tbl = self.get_table('metabolomics_entity')
        self.metabolomics_analysis_tb = self.get_table('metabolomics_analysis')
        self.test_type_tb = self.get_table('test_type')
        self.test_value_tb = self.get_table('test_value')

    def parse_file(self, filename):
        with open(filename, 'r') as f:
            header_line = f.readline()
            column_headers = []
            for h in header_line.split('\t'):
                column_headers.append(h)

            if 'CustID' not in column_headers:
                raise RuntimeError('Input file missing \'CustID\' column')

            if 'Platform' not in column_headers:
                raise RuntimeError('Input file missing \'Platform\' column')

            if 'Charge' not in column_headers:
                raise RuntimeError('Input file missing \'Charge\' column')

            lines = f.readlines()
            for i in range(0, len(lines)):
                row = lines[i].split('\t')
                if len(row) != len(column_headers):
                    raise RuntimeError('Mismatch in number of columns, missing data?')

                yield { column_headers[ci] : row[ci] for ci in range(0, len(column_headers)) }

    def insert_file(self, filename, num_classes, tissue, note, date):
        if num_classes not in [2, 3]:
            raise ValueError('Only supports 2 or 3 classes')

        trans = self.conn.begin()

        for r in self.parse_file(filename):
            tech = '{}_{}'.format(r['Platform'], r['Charge'])

            analysis_values = {
                'metabolite_id': self.get_metabolite(r['CustID']),
                'tissue': tissue,
                'technology': tech,
                'note': note
            }

            if date is not None:
                analysis_values['date'] = datetime.datetime.strptime(date, '%Y-%m-%d')

            res = self.conn.execute(self.metabolomics_analysis_tb.insert(), analysis_values)
            analysis_id = res.inserted_primary_key[0]

            def insert_test_value(name, value):
                self.conn.execute(self.test_value_tb.insert(), 
                {
                    'metabolomics_analysis_id': analysis_id,
                    'test_type_id': self.get_test_type(name),
                    'value': value
                })

            # Two classes:      pVal, TvNr, TvNp
            # Three classes:    pVal, PvNp, TvNr, TvNp, TvPp
            
            if num_classes == 2:
                insert_test_value('2class_pval', float(r['pVal']))
                insert_test_value('2class_tvnr', float(r['TvNr']))
                insert_test_value('2class_tvnp', float(r['TvNp']))
            elif num_classes == 3:
                insert_test_value('3class_pval', float(r['pVal']))
                insert_test_value('3class_pvnp', float(r['PvNp']))
                insert_test_value('3class_tvnr', float(r['TvNr']))
                insert_test_value('3class_tvnp', float(r['TvNp']))
                insert_test_value('3class_tvpp', float(r['TvPp']))

        trans.commit()

    def get_test_type(self, name):
        return self.get_or_create(self.test_type_tb, {"test": name})

    def get_metabolite(self, metabolite):
        return self.get_or_create(self.metabolomics_entity_tbl, {"name": metabolite})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Insert metabolomics analyis results")
    parser.add_argument('--file', type=str, required=True, help="TSV with metabolomics analysis results")
    parser.add_argument('--num_classes', type=int, required=True, help="Number of classes tested, should be either 2 or 3")
    parser.add_argument('--tissue', type=str, required=True, help="The tissue that was sampled")
    parser.add_argument('--note', type=str, required=True, help="Information about this metabolomics analysis")
    parser.add_argument('--date', type=str, required=False, help="Date when this analysis was performed (Format: yyyy-mm-dd, e.g. 2017-11-30)")

    args = parser.parse_args()

    try:
        AnalysisInserter().insert_file(args.file, args.num_classes, args.tissue, args.note, args.date)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
