#!usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import torch
import torch.optim as optim
import torch.autograd as autograd 
import torch.nn.functional as F
from collections import deque
import os
import random
import sys
sys.path.append("..")
from memoryBuffer.replayBuffer import ReplayBuffer
from models.components import REGISTRY as registry_net_frame
from argument.dqnArgs import args
from utlis.utlis import set_seed

set_seed(args.seed)

# todo: 判断需要更全面，添加报错机制
net_frmae = registry_net_frame[args.net_frame]
if 'cnn' in args.net_frame:
    print("\nWarning: must def convs!")


class DQN(object):
    def __init__(self, state_dim, n_action):
        self.replay_buffer = ReplayBuffer(args.replay_size)
        self.epsilon = args.initial_epsilon
        self.state_dim = state_dim
        self.n_action = n_action

    def load_parms(self):
        raise NotImplementedError

    def create_network(self):
        raise NotImplementedError

    def create_training_method(self):
        raise NotImplementedError

    def perceive(self):
        raise NotImplementedError

    def train_network(self):
        raise NotImplementedError

    def sample_action(self):
        raise NotImplementedError

    def greedy_action(self):
        raise NotImplementedError

USE_CUDA = torch.cuda.is_available()
Variable = lambda *args, **kwargs: autograd.Variable(*args, **kwargs).cuda() if USE_CUDA else autograd.Variable(*args, **kwargs)

class DQN2013(DQN):
    def __init__(self, state_dim, n_action, is_train=False, is_based=False, scope=None):
        super(DQN2013, self).__init__(state_dim, n_action)
        self.epsilon = args.initial_epsilon
        self.scope = scope

        self.is_train = is_train
        self.is_based = is_based

        self.bool_defaule_action = False

        self.gamma = args.gamma
        self.learning_rate = 0.00005

        self.save_path = args.save_path
        self.save_name = args.file_name

        self.model = registry_net_frame[args.net_frame](self.state_dim, self.n_action)
        if USE_CUDA:
            self.model = self.model.cuda()
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.load_parms()
        
        
    def load_parms(self):
        if self.is_train:
            if self.is_based:
                self.epsilon = INITIAL_EPSILON * 0.5
                self.model.load_state_dict(torch.load(self.save_path + self.scope + self.save_name))
                #     print("Successfully loaded:", checkpoint.model_checkpoint_path)
                # else:
                #     print("Could not find old network weights")
        else:
            file_path = self.save_path + self.scope + self.save_name
            if os.path.exists(file_path):
                self.model.load_state_dict(torch.load(file_path))
                print("\n\n\nSuccessfully loaded:" + file_path)
            else:
                print("\n\n\n ========== LoadNone: default action for use_agent ===============")
                print("Could not find old network weights, the agent will keep choosing default_action = 1")
                print("=========== please make ture your save_path is correct ==============\n")
                self.bool_defaule_action = True
                

    def train(self):
        assert len(self.replay_buffer) >= args.batch_size
        batch_transition = self.replay_buffer.sample(args.batch_size)
        state, action, reward, next_state, done = map(np.array , zip(*batch_transition)) 

        state      = Variable(torch.FloatTensor(state.astype(np.float32)))
        next_state = Variable(torch.FloatTensor(next_state.astype(np.float32)))
        action     = Variable(torch.LongTensor(action))
        reward     = Variable(torch.FloatTensor(reward))
        done       = Variable(torch.FloatTensor(done))

        q_values      = self.model(state)
        next_q_values = self.model(next_state)

        q_value          = q_values.gather(1, action.unsqueeze(1)).squeeze(1)
        next_q_value     = next_q_values.max(1)[0]
        expected_q_value = reward + self.gamma * next_q_value * (1 - done)
        
        loss = (q_value - Variable(expected_q_value.detach())).pow(2).mean()            
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


    def perceive(self, state, action, reward, next_state, done):
        self.replay_buffer.append(state, action, reward,
                                   next_state, done)
        if len(self.replay_buffer) > args.replay_size:
            self.replay_buffer.pop()
        if len(self.replay_buffer) > args.batch_size:
            self.train()

    def store_data(self, state, action, reward, next_state, done):
        self.replay_buffer.append(state, action, reward,
                                   next_state, done)
        if len(self.replay_buffer) > args.replay_size:
            self.replay_buffer.pop()

    def egreedy_action(self, state):
        if self.epsilon > 0.1:
            self.epsilon = self.epsilon - 0.000005
        else:
            self.epsilon = self.epsilon * args.decay_rate

        if random.random() > self.epsilon:
            # state   = Variable(torch.FloatTensor(state.astype(np.float32)).unsqueeze(0), volatile=True)
            state   = Variable(torch.FloatTensor(state.astype(np.float32)).unsqueeze(0))
            q_value = self.model(state)
            action_max_value, index = torch.max(q_value, 1)
            action = index.item()
            # action  = q_value.max(1)[1].data[0]
#             print(action)
        else:
            action = random.randrange(self.n_action)
        return action

    def action(self, state):
        if self.bool_defaule_action:
            return 2
        else:
            # state   = Variable(torch.FloatTensor(state.astype(np.float32)).unsqueeze(0), volatile=True)
            state   = Variable(torch.FloatTensor(state.astype(np.float32)).unsqueeze(0))
            q_value = self.model(state)
            action_max_value, index = torch.max(q_value, 1)
            action = index.item()
            return action

    def save_model(self, iter_num=None):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        if iter_num is None:
            torch.save(self.model.state_dict(), self.save_path + self.scope + self.save_name)
        else:
            torch.save(self.model.state_dict(), self.save_path + str(iter_num) + self.scope + self.save_name)