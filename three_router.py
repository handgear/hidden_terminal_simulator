#-*- coding: utf-8 -*-
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
from routerlib import *




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
router_list[0].receiver.append([1,500,500])
router_list[2].receiver.append([1,500,500])

#===========loop for one frame=============#
for a in range(3):

    router_list[0].set_R
    router_list[2].set_R

    if router_list[0].state == '':
        router_list[0].set_RTS_time
        router_list[2].set_RTS_time

    #=================sender router=============#
    #현재 받는 대상은 1번 라우터로 설정, 추후에는 인접한 라우터 중 무작위로 선정
    #RTS를 보낸다
    if supervisor.current_time_slot == router_list[0].time_to_send['RTS']:
        router_list[0].ctrl_data['RTS'] = 1 #router number
        router_list[0].state = 'RTS'
        # print 'set rts ok'
        #RTS 보내고 난 다음에는 RTS flag 내려준다
    elif supervisor.current_time_slot > router_list[0].time_to_send['RTS']:
        router_list[0].ctrl_data['RTS'] = -1


    if supervisor.current_time_slot > router_list[0].time_to_send['RTS']:
        #CTS 받은 경우, 데이터 전송 시기를 지정해준다
        if router_list[0].time_out['CTS'] is not 0 and \
        router_list[1].ctrl_data['CTS'] == 0:
            #receiver router number, [0] for router number, ==0 for sender router number:
            router_list[0].time_to_send['DATA'] = supervisor.current_time_slot + 1
            router_list[0].state = 'DATA'
        #CTS 받지 못한 경우
        elif router_list[0].time_out['CTS'] is not 0 and \
        router_list[1].ctrl_data['CTS'] == -1:
                #timeout 1줄인다
            router_list[0].time_out['CTS'] = router_list[0].time_out['CTS'] - 1
            router_list[0].state = 'WAIT_CTS'
        #CTS time out, K=K+1
        elif router_list[0].time_out['CTS'] == 0:
            router_list[0].backoff_data['K'] = router_list[0].backoff_data['K'] + 1
            router_list[0].state = 'WAIT'

    #CTS 받은 경우에만 DATA 전송
    if router_list[0].time_to_send['DATA'] <= supervisor.current_time_slot and \
    router_list[1].ctrl_data['CTS'] == 0:
        #데이터 전송 60time slot동안 진행
        if router_list[1].ctrl_data['DATA'] < 60:
            router_list[1].ctrl_data['DATA'] = router_list[1].ctrl_data['DATA'] + 1
            router_list[0].state = 'DATA'

    #데이터를 다 보낸 경우에만 ACK 기다림
    if router_list[1].ctrl_data['DATA'] == 60:
        #ACK 받은 경우
        if router_list[0].time_out['ACK'] is not 0 and \
        router_list[1].ctrl_data['ACK'] == 0:
            router_list[0].initialize_sender
            router_list[1].initialize_receiver
            router_list[0].state = 'ACK'
        #ACK 받지 못한 경우
        elif router_list[0].time_out['ACK'] is not 0 and \
        router_list[1].ctrl_data['ACK'] == -1:
            router_list[0].state = 'WAIT_ACK'
        #ACK time out, K=K+1
        elif router_list[0].time_out['ACK'] == 0:
            router_list[0].backoff_data['K'] = router_list[0].backoff_data['K'] + 1
            router_list[0].state = 'WAIT'

    #================receiver router==============#
    #RTS가 한개만 오면 해당 라우터에 다음 타임슬롯에 모든 라우터에 CTS보낸다
    #범위 내의 라우터 중 RTS를 보내는 라우터가 하나일 때만 CTS 전송(단 라우터 번호는 RTS받은 라우터번호)
    count = []
    if router_list[1].state == 'WAIT' or router_list[1].state == '':

        for i in range(len(router_list[1].near_router)):
            num = router_list[1].near_router[i][0] #router number
            if router_list[num].ctrl_data['RTS'] == 1:
                count.append(i)
        print count
        if len(count) == 1:
            router_list[1].time_to_send['CTS'] = supervisor.current_time_slot + 1
    print "time slot for cts: " +  str(router_list[1].time_to_send['CTS'])
    #CTS보낼 time slot 이 되면 CTS 보냄
    if supervisor.current_time_slot == router_list[1].time_to_send['CTS']:
        router_list[1].ctrl_data['CTS'] = 0
        router_list[1].state = 'CTS'
    #CTS 전송 완료된 경우 flag 내려줌
    elif supervisor.current_time_slot > router_list[1].time_to_send['CTS']:
        router_list[1].ctrl_data['CTS'] = -1


    #DATA 받는 중
    if router_list[1].ctrl_data['DATA'] is not 0:
        router_list[1].state = 'DATA'


    #데이터 전송 완료된 경우 ACK 시간 세팅 (receiver쪽에서 세팅)
    if router_list[0].ctrl_data['DATA'] == 0:
        router_list[1].time_to_send['ACK'] = supervisor.current_time_slot + 1
    #ACK를 보내야하는 time slot에 도달한 경우, ACK 보냄
    if router_list[1].time_to_send['ACK'] == supervisor.current_time_slot:
        router_list[1].ctrl_data['ACK'] = 0 #ACK를 받을 라우터 번호 입력
        router_list[1].state = 'ACK'



    #======================================#

    #for문으로 바꾸기
    #기다리고 있는 동안 R 1씩 줄이기
    if router_list[0].state == 'WAIT':
        router_list[0].backoff_data['R'] = router_list[0].backoff_data['R'] -1
    #CTS 기다리고 있는 동안 time_out['CTS'] 1씩 줄이기
    if router_list[0].state == 'WAIT_CTS':
        router_list[0].time_out['CTS'] =  router_list[0].time_out['CTS'] - 1
    #ACK 기다리고 있는 동안 time_out['ACK'] 1씩 줄이기
    if router_list[0].state == 'WAIT_ACK':
        router_list[0].time_out['ACK'] =  router_list[0].time_out['ACK'] - 1

    #move time slot to next time slot
    supervisor.current_time_slot = supervisor.current_time_slot + 1






    print "router_list[0].state: " + router_list[0].state
    print "router_list[1].state: " + router_list[1].state
    print router_list[0].ctrl_data['RTS']
    # print router_list[1].near_router[0][0]
    # print router_list[1].near_router[1][0]
    print '================='


    #=========================drawing section==========================#

    # for i in range(setting.TOTAL_TIME_SLOT):

    # plot axis number
    plt.axis([0, 1000, 0, 1000])
    plt.xlabel('Time Slot = %d' %supervisor.current_time_slot, fontsize=18)

    for j in range(setting.TOTAL_ROUTER_NUM):
        #draw router
        plt.plot(router_list[j].x, router_list[j].y,'bo')



        #draw range of routers
        if router_list[j].state == 'WAIT' or router_list[j].state == '':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='white')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'RTS':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='orange')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'CTS' or router_list[j].state == 'WAIT_CTS':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='cyan')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'DATA':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='green')
            plt.gca().add_patch(circle)

        # #color conflicting router range as red
        # if len(router_list[j].near_router) is not 0:
        #     circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='red')
        #     plt.gca().add_patch(circle)
        # else:
        #     circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='blue')
        #     plt.gca().add_patch(circle)

    #draw arrow
    # plt.arrow(0, 0, 100, 100, head_width=20, head_length=20, width=5, fc='k', ec='k')

    #END drawing section
    # plt.savefig('./output/test%d.png' % i) #uncomment to save as img
    plt.show() #uncomment to show windows
    plt.gcf().clear()

