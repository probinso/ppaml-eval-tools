# CSV helper
# Copyright (C) 2014  Galois, Inc.
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this library.  If not, see <http://www.gnu.org/licenses/>.
#
# To contact Galois, complete the Web form at <http://corp.galois.com/contact/>
# or write to Galois, Inc., 421 Southwest 6th Avenue, Suite 300, Portland,
# Oregon, 97204-1622.

import csv
import numpy as np

# given a set of CSV file filenames, each with associated headers,
# load each and merge the resulting dictionaries into a single
# unified dictionary.  Note that column name collisions are NOT
# gracefully resolved across the data sets that come from different
# CSV files.  The only legitimate instance of duplicated column names
# is within a single file to indicate the presence of a 2D matrix,
# and that is handled in the individual file read_csv_to_numpy_dict()
# function.
def unified_dataset(fnames):
    dataset = {}
    for fname in fnames:
        x = read_csv_to_numpy_dict(fname)
        for key in x.keys():
            dataset[key] = x[key]
    return dataset

def read_csv_to_numpy_dict(fname):
    dat = csv.reader(open(fname,'rb'))

    # reader header
    header = dat.next()

    # headings that repeat in a sequence indicate that columns are related
    # and correspond to a matrix, not a set of individual vectors
    heading_widths = {}
    heading_names = []
    i = 1
    last_seen = ''
    for heading in header:
        if heading != last_seen:
            if last_seen != '':
                heading_widths[last_seen] = i
                heading_names.append(last_seen)
                i = 1
        else:
            i = i + 1
        last_seen = heading
    heading_widths[last_seen] = i
    heading_names.append(last_seen)

    # the data dictionary to return
    data_dict = {}

    # record contents into a list of lists
    contents = []
    for row, record in enumerate(dat):
        contents.append(map(float,record))

    # assuming the contents were numeric, make a
    # 2D numpy array out of it
    contents_np = np.array(contents)

    # now extract the columns in the appropriate width chunks
    # and populate the data dictionary
    colnum = 0
    for heading in heading_names:
        width = heading_widths[heading]
        if width==1:
            data_dict[heading] = np.transpose(contents_np[:,colnum:(colnum+width)])
        else:
            data_dict[heading] = contents_np[:,colnum:(colnum+width)]
        colnum = colnum+width

    return data_dict
