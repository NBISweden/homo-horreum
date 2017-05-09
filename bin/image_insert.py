#!/usr/bin/env python
import sqlalchemy as sa
import argparse
import zlib

from database import DatabaseConnection, DatabaseError

class ImageInserter(DatabaseConnection):
    def __init__(self):
        super().__init__()
        self.conn.execute('pragma foreign_keys=OFF')

        self.person_tbl = self.get_table('person')
        self.img_tbl    = self.get_table('img')
        self.img_data_tbl = self.get_table('img_data')

    def insert_image(self, person, image_file, image_type):
        trans = self.conn.begin()

        person_sel = self.person_tbl.select(self.person_tbl.c.identifier == person)
        person = self.engine.execute(person_sel).fetchone()

        if not person:
            raise DatabaseError("Can't find anyone in the database with the id {}\n".format(person))

        try:
            img = self.read_image(image_file)
        except FileNotFoundError:
            raise DatabaseError("Can't find the image file {}\n".format(image_file))
        except ValueError as e:
            raise DatabaseError("Can't parse the image file {}: \n".format(image_file, e))


        ## Insert the image metadata
        img_ins = self.img_tbl.insert()
        res = self.conn.execute(img_ins,
                person_id = person[0],
                type = image_type,
                dimensions  = ",".join([str(x) for x in img['dimensions']]),
                origin  = ",".join([str(x) for x in img['origin']]),
                spacing = ",".join([str(x) for x in img['spacing']]),
                npoints = img['n']
                )
        image_id = res.inserted_primary_key[0]

        dimensions = img['dimensions']

        self.conn.execute( self.img_data_tbl.insert(), {
                "img_id": image_id,
                "data": zlib.compress(img['data'])
            })

        trans.commit()

    def read_image(self, image_file):
        with open(image_file, 'rb') as f:
            ## First 10 lines are headerlines
            for i in range(10):
                (tag, *vals) = str(f.readline().decode('utf-8')).strip().split(' ')
                if tag == 'DIMENSIONS':
                    dims = list(int(v) for v in vals)
                elif tag == 'SPACING':
                    spacing = list(float(v) for v in vals)
                elif tag == 'ORIGIN':
                    origin = list(float(v) for v in vals)
                elif tag == 'POINT_DATA':
                    n = int(vals[0])

            # Next read the image
            data = f.read()

        return {
            'data': data,
            'origin': origin,
            'dimensions': dims,
            'spacing': spacing,
            'n': n,
        }


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Insert an image in the database")
    parser.add_argument('--person', type=str, required=True, help="Person ID")
    parser.add_argument('--image',   type=str, required=True, help="VTK image file")
    parser.add_argument('--type',    type=str, required=True, help="Type of image (fat, water, etc.)")
    args = parser.parse_args()

    try:
        ImageInserter().insert_image(args.person, args.image, args.type)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
