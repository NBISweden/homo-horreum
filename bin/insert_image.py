import numpy as np
import sqlalchemy as sa
from tqdm import tqdm
import sys

def insert_image(patient, image_file):
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()

    person_tbl = sa.Table('person', metadata, autoload=True, autoload_with=engine)
    img_tbl    = sa.Table('img'   , metadata, autoload=True, autoload_with=engine)
    points_tbl = sa.Table('points', metadata, autoload=True, autoload_with=engine)


    person_sel = person_tbl.select(person_tbl.c.identifier == patient)
    person = engine.execute(person_sel).fetchone()

    img = read_image(image_file)

    conn = engine.connect()
    conn.execute('pragma foreign_keys=OFF')

    ## Insert the image metadata
    img_ins = img_tbl.insert()
    res = conn.execute(img_ins,
            person_id = person[0],
            type = 'TODO',
            dimensions  = ",".join([str(x) for x in img['dimensions']]),
            origin  = ",".join([str(x) for x in img['origin']]),
            spacing = ",".join([str(x) for x in img['spacing']])
            )
    image_id = res.inserted_primary_key[0]

    coords = get_coords(img['dimensions'], engine)

    trans = conn.begin()

    dimensions = img['dimensions']
    imgdata = img['img']
    data = []
    for x in tqdm(range(dimensions[0]), desc="Creating data"):
        for y in range(dimensions[1]):
            for z in range(dimensions[2]):
                cid = coords[x,y,z]
                value = imgdata[x,y,z]
                data.append({"img_id": image_id,
                             "coord_id": cid,
                             "value": value})

    pbar = tqdm(desc="Inserting into db", total=len(data))
    conn.execute(points_tbl.insert(), data)
    pbar.update(len(data))

    trans.commit()
    pbar.close()


def get_coords(dimensions, engine):
    coords_tbl = sa.Table('coords', sa.MetaData(), autoload=True, autoload_with=engine)

    add_missing_coords(dimensions, coords_tbl, engine)

    result = engine.execute(coords_tbl.select())
    #dimensions[0]+=2
    #dimensions[1]+=2
    #dimensions[2]+=2

    lookup = np.zeros(dimensions)
    for i in result:
        lookup[i[1],i[2],i[3]] = i[0]

    return lookup


def add_missing_coords(dimensions, coords_tbl, engine):
    dim_max_db = get_max_dimensions(engine, coords_tbl)

## This should work as an algorithm, for 2d case, imagine that we start with
# area O (as in original) and we want to expand it to the outer below in the
# figure.
#     y
#     |
#  y2 +--+-----+
#     |  |     |
#     |2 |     |
#  y1 +--+  1  |
#     |  |     |
#     |O |     |
#     +--+-----+-- x
#    0   x1    x2
#
# 1. Expand in x direction:
#    * let x go from x1 to x2
#    * let y go from 0 to max(y1,y2)
#    * create coord
# 2. Expand in y direction
#    * let y go from y1 to y2
#    * let x go from 0 to x1

    (x1, x2) = (dim_max_db[0], dimensions[0])
    (y1, y2) = (dim_max_db[1], dimensions[1])
    (z1, z2) = (dim_max_db[2], dimensions[2])

    data = []

    if x2 > x1:
        for x in tqdm(range(x1+1, x2), "Adding x"):
            for y in range(max(y1,y2)):
                for z in range(max(z1,z2)):
                    data.append({ 'x': x, 'y': y, 'z': z })

    if y2 > y1:
        for y in tqdm(range(y1+1, y2), "Adding y"):
            for x in range(x1):
                for z in range(max(z1,z2)):
                    data.append({ 'x': x, 'y': y, 'z': z })

    if z2 > z1:
        for z in tqdm(range(z1, z2), "Adding z"):
            for x in range(x1):
                for y in range(y1):
                    data.append({ 'x': x, 'y': y, 'z': z })

    if len(data)>1:
        print("Adding {} new datapoints".format(len(data)))
        engine.execute(coords_tbl.insert(), data)


def read_image(image_file):
    with open(image_file) as f:
        ## First 10 lines are headerlines
        for i in range(0, 10):
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
        #print("Len 1 is {}".format(len(img)))
        img = img.reshape(dims) # Reshape to the extracted dimensions
        #print("Len 2 is {}".format(len(img)))

    return {
        'img': img,
        'origin': origin,
        'dimensions': dims,
        'spacing': spacing,
        'n': n,
    }


def get_max_dimensions(engine, tbl):
    s = sa.select([sa.func.max(tbl.c.x),
                   sa.func.max(tbl.c.y),
                   sa.func.max(tbl.c.z)])
    res = engine.execute(s).fetchone()
    if res[0] == None:
        return (0,0,0)
    return res

if __name__ == '__main__':
    #engine = sa.create_engine('sqlite:///test.db', echo=False)
    #coords_tbl = sa.Table('coords', sa.MetaData(), autoload=True, autoload_with=engine)

    #img = read_image('/Users/johanviklund/Downloads/image-sample-data/500158_500022_fat_percent.vtk')
    #for n1 in img['img']:
    #    for n2 in n1:
    #        for n3 in n2:
    #            print(n3)
    #dimensions = (4,4,4)
    #add_missing_coords(dimensions, coords_tbl, engine)

    insert_image('pt087', '/Users/johanviklund/Downloads/image-sample-data/500158_500022_fat_percent.vtk')
