# test-slamutil.py -- unit tests for 2D EKM SLAM
# Copyright (C) 2014  Galois, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
#   3. Neither Galois's name nor the names of other contributors may be
#      used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL GALOIS OR OTHER
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import math
from slamutil import *

##
# Tests the Slam Utility Functions, which are used all over the EKF-SLAM system.
class TestSlamUtilFuncs(unittest.TestCase):
  def setUp(self):
    pass

  def test_FindClumpsSizeMismatch(self):
    self.assertEqual(FindClumps([1,2,3],[1,2]),
                     False)

  def test_FindClumpsNormal(self):
    self.assertEqual(FindClumps([1,2,3,1,4,0,0],[0,1,2,0,0,0,0]),
                     [[1,[2,3],[1,2]]])

  def test_FindClumps2(self):
    self.assertEqual(FindClumps([1,2,3,1,4,1,2,6,10,15,2,7],
                                [0,1,2,0,0,0,0,5,2,0,0,0]),
                     [[1,[2,3],[1,2]],[7,[6,10],[5,2]]])

  def test_DistanceFormula(self):
    self.assertEqual(DistanceFormula([1,2],[11,2]),10)

  def test_DistanceFormula2(self):
    self.assertEqual(DistanceFormula([1,1],[4,5]),5)

  def test_FindClosestLandmark(self):
    self.assertAlmostEqual(FindClosestLandmark(numpy.array([[0],[0],[0]]),
                                               10,0,[[1,-10]])[0],1)

  def test_FindClosestLandmark2(self):
    self.assertAlmostEqual(FindClosestLandmark(numpy.array([[0],[0],[0]]),
                                               10,0,[[1,-10]])[1],0)

  def test_FindClosestLandmark3(self):
    self.assertAlmostEqual(FindClosestLandmark(numpy.array([[0],[0],[0]]),
                                               10,0,[]),False)

  def test_FindClosestLandmark4(self):
    self.assertAlmostEqual(FindClosestLandmark(numpy.array([[0],[0],[0]]),
                                               10,0,[[50,50],[1,-10]])[0],1)

  def test_FindClosestLandmark5(self):
    self.assertAlmostEqual(FindClosestLandmark(numpy.array([[0],[0],[0]]),
                                               10,0,[[50,50],[1,-10]])[1],1)

  def test_FindClosestLandmark6(self):
    self.assertAlmostEqual(FindClosestLandmark(numpy.array([[0],[0],[0]]),
                                               9,0,[[1,-10],[50,50]])[0],
                           math.sqrt(2))

  def test_FindClumpsEdge(self):
    self.assertEqual(FindClumps([0,2,3,0],[0,0,0,1]),
                     [[3,[0],[1]]])

  def test_FindClumps2Edge(self):
    self.assertEqual(FindClumps([0,2,3,0],[0,0,2,0]),
                     [[2,[3,0],[2,0]]])

  def test_FindClumps3Edge(self):
    self.assertEqual(FindClumps([0,2,3,0],[0,4,0,0]),
                     [[1,[2,3,0],[4,0,0]]])

  def test_ClumpsToRangeBearing(self):
    self.assertEqual(ClumpsToRangeBearing([[300,[1,2],[2,2]]]),
                     [[1.5],[150.5*math.pi/180.0]])
if __name__ == '__main__':
  unittest.main()
