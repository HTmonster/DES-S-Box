#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   ____    ____    ______________
#  |    |  |    |  |              |
#  |    |  |    |  |_____    _____|
#  |    |__|    |       |    |
#  |     __     |       |    |
#  |    |  |    |       |    |
#  |    |  |    |       |    |
#  |____|  |____|       |____|
#
#
# @purpose:DES sbox 生成 （满足准则1,2,3,4）
# @Date    : 2018-10-12 创建 实现规则1,2
#            2018-10-19 增加规则3,4 增加局部优化
#            2018-10-22 修复死胡同BUG
# @Author  : 辉涛

import numpy as np
from random import choice


# p2卡诺图相邻表 i与第i个内的数字(二进制)有且仅有一位不同  例： 0000 （1000,0100,0010,0001)
T_dif1 = ((8, 4, 2, 1),  (9, 5, 3, 0),  (10, 6, 0, 3),  (11, 7, 1, 2),
          (12, 0, 6, 5), (13, 1, 7, 4), (14, 2, 4, 7),  (15, 3, 5, 6),
          (0, 12, 10, 9), (1, 13, 11, 8), (2, 14, 8, 11), (3, 15, 9, 10),
          (4, 8, 14, 13), (5, 9, 15, 12), (6, 10, 12, 15), (7, 11, 13, 14))

# p4 规则4中一行中可取的 1yz0 的值 位置
T_1yz0 = ((8, 10, 12, 14), (9, 11, 13, 15), (8, 10, 12, 14), (9, 11, 13, 15),
          (8, 10, 12, 14), (9, 11, 13, 15), (8, 10, 12, 14), (9, 11, 13, 15),
          (0, 2, 4, 6), (1, 3, 5, 7), (0, 2, 4, 6), (1, 3, 5, 7),
          (0, 2, 4, 6), (1, 3, 5, 7), (0, 2, 4, 6), (1, 3, 5, 7),)

# 尝试的的界限
i_MAX = 1000

# 根据候选值表生成一行


def getLine(cT):

    T_candi = cT  # 16x16 每个位置候选的值 禁用 -1

    T_num = [16] * 16  # 每个位置候选值的数量 已填充 inf

    rst = [-1] * 16  # 结果数组

    slct_pos = 0  # 选择的位置
    slct_num = 0  # 选择的填充数

    # 分别对16个位置填充
    for i in range(16):

        # 更新候选数量
        for j in range(16):
            if T_num[j] <= 16:
                num = (T_candi[j] != -1).sum()
                # num = len(T_candi[j][np.where(T_candi[j] >= 0)])
                # 未填充的已经没有候选了 失败
                if num == 0:
                    # print("False", slct_num)
                    return False
                T_num[j] = num

        # 先填充剩余数量最少的位置
        # slct_pos = T_num.index(min(T_num))
        slct_pos = choice([i for i in range(16) if T_num[i] == min(T_num)])
        T_num[slct_pos] = float('inf')

        # 候选值中 随机选一
        slct_num = choice(
            T_candi[slct_pos][np.where(T_candi[slct_pos] != -1)])

        # 写入结果
        rst[slct_pos] = slct_num

        # p1 p2 禁用已经选的
        T_candi[:, slct_num] = -1

        for j in range(4):
            # p2规则 卡诺图上下左右位置 禁用差一位的值
            T_candi[slct_pos ^ 0b0001][T_dif1[slct_num][j]] = -1
            T_candi[slct_pos ^ 0b0010][T_dif1[slct_num][j]] = -1
            T_candi[slct_pos ^ 0b0100][T_dif1[slct_num][j]] = -1
            T_candi[slct_pos ^ 0b1000][T_dif1[slct_num][j]] = -1

            # p3规则 x^001100禁用差一位的值
            T_candi[slct_pos ^ 0b0110][T_dif1[slct_num][j]] = -1

    return rst


def getL0():
    # 正常候选值
    T = np.array([[i for i in range(16)] for j in range(16)])
    return getLine(T)


def getL1(L0):
    T = np.array([[i for i in range(16)] for j in range(16)])

    # p2 禁用与L0中相同,相差一位的值
    for i in range(16):
        T[i][L0[i]] = -1
        for j in range(4):
            T[i][T_dif1[L0[i]][j]] = -1

    return getLine(T)


def getL2(L0, L1=None):
    T = np.array([[i for i in range(16)] for j in range(16)])

    for i in range(16):
        # p2 禁用与L0中相同的值
        T[i][L0[i]] = -1

        for j in range(4):
            # p2 禁用与L0中相差一位的值
            T[i][T_dif1[L0[i]][j]] = -1

            # p4 禁用 x^11yz00 即L0中 1yz0 相等的值
            T[i][L0[T_1yz0[i][j]]] = -1

    # 可选条件 局部优化性 同列不等
    if L1:
        for i in range(16):
            T[i][L1[i]] = -1
    return getLine(T)


