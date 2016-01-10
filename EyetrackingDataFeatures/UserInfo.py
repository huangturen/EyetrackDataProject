#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'baoyanma'


import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class UserInfo(object):
    """docstring for Eyetrackdata
	This class can be used to process Eyetrackdata"""

    def __init__(self, filename):
        super(UserInfo, self).__init__()
        self.fileName = filename
        self.userInfo = {}
        #dtype = [userName,gender,age,acurity,maineye]
        # 0-----female
        # 1-----male
        # -1-----left eye
        # 1-----right eye
    def readUserInfoFile(self):
        userInfo = np.recfromcsv(self.fileName)

        for item in userInfo:
            self.userInfo[item[0]] = int(item[4])
        return self.userInfo