#=========================comments============================#
#가운데는 일단 듣는 역할, 양옆 두개가 전송하려고 하는 상황
'''송신측
R=0, K=0, K_limit

RTS 보낸다(NAV도 같이 보낸다, NAV는 상대시간으로 보낸다)
5동안 기다린다.
CTS 안오면 K = K+1 (CTS 가 오긴오는데 자신것이 아니면 NAV 확인 해서 대기상태/NAV 이후 얼마나 기다릴지는 추후 구현. 기존에 기다리다가 남은 슬롯만큼만 기다리고 재전송 시도->남은 R 줄이면서 0에 도달하면 전송)
랜덤하게 정한다 (pick rand Tslot method)
다시 시도. R 을 슬롯마다 1씩 줄인다.
===
CTS받으면 다음부터 데이터 전송(60슬랏동안, 번호붙여서)
말이 전송이지 그냥 보내는 측 라우터의 DATA의 숫자 늘려주면 됨.
다 보내면 ACK 기다림.(현 구현에서는 다음 슬롯에 바로 도착하므로 확인처리(전체 value 초기화)만 하고 다음 전송을 준비하면 됨)
'''

'''수신측
RTS신호가 2개 잡히면 충돌이므로 무시 =>near_router 의 RTS 상태를 확인한다.
(보내는 측의 router RTS = [수신측 라우터 번호, NAV]) NAV=62
하나만 잡히면 해당 RTS에 CTS보내준다.
(받는 측 라우터의 CTS = [수신측 라우터번호, NAV]) NAV = 61
데이터를 60슬랏동안 받으면 다음 슬랏에 ACK를 보대준다.


'''


#RTS, CTS, DATA, ACK 모두 다른 색깔 화살표로 표시하기
#캡션 달기(화살표 안에 적어도 되고) //방법 알아보기

#전송이 끝나면 모든 데이터 초기화 하기
