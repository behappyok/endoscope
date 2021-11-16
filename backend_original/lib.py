# -*- coding: UTF-8 -*-
import numpy as np
import skimage
from skimage import transform
import cv2
import os
import time
from PIL import Image
import shutil
from utils import log, dbLog
from libmethod import stitch2im, ensure, rmList, isContainChinese
from pathlib import Path
import math
from xpinyin import Pinyin


class Process:

    def __init__(self, video_full_path, projectId, processPath):
        self.projectId = projectId
        # self.projectId = shortuuid.ShortUUID().random(8)
        self.video_full_path = video_full_path
        fileNameWithoutExt = Path(video_full_path).stem
        # 在文件名为中文的情况下建立的工作路径，cv2.imread无法正常运行，输出的结果为None
        if isContainChinese(fileNameWithoutExt):
            self.processPath = os.path.join(
                processPath, Pinyin().get_pinyin(fileNameWithoutExt))
        else:
            self.processPath = os.path.join(processPath, fileNameWithoutExt)
        dbLog('insert', 'projectId', self.projectId)
        dbLog(self.projectId, 'file', os.path.basename(video_full_path))
        self.dir_Pic = os.path.join(self.processPath, "Pic")
        self.dir_AnyPic = os.path.join(self.processPath, "AnyPic")
        self.dir_CutPic = os.path.join(self.processPath, "CutPic")
        self.dir_AllCombine = os.path.join(self.processPath, "AllCombine.jpg")
        rmList([self.dir_Pic,self.dir_AnyPic,self.dir_CutPic,self.dir_AllCombine])
        ensure(self.dir_Pic)
        ensure(self.dir_AnyPic)
        ensure(self.dir_CutPic)

    def GetPic(self):
        '将视频转换成单帧图像'
        cap = cv2.VideoCapture(self.video_full_path)
        cap.isOpened()  # 判断视频对象是否成功读取，成功读取视频对象返回True
        num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        dbLog(self.projectId, 'stage', 1)
        dbLog(self.projectId, 'total', num_frames)
        for n in range(0, math.floor(num_frames)):
            dbLog(self.projectId, 'current', n+1)
            # 按帧读取视频，返回值ret是布尔型，正确读取则返回True，读取失败或读取视频结尾则会返回False。
            # frame为每一帧的图像，这里图像是三维矩阵，即frame.shape = (640,480,3)，读取的图像为BGR格式。
            success, frame = cap.read()
            im = Image.fromarray(frame)
            im.save(os.path.join(self.dir_Pic, "video_" + str(n)+".jpg"))
            log('stage 1:'+"video_" + str(n)+".jpg")
        cap.release()

    def AnalyisImg(self, start, interval):  # 等差数列提取图像，并复制到AnyPic文件夹
        anyPicdir = self.dir_AnyPic
        filedir = self.dir_Pic
        pathlist = next(os.walk(filedir))[2]
        pathlist.sort(key=lambda x: int(x.split('_')[1][:-4]))
        fileNum = len(pathlist)-start+1
        ImagNum = np.arange(start, start+fileNum -1 , interval)
        for i in ImagNum:
            filepath = filedir + '\\' + pathlist[i-1]
            new_file_path = anyPicdir + '\\' + pathlist[i-1]
            shutil.copy(filepath, new_file_path)
        return 0

    # image preprocessing

    def ImgProcess(self, centx, centy, width, rmax):
        # center:中心点 cenx = 485.5; ceny = 753.5;
        # width:圆环宽度
        # rmax: 圆环半径限制

        cutPicdir = self.dir_CutPic
        filedir = self.dir_AnyPic

        pathlist = next(os.walk(filedir))[2]
        pathlist.sort(key=lambda x: int(x.split('_')[1][:-4]))
        fileNum = len(pathlist)
        dbLog(self.projectId, 'stage', 2)
        dbLog(self.projectId, 'total', fileNum)
        for n in range(0, fileNum):
            dbLog(self.projectId, 'current', n+1)
            PicPath = os.path.join(filedir, pathlist[n])
            img = cv2.imread(PicPath, cv2.IMREAD_COLOR)
            r = rmax-np.array(range(width))
            num = np.round(r * np.pi / 180)  # 单位角度对应的弧长，也即单位角度对应的像素点个数：半径乘以弧度角
            # the final img length
            mn = np.int(np.round(np.mean(np.unique(num))*360))
            start = time.time()
            for i in range(width-1):
                klen = np.int(360 * num[i])
                tem_img = np.zeros([klen, 1, 3])

                j = np.arange(0, klen, 1)
                xj = np.round(
                    centx + r[i] * np.cos(j * np.pi / (num[i] * 180)))
                yj = np.round(
                    centy + r[i] * np.sin(j * np.pi / (num[i] * 180)))
                for h in j:

                    tem_img[h] = img[np.int(xj[h]), np.int(yj[h])]
                # standardize the img size
                tem_img = skimage.transform.resize(tem_img, [mn, 1, 3])
                if i == 0:
                    newimg = tem_img
                else:
                    newimg = np.append(newimg, tem_img, axis=1)

            end = time.time()
            log("第 "+str(n+1)+" 图的循环运行时间:%.2f秒" % (end - start))
            dbLog(self.projectId, 'timeElapsed', end - start)
            newimgpath = os.path.join(self.dir_CutPic, 'cut_' + pathlist[n])
            cv2.imwrite(newimgpath, newimg)

            # print(n)
        return 0

    def AllPicCombine(self):

        thisPath, folders, pathlist = next(os.walk(self.dir_CutPic))
        pathlist.sort(key=lambda x: int(x.split('_')[2][:-4]))
        dbLog(self.projectId, 'stage', 3)
        dbLog(self.projectId, 'total', len(pathlist) )
        if len(pathlist) > 0:
            for i in range(0, len(pathlist)):
                dbLog(self.projectId, 'current', i+1 )
                log("stage 3: 合并第 "+str(i+1)+" 图" )
                picPath = os.path.join(self.dir_CutPic, pathlist[i])
                img = cv2.imread(picPath, cv2.IMREAD_COLOR)
                imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                if i == 0:
                    finalImg = imgGray
                else:
                    finalImg = stitch2im(finalImg, imgGray, kp=5)
            imrotate = np.rot90(finalImg, k=-1)
            cv2.imwrite(self.dir_AllCombine, imrotate)
            ret = self.dir_AllCombine
        else:
            ret = None
        rmList([self.dir_Pic, self.dir_AnyPic, self.dir_CutPic])
        return ret
