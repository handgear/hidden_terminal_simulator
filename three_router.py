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
            router_list[i].set_R()
            # router_list[i].set_RTS_time(supervisor.current_time_slot)
    # for i in range(setting.TOTAL_ROUTER_NUM):
    #     router_list[i].set_R()
    logging.info('rts time0: ' + str(router_list[0].time_to_send['RTS']))
    logging.info('rts time1: ' + str(router_list[1].time_to_send['RTS']))
    logging.info('rts time2: ' + str(router_list[2].time_to_send['RTS']))

    if router_list[0].state == '' or router_list[1].state == '' or router_list[2].state == '':
        logging.info('backoff time R0: ' + str(router_list[0].backoff_data['R']))
        logging.info('backoff time R1: ' + str(router_list[1].backoff_data['R']))
        logging.info('backoff time R2: ' + str(router_list[2].backoff_data['R']))
        logging.info('backoff time K0: ' + str(router_list[0].backoff_data['K']))
        logging.info('backoff time K1: ' + str(router_list[1].backoff_data['K']))
        logging.info('backoff time K2: ' + str(router_list[2].backoff_data['K']))

    # CTS time out, K=K+1, reset sender without R,K init
    for i in range(setting.TOTAL_ROUTER_NUM):
        if supervisor.current_time_slot > router_list[i].time_to_send['RTS'] and \
        router_list[i].state == 'WAIT_CTS' and router_list[i].time_out['CTS'] == 0:
            router_list[i].backoff_data['K'] = router_list[i].backoff_data['K'] + 1
            # router_list[i].state = 'CTS_TIMEOUT'
            print "%d router been CTS_TIMEOUT and reset" %i
            # router_list[i].reset = 3 #reset sender without RK
            router_list[i].initialize_sender_without_RK()
            router_list[i].set_R()

    #================receiver router divided == 0 ==============#
    #receiver
    for i in range(setting.TOTAL_ROUTER_NUM):
        #RTS가 한개만 오면 해당 라우터에 다음 타임슬롯에 모든 라우터에 CTS보낸다
        #범위 내의 라우터 중 RTS를 보내는 라우터가 하나일 때만 CTS 전송(단 라우터 번호는 RTS받은 라우터번호)
        if router_list[i].state == '' or router_list[i].state == 'CTS_TIMEOUT':
            router_list[i].sender_list = []
            for j in range(len(router_list[i].near_router)):
                num = router_list[i].near_router[j][0] #router number
                logging.debug('i:'+ str(i) + ' num or near router: ' + str(num))
                logging.debug("router_list[num].ctrl_data['RTS']: " + str(router_list[num].ctrl_data['RTS']))
                if router_list[num].ctrl_data['RTS'] == i:
                    router_list[i].sender_list.append(num)
                    logging.debug('appended router num: ' + str(num))
                    logging.debug('len of sender list'+str(i)+': ' + str(len(router_list[i].sender_list)))
                    logging.debug('rts router from 0: ' + str(router_list[0].ctrl_data['RTS']))
                    logging.debug('rts router from 1: ' + str(router_list[1].ctrl_data['RTS']))
                    logging.debug('rts router from 2: ' + str(router_list[2].ctrl_data['RTS']))
            #send CTS
            if len(router_list[i].sender_list) == 1:
                router_list[i].ctrl_data['CTS'] = router_list[i].sender_list[0]
                router_list[i].state = 'CTS'
                logging.debug("sender router num for cts: " +  str(router_list[i].ctrl_data['CTS']))

                #send NAV to other routers
                for router_num in range(len(router_list[i].near_router)):
                    if router_num is not router_list[i].sender_list[0]: #only send NAV to other routers
                        router_list[router_num].NAV = setting.DATA_LENGTH + 2

                #down RTS flag
                router_list[router_list[i].sender_list[0]].ctrl_data['RTS'] = -1

        # #CTS보낼 time slot 이 되면 CTS 보냄
        # if supervisor.current_time_slot == router_list[i].time_to_send['CTS']:
        #     # router_list[i].ctrl_data['CTS'] = 0
        #     #sender router number를 저장하여 전송 표현
        #     router_list[i].ctrl_data['CTS'] = router_list[i].sender_list[0]
        #     router_list[i].state = 'CTS'
        #     logging.debug("sender router num for cts: " +  str(router_list[i].ctrl_data['CTS']))

        #     #send NAV to other routers
        #     for router_num in range(len(router_list[i].near_router)):
        #         if router_num is not router_list[i].sender_list[0]: #only send NAV to other routers
        #             router_list[router_num].NAV = setting.DATA_LENGTH + 2

        #CTS 전송 완료된 경우 flag 내려줌
        elif supervisor.current_time_slot > router_list[i].time_to_send['CTS']:
            router_list[i].ctrl_data['CTS'] = -1
            # router_list[i].sender_list = [] #reset sender_list

        #=================sender router devided = 0=============#

    #sender
    for i in range(setting.TOTAL_ROUTER_NUM):
        #CTS 받은 경우에만 DATA 전송
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
    #sender
    for i in range(setting.TOTAL_ROUTER_NUM):
        if supervisor.current_time_slot > router_list[i].time_to_send['RTS'] and \
        router_list[i].state == 'RTS' or router_list[i].state == 'WAIT_CTS':
            logging.debug('entered setting CTS by: ' + str(i))
            logging.debug('router_list[receiver].ctrl_data[CTS]: ' + str(router_list[router_list[i].receiver].ctrl_data['CTS']))
            #CTS 받은 경우, 데이터 전송 시기를 지정해준다
            if router_list[i].time_out['CTS'] is not 0 and \
            router_list[router_list[i].receiver].ctrl_data['CTS'] == i:
                #receiver router number, [0] for router number, ==0 for sender router number:
                router_list[i].time_to_send['DATA'] = supervisor.current_time_slot + 1
                router_list[router_list[i].receiver].time_to_end['DATA'] = supervisor.current_time_slot + setting.DATA_LENGTH + 1 #데이터 전송이 끝나는 시기를 입력해 놓는다
                # router_list[i].receiver = 1
                router_list[i].state = 'CTS'
            #CTS 받지 못한 경우
            elif router_list[i].time_out['CTS'] is not 0 and \
            router_list[router_list[i].receiver].ctrl_data['CTS'] == -1:
            # router_list[i].receiver == -1
                router_list[i].state = 'WAIT_CTS'
            #CTS time out, K=K+1 #moved to top
            # elif router_list[i].time_out['CTS'] == 0:
            #     router_list[i].backoff_data['K'] = router_list[i].backoff_data['K'] + 1
            #     router_list[i].state = 'CTS_TIMEOUT'
            #     router_list[i].reset = 3 #reset sender without RK

    #현재 받는 대상은 1번 라우터로 설정, 추후에는 인접한 라우터 중 무작위로 선정
    #sender: send RTS
    for i in range(setting.TOTAL_ROUTER_NUM):
        #NAV 에 따른 RTS송신 지연
        # if router_list[i].NAV is not 0:
        #     router_list[i].time_to_send['RTS'] = router_list[i].time_to_send['RTS'] + 1
        #정해진 시간이 되면 RTS를 보낸다
        # if supervisor.current_time_slot == router_list[i].time_to_send['RTS']:
        if router_list[i].backoff_data['R'] == 0 and router_list[i].state == '' and \
        router_list[i].NAV == 0:
            if i == 0:
                router_list[i].receiver = 1
            elif i == 1:
                router_list[i].receiver = random.choice([0, 2])
            elif i == 2:
                router_list[i].receiver = 1

            router_list[i].ctrl_data['RTS'] = router_list[i].receiver
            router_list[i].state = 'RTS'
        #     router_list[i].time_to_send['RTS'] = supervisor.current_time_slot #add

        # #RTS 보내고 난 다음에는 RTS flag 내려준다
        # elif supervisor.current_time_slot > router_list[i].time_to_send['RTS']:
        #     router_list[i].ctrl_data['RTS'] = -1

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
                #ACK time out, K=K+1
                elif router_list[i].time_out['ACK'] == 0:
                    router_list[i].backoff_data['K'] = router_list[i].backoff_data['K'] + 1
                    router_list[i].state = 'ACK_TIMEOUT'

    #================receiver router divided == 1 ==============#
    #receiver
    for i in range(setting.TOTAL_ROUTER_NUM):
        #DATA 받는 중
        #데이터를 받을 때만 데이터 상테를 표시하도록 조건 정해야함...
        if router_list[i].ctrl_data['DATA'] is not 0 and \
        supervisor.current_time_slot < router_list[i].time_to_end['DATA']:
            router_list[i].state = 'DATA'
            logging.debug('data receiving')
        #데이터 전송 완료된 경우 ACK 시간 세팅 (receiver쪽에서 세팅)
        if router_list[i].ctrl_data['DATA'] == setting.DATA_LENGTH:
            router_list[i].time_to_send['ACK'] = supervisor.current_time_slot + 1
            # router_list[i].ctrl_data['DATA'] = 0 #reset

    #======================================#
    #before time slot change (only divided time change)
    #======================================#
    logging.info("NAV 0: "+str(router_list[0].NAV))
    logging.info("NAV 1: "+str(router_list[1].NAV))
    logging.info("NAV 2: "+str(router_list[2].NAV))

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
        #CTS 기다리고 있는 동안 time_out['CTS'] 1씩 줄이기
        if router_list[i].state == 'WAIT_CTS':
            router_list[i].time_out['CTS'] =  router_list[i].time_out['CTS'] - 1
        #ACK 기다리고 있는 동안 time_out['ACK'] 1씩 줄이기
        if router_list[i].state == 'WAIT_ACK':
            router_list[i].time_out['ACK'] =  router_list[i].time_out['ACK'] - 1
        #NAV timer 줄이기
        if router_list[i].NAV is not 0:
            router_list[i].NAV = router_list[i].NAV - 1
    #move time slot to next time slot
    supervisor.current_time_slot = supervisor.current_time_slot + 1






    logging.info("router_list[0].state: " + router_list[0].state)
    logging.debug('timeout0: ' + str(router_list[0].time_out['CTS']))
    logging.info("router_list[1].state: " + router_list[1].state)
    logging.debug('timeout0: ' + str(router_list[1].time_out['CTS']))
    logging.info("router_list[2].state: " + router_list[2].state)
    logging.debug('timeout0: ' + str(router_list[2].time_out['CTS']))


    # print router_list[1].near_router[0][0]
    # print router_list[1].near_router[1][0]
    logging.info('====================================')


    #=========================drawing section==========================#

    # for i in range(setting.TOTAL_TIME_SLOT):

    # plot axis number
    plt.axis([0, 1000, 0, 1000])
    plt.xlabel('Time Slot = %d' %supervisor.current_time_slot, fontsize=18)

    for j in range(setting.TOTAL_ROUTER_NUM):
        #draw router
        plt.plot(router_list[j].x, router_list[j].y,'bo')



        #draw range of routers
        if router_list[j].state == 'WAIT' or router_list[j].state == '' or \
        router_list[j].state == 'CTS_TIMEOUT' or router_list[j].state == 'ACK_TIMEOUT':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='white')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'RTS':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='orange')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'CTS':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='blue')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'WAIT_CTS':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='cyan')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'DATA':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='green')
            plt.gca().add_patch(circle)

        elif router_list[j].state == 'WAIT_ACK':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.5, fc='green')
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

    #draw arrow
    # plt.arrow(0, 0, 100, 100, head_width=20, head_length=20, width=5, fc='k', ec='k')

    #END drawing section
    plt.savefig('./output/test%d.png' % timeslot) #uncomment to save as img
    # plt.show() #uncomment to show windows
    plt.gcf().clear()

print supervisor.transfer_success
print "success rate: %0.2f%%" %((supervisor.transfer_success * setting.DATA_LENGTH)/setting.TOTAL_TIME_SLOT * 100)

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
