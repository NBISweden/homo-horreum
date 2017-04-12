import sqlalchemy as sa
import numpy as np
import sys
import argparse

def get_image(id, filename):
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()

    img_tbl      = sa.Table('img'     , metadata, autoload=True, autoload_with=engine)
    img_data_tbl = sa.Table('img_data', metadata, autoload=True, autoload_with=engine)

    img_sel = img_tbl.join(img_data_tbl).select(img_tbl.c.id==id)
    img = engine.execute(img_sel).fetchone()

    if not img:
        sys.stderr.write("Can't find an image in the database with the id {}\n".format(id))
        sys.exit(1)

    def enc_write(f, s, enc='utf-8'):
        f.write(s.encode(enc))

    with open(filename, 'wb') as f:
        enc_write(f, "# vtk DataFile Version 3.0\n")
        enc_write(f, "Created using image_get.py (based on the Grid3 library output)\n")
        enc_write(f, "BINARY\n")
        enc_write(f, "DATASET STRUCTURED_POINTS\n")
        enc_write(f, "DIMENSIONS {}\n".format( img[img_tbl.c.dimensions].replace(",", " ")))
        enc_write(f, "ORIGIN {}\n".format( img[img_tbl.c.origin].replace(",", " ")))
        enc_write(f, "SPACING {}\n".format( img[img_tbl.c.spacing].replace(",", " ")))
        enc_write(f, "POINT_DATA {}\n".format(img[img_tbl.c.npoints]))
        enc_write(f, "SCALARS image_data double\n")
        enc_write(f, "LOOKUP_TABLE default\n")

        f.write(img[img_data_tbl.c.data])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract an image from the database")
    parser.add_argument('--id', type=str, required=True, help="Image ID")
    parser.add_argument('--file', type=str, required=True, help="Output file")
    args = parser.parse_args()

    get_image(args.id, args.file)
