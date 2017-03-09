import sqlalchemy as sa

def list_images():
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()

    person_tbl = sa.Table('person', metadata, autoload=True, autoload_with=engine)
    img_tbl    = sa.Table('img'   , metadata, autoload=True, autoload_with=engine)

    sel = sa.select([
        img_tbl.c.id,
        person_tbl.c.identifier,
        img_tbl.c.type,
        img_tbl.c.dimensions]).where(img_tbl.c.person_id==person_tbl.c.id)

    tbl_format = "{:>5} | {:>10} | {:>10} | {:>20}"
    print(tbl_format.format("ID", "Person", "Img Type", "Dimensions"))
    print(" -----+------------+------------+---------------------")

    for row in engine.execute(sel):
        print(tbl_format.format(*row))

if __name__ == '__main__':
    list_images()
