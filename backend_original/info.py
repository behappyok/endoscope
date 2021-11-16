# -*- coding: UTF-8 -*-
'''
Description  : 
Author       : zyl
Date         : 2021-10-28 10:46:36
LastEditTime : 2021-11-08 10:22:56
FilePath     : \\splicetools\\backend_original\\info.py
'''

import sys
from cv2 import cv2
from utils import Results
import os


def get_source_info_opencv(source_name):
    return_value = 0
    if(not os.path.exists(source_name)):
        return Results().err('文件不存在')
    try:
        cap = cv2.VideoCapture(source_name)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        num_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = num_frames/fps
        # print("duration:{} \nwidth:{} \nheight:{} \nfps:{} \nnum_frames:{}".format(duration, width, height, fps, num_frames))
        return_value = dict(duration=duration, width=width,
                            height=height, fps=fps, num_frames=num_frames)
        return Results().ok(return_value)
    except (OSError, TypeError, ValueError, KeyError, SyntaxError) as e:
        # print("init_source:{} error. {}\n".format(source_name, str(e)))
        return_value = -1
        return Results().err(return_value)

if __name__=='__main__':
    fullPath = sys.argv[1]
    print(get_source_info_opencv(fullPath))
    sys.stdout.flush()
