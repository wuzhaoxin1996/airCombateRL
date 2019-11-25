#!usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import numpy as np

def set_seed(seed):
	import numpy as np
	import random
	import tensorflow as tf
	
	np.random.seed(seed)
	random.seed(seed)
	tf.set_random_seed(seed)


def distance(agent1:list, agent2:list):
	dis = 0
	for pos1, pos2 in zip(agent1, agent2):
		dis = dis + (pos1 - pos2)*(pos1 - pos2)
	dis = math.sqrt(dis) 
	return dis