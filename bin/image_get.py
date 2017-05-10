#!/usr/bin/env python
import sqlalchemy as sa
import argparse
import zlib

from database import DatabaseConnection, DatabaseError

class ImageGetter(DatabaseConnection):
    def __init__(self):
        super().__init__()

        self.img_tbl      = self.get_table('img')
        self.img_data_tbl = self.get_table('img_data')

    def get_image(self, id, filename):

        img_sel = self.img_tbl.join(self.img_data_tbl).select(self.img_tbl.c.id==id)
        img = self.engine.execute(img_sel).fetchone()

        if not img:
            raise DatabaseError("Can't find an image in the database with the id {}\n".format(id))

        # Decompress
        img_data = zlib.decompress(img[self.img_data_tbl.c.data])

        # Small helper function for writing encoded data to a binary stream
        def enc_write(f, s, enc='utf-8'):
            f.write(s.encode(enc))

        with open(filename, 'wb') as f:
            enc_write(f, "# vtk DataFile Version 3.0\n")
            enc_write(f, "Created using image_get.py (based on the Grid3 library output)\n")
            enc_write(f, "BINARY\n")
            enc_write(f, "DATASET STRUCTURED_POINTS\n")
            enc_write(f, "DIMENSIONS {}\n".format( img[self.img_tbl.c.dimensions].replace(",", " ")))
            enc_write(f, "ORIGIN {}\n".format( img[self.img_tbl.c.origin].replace(",", " ")))
            enc_write(f, "SPACING {}\n".format( img[self.img_tbl.c.spacing].replace(",", " ")))
            enc_write(f, "POINT_DATA {}\n".format(img[self.img_tbl.c.npoints]))
            enc_write(f, "SCALARS image_data double\n")
            enc_write(f, "LOOKUP_TABLE default\n")

            f.write(img_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract an image from the database")
    parser.add_argument('--id', type=str, required=True, help="Image ID")
    parser.add_argument('--file', type=str, required=True, help="Output file")
    args = parser.parse_args()

    try:
        ImageGetter().get_image(args.id, args.file)
    except DatabaseError as e:
        print("ERROR!: {}".format(e))