def getL3(L1, L2, L0=None):
    T = np.array([[i for i in range(16)] for j in range(16)])

    for i in range(16):
        # p2禁用与L1,L2中相同的值
        T[i][L1[i]] = -1
        T[i][L2[i]] = -1

        for j in range(4):
            # p2禁用与L1,L2中相差一位的值
            T[i][T_dif1[L1[i]][j]] = -1
            T[i][T_dif1[L2[i]][j]] = -1

            # p4 禁用 x^11yz00 即L1中 1yz0 相等的值
            T[i][L1[T_1yz0[i][j]]] = -1

    # 可选条件 局部优化性 同列不等
    if L0:
        for i in range(16):
            T[i][L0[i]] = -1

    return getLine(T)


# 分别获得L0,L1,L2,L3构成Sbox


def getSbox(optimize=False):
    L0 = L1 = L2 = L3 = None

    # 开启局部优化
    if(optimize):
        while not L3:
            L0 = L1 = L2 = None
            i = 0

            while not L0:
                L0 = getL0()

                i = i + 1
                if i > i_MAX:
                    break

            while not L1 and L0:
                L1 = getL1(L0)

                i = i + 1
                if i > i_MAX:
                    break

            while not L2 and L0 and L1:
                L2 = getL2(L0, L1)

                i = i + 1
                if i > i_MAX:
                    break

            while not L3 and L1 and L2 and L0:
                L3 = getL3(L1, L2, L0)

                i = i + 1
                if i > i_MAX:
                    break

    # 默认不开启
    else:
        while not L3:
            L0 = L1 = L2 = None
            i = 0

            while not L0:
                L0 = getL0()

                i = i + 1
                if i > i_MAX:
                    break

            while not L1 and L0:
                L1 = getL1(L0)

                i = i + 1
                if i > i_MAX:
                    break

            while not L2 and L0:
                L2 = getL2(L0)

                i = i + 1
                if i > i_MAX:
                    break

            while not L3 and L1 and L2:
                L3 = getL3(L1, L2)

                i = i + 1
                if i > i_MAX:
                    break

    S = np.array([L0, L1, L2, L3])

    return(S)


# 对Sbox测试准则2,3,4


def test(S):
    # abcdef
    # 000000-111111

    for L in range(4):
        for R in range(16):
            # p2 输入改变一位 输出改变两位
            f1 = bin(S[L][R] ^ S[L ^ 0b10][R]).count('1')  # a变
            f2 = bin(S[L][R] ^ S[L][R ^ 0b1000]).count('1')  # b
            f3 = bin(S[L][R] ^ S[L][R ^ 0b0100]).count('1')  # c
            f4 = bin(S[L][R] ^ S[L][R ^ 0b0010]).count('1')  # d
            f5 = bin(S[L][R] ^ S[L][R ^ 0b0001]).count('1')  # e
            f6 = bin(S[L][R] ^ S[L ^ 0b01][R]).count('1')  # f

            # p3 x^001100 相差两位以上
            y = bin(S[L][R] ^ S[L][R ^ 0b0110]).count('1')  # x^001100

            # p4 x^11yz00 不同
            y1 = S[L][R] == S[L ^ 0b10][R ^ 0b1000]  # 110000
            y2 = S[L][R] == S[L ^ 0b10][R ^ 0b1010]  # 110100
            y3 = S[L][R] == S[L ^ 0b10][R ^ 0b1100]  # 111000
            y4 = S[L][R] == S[L ^ 0b10][R ^ 0b1110]  # 111100

            if(f1 < 2 or f2 < 2 or f3 < 2 or f4 < 2 or f5 < 2 or f6 < 2):
                print("error %d行%d不符合p2" % (L, R))
                return False
            if(y < 2):
                print("error %d行%d不符合p3" % (L, R))
                return False
            if(y1 or y2 or y3 or y4):
                print("error %d行%d不符合p4" % (L, R))
                return False

    # print("p2,p3,p4 passed!!")

    return True

if __name__ == '__main__':

    # 生成输出8个 sbox 并测试
    s8 = []
    for i in range(8):
        S = getSbox(True)  # 开启局部优化 若速度较慢 可以关闭
        print(">>第%d个box" % (i + 1))
        print(S)
        s8.append(S)

    match = []
    for i in range(8):
        match.append(test(s8[i]))
    print("检测结果")
    print(match)

    input()
