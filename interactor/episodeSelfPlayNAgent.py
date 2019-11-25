#!usr/bin/env python3
# -*- coding: utf-8 -*-

import xlwt
import time
import tensorflow as tf
import sys
sys.path.append('..')
import utlis.alloc as alloc
from argument.dqnArgs import args


workbook=xlwt.Workbook(encoding='utf-8')
showbook = xlwt.Workbook(encoding="utf-8")
trainsheet=workbook.add_sheet('train', cell_overwrite_ok=True)      #训练数据
showsheet = showbook.add_sheet('show',cell_overwrite_ok=True)       #使用保存网络的数据
row0 = [u'episode',u'step',u'reward',u'success']
row1 = ['PATH_NUM','b_x','b_y','b_heading', 'b_bank','r_x','r_y','r_heading','ATA','AA']
for i in range(len(row0)):
    trainsheet.write(0, i, row0[i])
    showsheet.write(0,i,row0[i])


def run_AirCombat_selfPlay(env, train_agent_list, use_agent_list, train_agent_name):  
    '''
    Params：
        env:                class object
        train_agent:        class object
        use_agent:          class object
        train_agent_name:   str

    主要逻辑：
        将红、蓝智能体分为训练智能体、使用智能体进行训练；
        使用 utlis.selfPlayUtlis模块 进行 红&蓝 与 训练&使用 之间的转换,
        完成训练和测试功能，并可以进行可视化。
    '''

    # ====  loop start ====
    if train_agent_list[0].is_train:       #训练模式(else:直接加载模型)
        suc_num = 0

        # #经验池存储数据
        # for episode in range(args.STORE):
        #     state_train_agent, state_use_agent = alloc.env_reset(env, train_agent_name)

        #     if episode % 100 == 0:
        #         print('data collection: {} ,buffer capacity: {} '.format(episode / 100,
        #                                                                  train_agent.replay_buffer.size))
        #     while True:
        #         action_train_agent = train_agent.egreedy_action(state_train_agent)
        #         # levin-red-action
        #         action_use_agent = use_agent.action(state_use_agent)
        #         #action_use_agent = 2

        #         next_state_train_agent, next_state_use_agent, reward_train_agent, done = alloc.env_step(env, action_train_agent, action_use_agent, train_agent_name)
        #         train_agent.store_data(state_train_agent, action_train_agent, reward_train_agent, next_state_train_agent, done)
        #         state_train_agent = next_state_train_agent
        #         if done:
        #             break
        #     if(train_agent.replay_buffer.size >= 100000):
        #         break

        #开始训练
        for episode in range(args.EPISODE):
            e_reward = 0
            step = 0
            state_train_agent, state_use_agent = alloc.env_reset(env, train_agent_name)
            while True:
                action_train_agent = train_agent.egreedy_action(state_train_agent)
                action_use_agent = use_agent.action(state_use_agent)
                #action_use_agent = 2
                next_state_train_agent, next_state_use_agent, reward, done = alloc.env_step(env, action_train_agent, action_use_agent, train_agent_name)

                e_reward += reward
                train_agent.perceive(state_train_agent, action_train_agent, reward, next_state_train_agent, done)
                state_train_agent = next_state_train_agent
                step += 1
                if done:
                    #print('Episode: ', episode, 'Step', step, "Reward:", e_reward, 'Success',env.success,train_agent.epsilon,env.acts)
                    break

            #训练过程中的阶段测试模式
            if (episode % args.TRAIN == 0):
                train_agent.saver.save(train_agent.session, train_agent_name + '_saved_networks/' + '-dqn', global_step=episode)
                total_reward = 0
                suc_count = 0
                fal_count = 0
                eval_count = 0
                for i in range(args.TEST):
                    state_train_agent, state_use_agent = alloc.env_reset(env, train_agent_name)
                    # state_blue, state_red = env.reset_selfPlay()
                    # state_train_agent, state_use_agent = alloc.alloc_state(state_blue, state_red, train_agent_name)
                    step = 0
                    e_reward = 0
                    #env.creat_ALG()         #测试过程可视化显示 0/1
                    #testsheet = workbook.add_sheet('trace' + str(int(episode/args.TRAIN * args.TEST + i + 1)), cell_overwrite_ok=True)
                    #for j in range(len(row1)):
                        #testsheet.write(0, j, row1[j])
                    #testsheet.write(step + 1, 0, step + 1)
                    #testsheet.write(step + 1, 1, float(env.pos[0]))
                    #testsheet.write(step + 1, 2, float(env.pos[1]))
                    #testsheet.write(step + 1, 3, float(env.heading))
                    while True:
                        action_train_agent = train_agent.action(state_train_agent)
                        action_use_agent = use_agent.action(state_use_agent)
                        #action_use_agent = 2
                        state_train_agent, state_use_agent, reward, done = alloc.env_step(env, action_train_agent, action_use_agent, train_agent_name)

                        total_reward += reward
                        e_reward += reward
                        step += 1
                        #env.render()        #测试过程可视化显示 1/1
                        #testsheet.write(step + 1, 0, step + 1)
                        #testsheet.write(step + 1, 1, float(env.pos[0]))
                        #testsheet.write(step + 1, 2, float(env.pos[1]))
                        #testsheet.write(step + 1, 3, float(env.heading))
                        if done:
                            trainsheet.write(int(episode/args.TRAIN * args.TEST + i + 1), 0, (episode/args.TRAIN * args.TEST + i + 1))
                            trainsheet.write(int(episode/args.TRAIN * args.TEST + i + 1), 1, step)
                            trainsheet.write(int(episode/args.TRAIN * args.TEST + i + 1), 2, e_reward)
                            trainsheet.write(int(episode/args.TRAIN * args.TEST + i + 1), 3, env.success)
                            if env.success == 1:
                                suc_count += 1
                            elif env.success == -1:
                                fal_count += 1
                            else:
                                eval_count += 1
                            break
                ave_reward = total_reward / args.TEST
                workbook.save(train_agent_name + '_data_train'  + '.xls')
                print('Episode: ', episode, "Success count:", suc_count, "Fail count:", fal_count, "Eval count:", eval_count, "Average Reward:", ave_reward,env.acts)
                if suc_count >= 0.95 * args.TEST:
                    suc_num += 1
                else:
                    suc_num = 0
                if suc_num ==10:
                    break

    else:    # 直接加载train_agent保存的模型，进行可视化
        for episode in range(args.EPISODE):
            e_reward = 0
            step = 0
            tracesheet = showbook.add_sheet('trace' + str(episode + 1), cell_overwrite_ok=True)
            for i in range(len(row1)):
                tracesheet.write(0, i, row1[i])
            state_train_agent, state_use_agent = alloc.env_reset(env, train_agent_name)
            # state_blue, state_red = env.reset_selfPlay()
            # state_train_agent, state_use_agent = alloc.alloc_state(state_blue, state_red, train_agent_name)
            env.creat_ALG()
            tracesheet.write(step + 1, 0, step + 1)
            tracesheet.write(step + 1, 1, float(env.ac_pos_b[0]))
            tracesheet.write(step + 1, 2, float(env.ac_pos_b[1]))
            tracesheet.write(step + 1, 3, float(env.ac_heading_b))
            tracesheet.write(step + 1, 4, float(env.ac_bank_angle_b))
            tracesheet.write(step + 1, 5, float(env.ac_pos_r[0]))
            tracesheet.write(step + 1, 6, float(env.ac_pos_r[1]))
            tracesheet.write(step + 1, 7, float(env.ac_heading_r))
            tracesheet.write(step + 1, 8, float(env.ac_bank_angle_r))
            #tracesheet.write(step + 1, 8, float(env.ATA))
            #tracesheet.write(step + 1, 9, float(env.AA))

            while True:
                action_train_agent = train_agent.action(state_train_agent)
                action_use_agent = use_agent.action(state_use_agent)
                state_train_agent, state_use_agent, reward, done = alloc.env_step(env, action_train_agent, action_use_agent, train_agent_name)

                e_reward += reward
                step += 1
                env.render()
                tracesheet.write(step + 1, 0, step + 1)
                tracesheet.write(step + 1, 1, float(env.ac_pos_b[0]))
                tracesheet.write(step + 1, 2, float(env.ac_pos_b[1]))
                tracesheet.write(step + 1, 3, float(env.ac_heading_b))
                tracesheet.write(step + 1, 4, float(env.ac_bank_angle_b))
                tracesheet.write(step + 1, 5, float(env.ac_pos_r[0]))
                tracesheet.write(step + 1, 6, float(env.ac_pos_r[1]))
                tracesheet.write(step + 1, 7, float(env.ac_heading_r))
                tracesheet.write(step + 1, 8, float(env.ac_bank_angle_r))
                #tracesheet.write(step + 1, 8, float(env.ATA))
                #tracesheet.write(step + 1, 9, float(env.AA))

                if done:
                    showsheet.write(episode + 1, 0, episode + 1)
                    showsheet.write(episode + 1, 1, step + 1)
                    showsheet.write(episode + 1, 2, e_reward)
                    print('Episode: ', episode, 'Step', step, "Reward:", e_reward,"Success:", env.success,env.acts)
                    break
            showbook.save(train_agent_name + '_data_show' + '.xls')

