#!/usr/bin/env python
import sqlalchemy as sa

from database import DatabaseConnection

class ImageLister(DatabaseConnection):
    def list_images(self):
        person_tbl = self.get_table('person')
        img_tbl    = self.get_table('img')

        sel = sa.select([
            img_tbl.c.id,
            person_tbl.c.identifier,
            img_tbl.c.type,
            img_tbl.c.dimensions]).where(img_tbl.c.person_id==person_tbl.c.id)

        tbl_format = "{:>5} | {:>10} | {:>10} | {:>20}"
        print(tbl_format.format("ID", "Person", "Img Type", "Dimensions"))
        print(" -----+------------+------------+---------------------")

        for row in self.engine.execute(sel):
            print(tbl_format.format(*row))

if __name__ == '__main__':
    ImageLister().list_images()
