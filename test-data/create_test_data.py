import uuid
import random
import sqlalchemy as sa

def generate_identifier():
    return uuid.uuid4().hex[:5].upper()

def create_person():
    return (generate_identifier(),
            random.choice(["control","experiment"]),
            random.choice(["F","M"]))

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

def generate_expression_identifier():
    return "exp{:05}".format(random.randint(1,50000)) # For genes, 50000, transcripts=250000

def generate_expression_data():
    return (generate_expression_identifier(), int(abs(random.normalvariate(100, 50))))

def insert_variants(num=100):
    engine = sa.create_engine('sqlite:///test.db', echo=False)
    metadata = sa.MetaData()
    variant = sa.Table('variant', metadata, autoload=True, autoload_with=engine)
    conn = engine.connect()
    insert = variant.insert()
    trans = conn.begin()
    for i in range(num):
        v = generate_variant_data()
        conn.execute(insert,
                chromosome=v[0],
                pos=v[1],
                identifier=v[2],
                ref=v[3],
                alt=v[4],
                )
    trans.commit()

if __name__ == '__main__':
    print("Hello Cruel world!\n")
    insert_variants(1000)
