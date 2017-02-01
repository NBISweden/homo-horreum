import uuid
import random

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

def generate_expression_data():
    pass
