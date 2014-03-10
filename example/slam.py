# slam.py -- 2D EKM SLAM
# Copyright (C) 2014  Galois, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
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
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Implementation of the 2D EKM SLAM problem in Python.  Based on code
from:

  https://github.com/gpcz/python-drexel-slam

Modified to take input from the VREP car model, and dump reconstructed
track and beacon locations for use with the accuracy scoring scripts.
'''

import contextlib
import sys
import scipy.io
import numpy
import pylab
import math
from csv_helper import *
from slamutil import *
from ppamltracer import Tracer

# force the user to specify where input CSV files are an
# where output CSV files should go
if len(sys.argv) != 4:
    print "USAGE: slam.py END_TIME INPUT_DATA_DIR OUTPUT_DATA_DIR"
    exit(1)

data_input_directory = sys.argv[2]
data_output_directory = sys.argv[3]

# Constants for use in interpreting the Sensor data so that
# for a given point in time, know which sensor was sampled
GPS_FRAME = 1
MOVEMENT_FRAME = 2
LASER_FRAME = 3

# The dataset starts doing weird things, so we stop the simulation before
# the end.  TODO: make this NOT be hardwired
timeLimit = float(sys.argv[1])

# parameters for dealing with computed results
plotting_on = False
slam_landmarkfile = data_output_directory + '/slam_out_landmarks.csv'
slam_pathfile = data_output_directory + '/slam_out_path.csv'

# load the data set from the different CSV data files into a
# single data dictionary
dataset = unified_dataset([data_input_directory + '/slam_gps.csv', 
                           data_input_directory + '/slam_sensor.csv',
                           data_input_directory + '/slam_control.csv', 
                           data_input_directory + '/slam_laser.csv'])

# vehicle parameters
configuration = unified_dataset([data_input_directory + '/properties.csv'])

# get parameters from configuration that was dumped at simulation time to
# define vehicle geometry
L = configuration['L'][0][0]
h = configuration['h'][0][0]
b = configuration['b'][0][0]
a = configuration['a'][0][0]

# starting position: use first ground truth data point, and vehicle 
# orientation from the config file
startLong = dataset['GPSLon'][0][0]
startLat = dataset['GPSLat'][0][0]
startAngle = configuration['InitialAngle'][0][0]

PI = math.pi

init_est = numpy.ndarray(shape=(3,1), buffer=numpy.array([[float(startLong)],
                                                          [float(startLat)],
                                                          [float(startAngle)]]))

##
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
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
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

##
# This computes an array of points that correspond to blind dead reckoning.
#
# @param dataset The Matlab data set in question.
# @return An array of points corresponding to dead reckoning movement.
def DeadReckoning(dataset):
    dtRet = MakeArrayDiffIterator(dataset['Time'][0])
    velRet = MakeArrayIterator(dataset['Velocity'][0])
    steerRet = MakeArrayIterator(dataset['Steering'][0])
    vehicleModel = AckermanVehicle(L,h,b,a,init_est,velRet(),steerRet())

    result = init_est
    for i in range(1,len(dataset['Time'][0])-1):
        dt = dtRet()
        vehicleModel.predict(dt)
        result = numpy.append(result,numpy.zeros((result.shape[0],1)),1)
        result[0:2,i] = vehicleModel.state[0:2,0]
        if dataset['Sensor'][0][i] == MOVEMENT_FRAME:
            vehicleModel.new_steering(velRet(),steerRet())
    return result

##
# This computes a new state and probability estimate for the robot using the
# Extended Kalman Filter (EKF).
#
# @param state The current state vector.
# @param Pest The current probability vector.
# @param markID The ID of the observed landmark.
# @param z The observation vector.
# @return A vector containing a new state vector and a new probability vector.
def EKFUpdate(state,Pest,markID,z,phase):
    with phase.running():
        subt = numpy.subtract
        ndot = numpy.dot
        state = numpy.transpose(numpy.matrix(state))
        Jh = ObservationJacobian(state,markID)
        Jht = numpy.transpose(Jh)
        dx = state[markID*2+3,0]-state[0,0]
        dy = state[markID*2+4,0]-state[1,0]
        r = math.sqrt(dx*dx+dy*dy)
        H = [[r],[math.atan2(dy,dx)-state[2,0]+PI/2.0]]
        inno = numpy.subtract(z,H)
        inno[1,0] = NormalizeAngle(inno[1,0])
        V = numpy.identity(2)
        Vt = numpy.transpose(V)
        R = numpy.array([[0.1, 0],[0, (PI/180.0)*(PI/180.0)]])
        S = numpy.dot(Jh,numpy.dot(Pest,Jht))+numpy.dot(V,numpy.dot(R,Vt))
        K = numpy.dot(Pest,numpy.dot(numpy.transpose(Jh),numpy.linalg.inv(S)))
        wtf = numpy.dot(K,inno)
        state = state + wtf
        Pest = numpy.matrix(ndot(subt(numpy.identity(K.shape[0]),ndot(K,Jh)),Pest))
        return [state,Pest]

##
# Performs EKF-SLAM on the dataset and returns an array of points corresponding
# to the best guess of where the robot is for a given point in time.
#
# @param dataset The Matlab dataset.
# @return An array of points corresponding to the robot's location and heading.
def SLAM(dataset, tracer):
    with tracer.create_phase("initialization") as phase:
        with phase.running():
            dtRet = MakeArrayDiffIterator(dataset['Time'][0])
            velRet = MakeArrayIterator(dataset['Velocity'][0])
            steerRet = MakeArrayIterator(dataset['Steering'][0])
            laserRet = MakeArrayIterator(dataset['Laser'])
            intensityRet = MakeArrayIterator(dataset['Intensity'])
            vehicleModel = AckermanVehicle(L,h,b,a,init_est,velRet(),steerRet())
            factor = (15.0*PI/180.0)
            Pest = numpy.array([[0.01,0,0],[0,0.01,0],[0,0,factor]])
            Q = numpy.array([[0.5,0.0,0.0],[0,0.5,0.0],[0.0,0.0,factor*factor]])
            W = numpy.array([[1,0,0],[0,1,0],[0,0,1]])

    with contextlib.nested(
            tracer.create_phase("iteration"),
            tracer.create_phase("FindClumps"),
            tracer.create_phase("ClumpsToRangeBearing"),
            tracer.create_phase("FindClosestLandmark"),
            tracer.create_phase("FindGlobalLaserCoord"),
            tracer.create_phase("EKFUpdate"),
            ) as (
            iteration_phase,
            FindClumps_phase,
            ClumpsToRangeBearing_phase,
            FindClosestLandmark_phase,
            FindGlobalLaserCoord_phase,
            EKFUpdate_phase,
            ):
        with iteration_phase.running():
            result = init_est
            for i in range(1,len(dataset['Time'][0])-1):
                if dataset['Time'][0][i] >= dataset['Time'][0][0]+timeLimit:
                    break
                dt = dtRet()
                vehicleModel.predict(dt)
                result = numpy.append(result,numpy.zeros((result.shape[0],1)),1)
                result[:,i] = result[:,i-1]
                result[0:3,i] = vehicleModel.state[0:3,0]
                A = vehicleModel.jacobian(dt,(result.shape[0]-3)/2)
                At = numpy.transpose(A)
                Wt = numpy.transpose(W)
                Pest = numpy.dot(A,numpy.dot(Pest,At))-numpy.dot(W,numpy.dot(Q,Wt))
                if dataset['Sensor'][0][i] == MOVEMENT_FRAME:
                    vehicleModel.new_steering(velRet(),steerRet())
                if dataset['Sensor'][0][i] == LASER_FRAME:
                    laserMeasure = laserRet()
                    intensityMeasure = intensityRet()
                    clumps = FindClumps(laserMeasure,intensityMeasure,FindClumps_phase)
                    if len(clumps) > 0:
                        [clumpRange,clumpBearings] = ClumpsToRangeBearing(clumps,ClumpsToRangeBearing_phase)
                        for count in range(len(clumpRange)):
                            closest = FindClosestLandmark(result[0:3,i],
                                                          clumpRange[count],
                                                          clumpBearings[count],
                                                          MakeLandmarkArray(result),
                                                          FindClosestLandmark_phase,
                                                          FindGlobalLaserCoord_phase)
                            landmark = FindGlobalLaserCoord(result[0:3,i],
                                                            clumpRange[count],
                                                            clumpBearings[count],
                                                            FindGlobalLaserCoord_phase)
                            if closest != False:
                                [closeDist,theAddr] = closest
                                if closeDist > 2.0:
                                    [result,Pest,theAddr,Q,W] = AddNewLandmark(result,
                                                                               Pest,
                                                                               landmark,Q,W)
                            else:
                                [result,Pest,theAddr,Q,W] = AddNewLandmark(result,
                                                                           Pest,
                                                                           landmark,Q,W)
                            [newState,Pest] = EKFUpdate(result[:,i],
                                                        Pest,
                                                        theAddr,
                                                        numpy.array([[clumpRange[count]],
                                                                     [clumpBearings[count]]]),
                                                        EKFUpdate_phase)
                            result[:,i] = numpy.transpose(newState[:,0])
                            vehicleModel.plantState(newState[0:3,0])
            return result

# compute the true path (GPS locations)
truep = TruePath(dataset)

# compute the reconstructed path via EKM-SLAM
deadr = None
with Tracer() as tracer:
    deadr = SLAM(dataset, tracer)

#
# dump result file of reconstructed paths
#
with open(slam_pathfile, 'wb') as csvfile:
  path_writer = csv.writer(csvfile)
  path_writer.writerow(['SLAMGPSTime', 'SLAMLat', 'SLAMLon'])
  for i in range(numpy.shape(deadr)[1]):
    if dataset['Time'][0][i] >= dataset['Time'][0][0]+timeLimit:
        break
    if dataset['Sensor'][0][i] == GPS_FRAME:
        path_writer.writerow([dataset['Time'][0][i], deadr[0,i], deadr[1,i]])

[estLocsX,estLocsY] = MakeScatterplotArrays(deadr)

#
# dump reconstructed landmark locations
#
with open(slam_landmarkfile, 'wb') as csvfile:
  lm_writer = csv.writer(csvfile)
  lm_writer.writerow(['SLAMBeaconX', 'SLAMBeaconY'])
  for i in range(numpy.shape(estLocsX)[0]):
    lm_writer.writerow([estLocsX[i], estLocsY[i]])

if plotting_on:
  pylab.hold(True)
  pylab.plot(truep[0,:],truep[1,:],'g-',deadr[0,:],deadr[1,:],'r-')
  pylab.scatter(estLocsX,estLocsY,s=10,c='r')
  pylab.hold(False)
  pylab.show()
