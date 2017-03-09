import sqlalchemy as sa
import numpy as np
import sys
import argparse

def get_image(id, filename):
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()

    img_tbl    = sa.Table('img'   , metadata, autoload=True, autoload_with=engine)
    points_tbl = sa.Table('points', metadata, autoload=True, autoload_with=engine)
    coords_tbl = sa.Table('coords', metadata, autoload=True, autoload_with=engine)

    img_sel = img_tbl.select(img_tbl.c.id == id)
    img = engine.execute(img_sel).fetchone()

    points_sel = sa.select([
            coords_tbl.c.x,
            coords_tbl.c.y,
            coords_tbl.c.z,
            points_tbl.c.value
        ]
    ).where(
        sa.and_(
            points_tbl.c.img_id == id,
            points_tbl.c.coord_id == coords_tbl.c.id
        )
    )

    points = engine.execute(points_sel).fetchall()
    n_points = len(points)

    if not img:
        sys.stderr.write("Can't find an image in the database with the id {}\n".format(id))
        sys.exit(1)

    with open(filename, 'w') as f:
        f.write("# vtk DataFile Version 3.0\n")
        f.write("Created using image_get.py (based on the Grid3 library output)\n")
        f.write("BINARY\n")
        f.write("DATASET STRUCTURED_POINTS\n")
        f.write("DIMENSIONS {}\n".format( img[img_tbl.c.dimensions].replace(",", " ")))
        f.write("ORIGIN {}\n".format( img[img_tbl.c.origin].replace(",", " ")))
        f.write("SPACING {}\n".format( img[img_tbl.c.spacing].replace(",", " ")))
        f.write("POINT_DATA {}\n".format(n_points))
        f.write("SCALARS image_data double\n")
        f.write("LOOKUP_TABLE default\n")

        dims = list( map(lambda x: int(x), img[img_tbl.c.dimensions].split(",")) )
        npimg = np.zeros(dims).astype(np.dtype('>f8'))
        for p in points:
            npimg[p[0],p[1],p[2]] = p[3]

        binary_data = npimg.reshape(n_points)
        binary_data.tofile(f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract an image from the database")
    parser.add_argument('--id', type=str, required=True, help="Image ID")
    parser.add_argument('--file', type=str, required=True, help="Output file")
    args = parser.parse_args()

    get_image(args.id, args.file)
