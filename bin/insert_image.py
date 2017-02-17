import numpy as np
import sqlalchemy as sa
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
    trans = conn.begin()

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

    # Next loop through all the points and insert them
    # TODO Double check that the coordinates are correct here, from what I
    # could read, the points first go from 0->max in x, increase y, and then
    # repeat (and finally for z)
    (x,y,z) = (0,0,0)
    dims = img['dimensions']
    points_ins = points_tbl.insert()
    for x in range(dims[2]):
        print("{:3d} ({})".format(x,dims[2]), file=sys.stderr)
        for y in range(dims[1]):
            for z in range(dims[0]):
                v = img['img'][x,y,z]
                print("{},{},{},{},{}".format(image_id,x,y,z,v))
                #conn.execute(points_ins,
                #        img_id = image_id,
                #        x = x,
                #        y = y,
                #        z = z,
                #        value = v,
                #)

    trans.commit()

def read_image(image_file):
    with open(image_file) as f:
        ## First 10 lines are headerlines
        for i in range(0, 10):
            (tag, *vals) = str(f.readline()).strip().split(' ')
            if tag == 'DIMENSIONS':
                dims = [int(v) for v in vals]
            elif tag == 'SPACING':
                spacing = [float(v) for v in vals]
            elif tag == 'ORIGIN':
                origin = [float(v) for v in vals]
            elif tag == 'POINT_DATA':
                n = int(vals[0])
            elif tag == 'SCALARS':
                if vals[1] == 'double':
                    dtype = np.dtype('>f8')
                else:
                    raise ValueError('Expected image of type double, got {}'.format(vals[1]))

        # Next read the image
        img = np.fromfile(f, dtype).astype('f8') # Read and convert to little endian
        img = img.reshape(dims[::-1]) # Reshape to the extracted dimensions

    return {
        'img': img,
        'origin': origin,
        'dimensions': dims,
        'spacing': spacing,
        'n': n,
    }


if __name__ == '__main__':
    insert_image('pt087', '/Users/johanviklund/Downloads/image-sample-data/500158_500022_fat_percent.vtk')
