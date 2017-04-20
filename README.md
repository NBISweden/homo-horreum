# homo-horreum

## High level overview

General note on database structure.

All data is associtated with Persons so to insert anything the persons that
data applies to has to be inserted first.

There are separate _modules_ for each type of data, genomics, metabolomics,
proteomics and so forth. Currently only the genomics and metabolomics modules
are implemented.

More freeform data, blood pressure or other clinical measurements for example,
always have to be associated with a visit. This includes cases where there's
more freeform information related to for example metabolomics data, then a
visit has to be defined for that and then you can add that to the database.


## Prerequisites

Python 3 and pip preferably with virtualenv.

To install prerequisites using virtualenv (replace `venv` with whatever you
feel like):

```shell
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```


## Initialize database

```shell
$ alembic upgrade head
```

## Insert data into database

### Persons

```shell
$ bin/person_insert.py -h
usage: person_insert.py [-h] --identifier IDENTIFIER --group GROUP --sex SEX

Insert a perons in the database

optional arguments:
  -h, --help            show this help message and exit
  --identifier IDENTIFIER
                        Identifier for the person
  --group GROUP         Experimental group
  --sex SEX             The sex, M, F or U
```

```shell
$ bin/person_isnert.py --identifier H1234 --group Control --sex U
```

### VCF-files

The inserter assumes that the genotyping data is in the extra columns of the
vcf standard. One column for each person with the person identifier as the
column header. Remember to add these persons to the database before running
the script.

```shell
$ bin/vcf_insert.py -h
usage: vcf_insert.py [-h] --file FILE

Insert an vcf data in the database

optional arguments:
  -h, --help   show this help message and exit
  --file FILE  VCF-file containing data
```

```shell
$ bin/vcf_insert.py --file file.vcf
```

### Metabolomics

Metabolomics data is tab-separated files with persons as rows and metabolites
as columns. Since there can be multiple different techniques used for the same
sample you have to supply a _note_ for each insertion. Each file will be
imported as one _metabolomics experiment_.

```shell
$ bin/metabolomics_insert.py -h
usage: metabolomics_insert.py [-h] --file FILE --note NOTE

Insert metabolomics data

optional arguments:
  -h, --help   show this help message and exit
  --file FILE  TSV with metabolomics data
  --note NOTE  Information about this metabolomics experiment
```

```shell
$ bin/metabolomics_insert.py --file metabolomcs.tsv --note lcms-data
```

### Images

Images are stored as blobs more or less as the vtk-file is reprenseted. Though
the header of the vtk file is inserted into a separate table and the binary
image information is then inserted as a blob.

```shell
$ bin/image_insert.py -h
usage: image_insert.py [-h] --person PERSON --image IMAGE --type TYPE

Insert an image in the database

optional arguments:
  -h, --help       show this help message and exit
  --person PERSON  Person ID
  --image IMAGE    VTK image file
  --type TYPE      Type of image (fat, water, etc.)
```

```shell
$ bin/image_insert.py --person H1234 --image file.vtk --type fat
```

There are also scripts for exporting and listing images in the database.

### Visits and information about them


