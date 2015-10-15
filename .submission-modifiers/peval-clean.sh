#!/bin/bash

set -x

sqlite3 ~/.local/share/ppaml/index.db \
  "pragma foreign_keys = ON;
   delete from engine;
   delete from solution;
   delete from dataset;"

rm -rf /tmp/peval*

