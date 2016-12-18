#-*- coding: utf-8 -*-
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from routerlib import *
import logging, sys
# logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
# logging.basicConfig(stream=sys.stderr, level=logging.WARNING)




#================================================================#
setting = Setting()
supervisor = Supervisor()


#make router objects
router_list = []
router_list.append(Router(300,500))
router_list.append(Router(500,500))
router_list.append(Router(700,500))

#search other routers in its range and add to .near_router[]
for i in range(setting.TOTAL_ROUTER_NUM):
    router_list[i].add_near_router_info(router_list, i)

#for debug
for i in range(setting.TOTAL_ROUTER_NUM):
    print router_list[i].near_router

#set receiver
#it will pick rand receiver later
# router_list[0].receiver = 1
# router_list[2].receiver = 1

#===========loop for one frame=============#
for timeslot in range(setting.TOTAL_TIME_SLOT): #can be change current_time_slot to using this
    logging.info('current time: ' + str(supervisor.current_time_slot))
    #reset router
    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].reset == 1:
            supervisor.transfer_success = supervisor.transfer_success + 1
            router_list[i].initialize_sender()
            # router_list[i].set_RTS_time(supervisor.current_time_slot)
        elif router_list[i].reset == 2:
            router_list[i].initialize_receiver()
        elif router_list[i].reset == 3:
            router_list[i].initialize_sender_without_RK()
            if router_list[i].backoff_data['K'] > setting.K_LIMIT:
                outer_list[i].backoff_data['K'] = 0
            router_list[i].set_R()


    if router_list[0].state == '' or router_list[1].state == '' or router_list[2].state == '':
        logging.info('backoff time R0: ' + str(router_list[0].backoff_data['R']))
        logging.info('backoff time R1: ' + str(router_list[1].backoff_data['R']))
        logging.info('backoff time R2: ' + str(router_list[2].backoff_data['R']))
        logging.info('backoff time K0: ' + str(router_list[0].backoff_data['K']))
        logging.info('backoff time K1: ' + str(router_list[1].backoff_data['K']))
        logging.info('backoff time K2: ' + str(router_list[2].backoff_data['K']))


    # ACK time out, K=K+1, reset sender without R,K init
    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].state == 'WAIT_ACK' and router_list[i].time_out['ACK'] == 0:
            #K = K+1
            router_list[i].backoff_data['K'] = router_list[i].backoff_data['K'] + 1
            print "%d router been ACK_TIMEOUT and reset" %i
            #reset
            router_list[i].initialize_sender_without_RK()
            router_list[i].set_R()

    #================receiver router divided == 0 ==============#


    #=================sender router devided = 0=============#

    #sender: send DATA
    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].time_to_send['DATA'] <= supervisor.current_time_slot and \
        router_list[i].time_to_send['DATA'] is not -1:
            #데이터 전송 60time slot동안 진행
            if supervisor.current_time_slot < router_list[router_list[i].receiver].time_to_end['DATA']:
                router_list[router_list[i].receiver].ctrl_data['DATA'] = router_list[router_list[i].receiver].ctrl_data['DATA'] + 1
                router_list[i].state = 'DATA'
                logging.debug('from router send data num: ' + str(router_list[router_list[i].receiver].ctrl_data['DATA']))


    #================receiver router divided == 0 ==============#
    #receiver
    for i in range(setting.TOTAL_ROUTER_NUM):
        #ACK를 보내야하는 time slot에 도달한 경우, ACK 보냄
        if router_list[i].time_to_send['ACK'] == supervisor.current_time_slot:
            router_list[i].ctrl_data['ACK'] = router_list[i].sender_list[0] #ACK를 받을 라우터 번호 입력
            router_list[i].reset = 2 #reset receiver
            router_list[i].state = 'ACK'

    #=================sender router devided = 1=============#

    #현재 받는 대상은 1번 라우터로 설정, 추후에는 인접한 라우터 중 무작위로 선정
    #sender: send DATA
    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].backoff_data['R'] == 0 and router_list[i].state == '':
            if i == 0:
                router_list[i].receiver = 1
            elif i == 1:
                router_list[i].receiver = random.choice([0, 2])
            elif i == 2:
                router_list[i].receiver = 1

            #여기서 데이터 보내기 시작
            #관련 성정하고 최종적으로는 DATA보내는 상태로 빠져나옴
            #이후 receiver가 보내는 데이터 확인하는 부분 필요함
            #============작성필요~~~!!!!===================#
            # router_list[i].ctrl_data['RTS'] = router_list[i].receiver
            # router_list[i].state = 'RTS'
        #     router_list[i].time_to_send['RTS'] = supervisor.current_time_slot #add


    #sender
    for i in range(setting.TOTAL_ROUTER_NUM):
        if supervisor.current_time_slot == router_list[router_list[i].receiver].time_to_end['DATA']:
            #데이터를 다 보낸 경우에만 ACK 기다림
            # logging.debug('1_data_num: ' + str(router_list[router_list[i].receiver].ctrl_data['DATA']))
            if router_list[router_list[i].receiver].ctrl_data['DATA'] == setting.DATA_LENGTH:
                #ACK 받은 경우
                if router_list[i].time_out['ACK'] is not 0 and \
                router_list[router_list[i].receiver].ctrl_data['ACK'] == i:
                    router_list[i].state = 'ACK'
                    router_list[i].reset = 1 #reset sender
                #ACK 받지 못한 경우
                elif router_list[i].time_out['ACK'] is not 0 and \
                router_list[router_list[i].receiver].ctrl_data['ACK'] == -1:
                    router_list[i].state = 'WAIT_ACK'
                # #ACK time out, K=K+1
                # elif router_list[i].time_out['ACK'] == 0:
                #     router_list[i].backoff_data['K'] = router_list[i].backoff_data['K'] + 1
                #     router_list[i].state = 'ACK_TIMEOUT'

    #================receiver router divided == 1 ==============#
    #receiver
    for i in range(setting.TOTAL_ROUTER_NUM):
        #DATA 받는 중
        #데이터를 받을 때만 데이터 상테를 표시하도록 조건 정해야함...
        if router_list[i].ctrl_data['DATA'] is not 0 and \
        supervisor.current_time_slot < router_list[i].time_to_end['DATA']:
            router_list[i].state = 'DATA_RECEIVE'
            logging.debug('data receiving')
        #데이터 전송 완료된 경우 ACK 시간 세팅 (receiver쪽에서 세팅)
        if router_list[i].ctrl_data['DATA'] == setting.DATA_LENGTH:
            router_list[i].time_to_send['ACK'] = supervisor.current_time_slot + 1
            # router_list[i].ctrl_data['DATA'] = 0 #reset

    #======================================#
    #before time slot change (only divided time change)
    #======================================#

    #only do once in each time slot
    for i in range(setting.TOTAL_ROUTER_NUM):
        #debug
        logging.info("i: "+str(i)+ "||state: " + str(router_list[i].state))
        logging.info("backoff R: "+str(router_list[i].backoff_data['R']))
        logging.info("is it idle?: "+str(router_list[i].is_channal_idle(router_list)))
        #기다리고 있는 동안 R 1씩 줄이기
        if router_list[i].state == '' and router_list[i].backoff_data['R'] is not 0 and \
        router_list[i].is_channal_idle(router_list) == True:
            router_list[i].backoff_data['R'] = router_list[i].backoff_data['R'] -1
        #ACK 기다리고 있는 동안 time_out['ACK'] 1씩 줄이기
        if router_list[i].state == 'WAIT_ACK':
            router_list[i].time_out['ACK'] =  router_list[i].time_out['ACK'] - 1

    #move time slot to next time slot
    supervisor.current_time_slot = supervisor.current_time_slot + 1






    logging.info("router_list[0].state: " + router_list[0].state)
    logging.debug('timeout0: ' + str(router_list[0].time_out['ACK']))
    logging.info("router_list[1].state: " + router_list[1].state)
    logging.debug('timeout0: ' + str(router_list[1].time_out['ACK']))
    logging.info("router_list[2].state: " + router_list[2].state)
    logging.debug('timeout0: ' + str(router_list[2].time_out['ACK']))


    # print router_list[1].near_router[0][0]
    # print router_list[1].near_router[1][0]
    logging.info('====================================')


    #=========================drawing section==========================#

    # for i in range(setting.TOTAL_TIME_SLOT):

    # plot axis number
    plt.axis([0, 1000, 0, 1000])
    plt.xlabel('Time Slot = %d' %(supervisor.current_time_slot-1), fontsize=18)

    #color info bar on top
    # DATA_SEND / DATA_RECEIVE / WAIT_ACK / ACK
    plt.text(20, 1045, 'DATA_SEND', style='italic',
        bbox={'facecolor':'greenyellow', 'alpha':0.5, 'pad':10})
    plt.text(240, 1045, 'DATA_RECEIVE', style='italic',
        bbox={'facecolor':'greenyellow', 'alpha':0.5, 'pad':10})
    plt.text(620, 1045, 'WAIT_ACK', style='italic',
        bbox={'facecolor':'limegreen', 'alpha':0.7, 'pad':10})
    plt.text(820, 1045, 'ACK', style='italic',
        bbox={'facecolor':'green', 'alpha':0.8, 'pad':10})

    for j in range(setting.TOTAL_ROUTER_NUM):
        #draw router
        plt.plot(router_list[j].x, router_list[j].y,'bH')


        #draw range of routers
        if router_list[j].state == 'WAIT' or router_list[j].state == '' or \
        or router_list[j].state == 'ACK_TIMEOUT':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.5, fc='white')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'DATA_SEND':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.5, fc='greenyellow')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'DATA_RECEIVE':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.5, fc='greenyellow')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'WAIT_ACK':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.7, fc='limegreen')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'ACK':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.8, fc='green')
            plt.gca().add_patch(circle)

        # #color conflicting router range as red
        # if len(router_list[j].near_router) is not 0:
        #     circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='red')
        #     plt.gca().add_patch(circle)
        # else:
        #     circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='blue')
        #     plt.gca().add_patch(circle)

        #draw arrow (example code)
        # plt.arrow(0, 0, 100, 100, head_width=20, head_length=20, width=5, fc='k', ec='k')

        #draw arrowto notate sending RTS
        if router_list[j].state == 'DATA_SEND':
            num = router_list[j].receiver
            plt.arrow(router_list[j].x, router_list[j].y, router_list[num].x -router_list[j].x, router_list[num].y - router_list[j].y, head_width=30, head_length=30, width=5, fc='m', ec='m')

    #END drawing section
    plt.savefig('./output/test%d.png' % timeslot) #uncomment to save as img
    # plt.show() #uncomment to show windows
    plt.gcf().clear()

print supervisor.transfer_success
print "success rate: %0.2f%%" %((supervisor.transfer_success * setting.DATA_LENGTH)/setting.TOTAL_TIME_SLOT * 100)

#=========================comments============================#
#가운데는 일단 듣는 역할, 양옆 두개가 전송하려고 하는 상황
#state: DATA_SEND / DATA_RECEIVE / WAIT_ACK / ACK


'''송신측
R=0, K=0, K_limit

R==0이면 DATA 보낸다
다 보낸 이후 5슬랏 이내로 ACK가 오지 않으면 (timeout)
k=k+1, R reset

채널이 idle할때만 R을 1씩 감소
ACK가 오면 전체 리셋

'''

'''수신측
데이터를 받는 경우는 두가지.
두 개이상의 데이터를 동시에 받기 시작해서 동시에 끝나거나
아니면 하나만 받거나

하나만 받는 경우 다 받은 뒤에(데이터 길이만큼) ACK을 보내주면 된다.
ACK 보낸 뒤에 리셋

두 개이상 받는 경우 데이터 전송 완료까지 대기(어차피 R 줄어들지 않을테니 신경안써도 됨)

'''

#전송이 끝나면 모든 데이터 초기화 하기
