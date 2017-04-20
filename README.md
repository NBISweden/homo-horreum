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

### Visits and information about them

### VCF-files

### Metabolomics

### Images
