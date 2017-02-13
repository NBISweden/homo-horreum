import uuid
import random
import sqlalchemy as sa


engine   = sa.create_engine('sqlite:///test.db', echo=False)
metadata = sa.MetaData()

person  = sa.Table('person', metadata, autoload=True, autoload_with=engine)
variant = sa.Table('variant', metadata, autoload=True, autoload_with=engine)
person_variant = sa.Table('person_variant', metadata, autoload=True, autoload_with=engine)

conn = engine.connect()

def get_all_patients():
    select = sa.sql.select([person])
    result = conn.execute(select)
    out = []
    for row in result:
        out.append( tuple(row) )
    return out

chromosomes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
        19, 20, 21, 22, 'X', 'Y']

def generate_vcf_identifier():
    return "fs{:08d}".format(random.randint(1,100000000))

def generate_variant_data():
    ref = random.choice(["A","C","T","G"])
    alt = random.choice([x for x in ["A","C","T","G"] if x != ref])
    return (random.choice(chromosomes),  # Chromosome
            random.randint(1,100000000), # Position
            generate_vcf_identifier(),   # SNP id
            ref, alt)

def create_person_variants(num=100):
    persons = get_all_patients()

    insert_variant = variant.insert()
    insert_link    = person_variant.insert()

    trans = conn.begin()
    for i in range(num):
        v = generate_variant_data()

        res = conn.execute(insert_variant, chromosome=v[0], pos=v[1], identifier=v[2], ref=v[3], alt=v[4])
        variant_key = res.inserted_primary_key[0]
        for p in persons:
            if random.random() < 0.4:
                conn.execute(insert_link, person_id=p[0], variant_id=variant_key)
    trans.commit()


if __name__ == '__main__':
    create_person_variants(500)
