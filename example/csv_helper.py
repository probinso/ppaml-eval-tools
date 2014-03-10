# CSV helper
# Copyright (C) 2014  Galois, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#   3. Neither Galois's name nor the names of other contributors may be used to
#      endorse or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL GALOIS OR OTHER CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
