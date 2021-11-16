# -*- coding: UTF-8 -*-
'''
Description  : 
Author       : zyl
Date         : 2021-11-04 15:55:07
LastEditTime : 2021-11-08 10:23:08
FilePath     : \\splicetools\\backend_original\\libmethod.py
'''

import numpy as np
import os
import shutil


def isContainChinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def ensure(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def rmtree(dir):
    isExists = os.path.exists(dir)
    if isExists:
        shutil.rmtree(dir)
    else:
        return 0


def rmList(dirList):
    # 删除过程图片，仅保留拼接图片
    try:
        for path in dirList:
            if os.path.isdir(path):
                rmtree(path)
            elif os.path.isfile(path) and os.path.exists(path):
                os.remove(path)
            # else:
            #     pass

    except Exception as e:
        # print(e)
        pass


def mean2(x):
    y = np.sum(x) / np.size(x)
    return y


def corr2(a, b):
    a = a - mean2(a)
    b = b - mean2(b)

    r = (a*b).sum() / np.sqrt((a*a).sum() * (b*b).sum())
    return r


def stitch2im(im1, im2, kp=5):
    # kp: patch size
    # Reading two images
    F = im1  # First image
    S = im2  # Second image
    rows, cols = F.shape
    rows2, cols2 = S.shape
    # Saving the patch(rows x 5 columns) of second(S) images
    S1 = S[:, :kp]
    # Performing Correlation i.e. Comparing the (rows x 5 column) patch of two images
    tmp1 = np.zeros([cols-kp, 1])
    for k in range(cols-kp):
        F1 = F[:, k:k+kp]
        tmp1[k] = corr2(F1, S1)  # comparing the patches using correlation.

    mxid = np.argmax(tmp1)
    # Determining new column for final stitched image.
    n_cols = mxid + cols2
    st_im1 = F[:, :mxid]
    st_im2 = S
    # Determining the Final Stitched image.
    fin_img = np.append(st_im1, st_im2, axis=1)
    return fin_img
