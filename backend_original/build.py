'''
Description  : 
Author       : zyl
Date         : 2021-11-05 15:49:55
LastEditTime : 2021-11-08 11:15:40
FilePath     : \\splicetools\\backend_original\\build.py
'''
import info 
import lib 
import libmethod
import main
import utils

import shutil
 
import os
pathSrc = os.path.join(__file__,'..\\__pycache__' )
pathDest = os.path.join(__file__,'..\\..\\backend' )
# command = 'copy  {0}\\*.pyc {1}'.format(pathSrc,pathDest )
# os.system (command)
dir,folders,files  =  next(os.walk(pathSrc))
for file  in files:
    shutil.copy(os.path.join(pathSrc,file),os.path.join(pathDest,file.split('.')[0]+'.pyc' ))