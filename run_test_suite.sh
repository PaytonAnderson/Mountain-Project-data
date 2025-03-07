#!/bin/sh

ARGC=$#

if [ $ARGC -ne 3 ]; then
    echo Usage: $0 source_db_path python_interpreter drop_review_chance
    exit 1
fi

SOURCE_DB=$1
PY_INTERP=$2
DROP_CHANCE=$3

DB_NAME=TEMP.$(uuidgen).db

sqlite3 $1 .dump | $2 dataset_preparation.py $3 | sqlite3 $DB_NAME

echo Created DB file $DB_NAME
echo All routes were kept, and $DROP_CHANCE reviews were removed per review.
