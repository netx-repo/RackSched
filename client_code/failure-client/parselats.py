#!/usr/bin/python3

import sys
import os
import numpy as np
from scipy import stats


class Lat(object):
    def __init__(self, fileName):
        f = open(fileName, 'rb')
        a = np.fromfile(f, dtype=np.uint64)
        self.reqTimes = a.reshape((a.shape[0], 1))
        f.close()

    def parseQueueTimes(self):
        return self.reqTimes[:, 0]

    def parseSvcTimes(self):
        return self.reqTimes[:, 1]

    def parseSojournTimes(self):
        return self.reqTimes[:, 0]


if __name__ == '__main__':
    def getLatPct(typeOfLats, latsFile):
        assert os.path.exists(latsFile)

        latsObj = Lat(latsFile)
        sjrnTimes = [l for l in latsObj.parseSojournTimes()]
        print(sjrnTimes)

    typeOfLats = sys.argv[1]
    latsFile = sys.argv[2]
    getLatPct(typeOfLats, latsFile)
