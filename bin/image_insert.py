import numpy as np
import sqlalchemy as sa
from tqdm import tqdm
import sys
import argparse

def insert_image(person, image_file, image_type):
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()

    person_tbl = sa.Table('person', metadata, autoload=True, autoload_with=engine)
    img_tbl    = sa.Table('img'   , metadata, autoload=True, autoload_with=engine)
    points_tbl = sa.Table('points', metadata, autoload=True, autoload_with=engine)


    person_sel = person_tbl.select(person_tbl.c.identifier == person)
    person = engine.execute(person_sel).fetchone()

    if not person:
        sys.stderr.write("Can't find anyone in the database with the id {}\n".format(person))
        sys.exit(1)

    try:
        img = read_image(image_file)
    except FileNotFoundError:
        sys.stderr.write("Can't find the image file {}\n".format(image_file))
        sys.exit(1)

    conn = engine.connect()
    conn.execute('pragma foreign_keys=OFF')

    ## Insert the image metadata
    img_ins = img_tbl.insert()
    res = conn.execute(img_ins,
            person_id = person[0],
            type = image_type,
            dimensions  = ",".join([str(x) for x in img['dimensions']]),
            origin  = ",".join([str(x) for x in img['origin']]),
            spacing = ",".join([str(x) for x in img['spacing']])
            )
    image_id = res.inserted_primary_key[0]

    dimensions = img['dimensions']
    npoints = dimensions[0]*dimensions[1]*dimensions[2]

    imgdata = img['img']
    data = []
    for i in tqdm(range(npoints), desc="Loading image", mininterval=1):
        value = imgdata[i]
        data.append({"img_id": image_id,
                     "coord_no": i,
                     "value": value})

    print("Inserting {} values".format(len(data)))
    conn.execute(points_tbl.insert(), data)


def read_image(image_file):
    with open(image_file) as f:
        ## First 10 lines are headerlines
        for i in range(10):
            (tag, *vals) = str(f.readline()).strip().split(' ')
            if tag == 'DIMENSIONS':
                dims = list(int(v) for v in vals)
            elif tag == 'SPACING':
                spacing = list(float(v) for v in vals)
            elif tag == 'ORIGIN':
                origin = list(float(v) for v in vals)
            elif tag == 'POINT_DATA':
                n = int(vals[0])
            elif tag == 'SCALARS':
                if vals[1] == 'double':
                    dtype = np.dtype('>f8')
                else:
                    raise ValueError('Expected image of type double, got {}'.format(vals[1]))

        # Next read the image
        img = np.fromfile(f, dtype).astype('f8') # Read and convert to little endian

    return {
        'img': img,
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

    insert_image(args.person, args.image, args.type)
