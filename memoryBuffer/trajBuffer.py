#!usr/bin/env python3
# -*- coding: utf-8 -*-

# 策略梯度算法使用的 经验缓存池
import sys
sys.path.append("..")
from utlis.utlis import set_seed
from argument.dqnArgs import args
# if 
set_seed(args.seed)