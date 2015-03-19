#!/bin/bash -eu
rm -f index.db;
sqlite3 index.db < db_init.sql;
python driver.py;
