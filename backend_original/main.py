# -*- coding: UTF-8 -*-
'''
Description  : 
Author       : zyl
Date         : 2021-10-26 21:50:13
LastEditTime : 2021-11-08 10:23:15
FilePath     : \\splicetools\\backend_original\\main.py
'''

from lib import  Process

from  utils import  getConfig,Results
import sys

if __name__=='__main__':
    # video_full_path = "E:\\playground\\neikuijing\\20210125第一次.avi" 
    # projectId="34343"

    video_full_path = sys.argv[1]
    projectId = sys.argv[2]

    '获取处理参数'
    config = getConfig()
    centx =  config['centx']
    centy = config['centy']
    picWidth = config['picWidth']
    radiusMax = config['radiusMax']
    start = config['start']
    interval = config['interval']
    processPath = config['processPath']

    p = Process(video_full_path,projectId,processPath)
    
    '将视频转换成单帧图像'
    p.GetPic()
    '图像抽帧，抽取部分图像进行拼接，当取值为1时，全部图像均参与拼接'
    p.AnalyisImg(start, interval)


    '将圆形单帧图像，提取特定宽度之后，进行矩形展开，得到矩形图像'
    p.ImgProcess(centx, centy, picWidth, radiusMax)

    '将多个矩形图像按照时间序列进行拼接'
    imgPath=p.AllPicCombine()

    print (Results().ok(dict(success=True,imgPath=imgPath)))
    sys.stdout.flush()



