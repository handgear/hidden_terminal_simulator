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
# logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)




#================================================================#
setting = Setting()
supervisor = Supervisor()


#make router objects
router_list = [Router() for i in range(setting.TOTAL_ROUTER_NUM)]
# router_list = []
# router_list.append(Router(300,500))
# router_list.append(Router(500,500))
# router_list.append(Router(700,500))

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
            if supervisor.current_time_slot < router_list[i].time_to_end['DATA']:
                router_list[i].ctrl_data['DATA'] = router_list[i].ctrl_data['DATA'] + 1
                router_list[i].state = 'DATA'
                logging.debug('from router send data num: ' + str(router_list[router_list[i].receiver].ctrl_data['DATA']))


    #================receiver router divided == 0 ==============#
    # #receiver: send ACK
    for i in range(setting.TOTAL_ROUTER_NUM):
        #ACK를 보내야하는 time slot에 도달한 경우, ACK 보냄
        if router_list[i].time_to_send['ACK'] == supervisor.current_time_slot and \
        router_list[i].single_sender == 1:
            router_list[i].ctrl_data['ACK'] = router_list[i].sender_list[0] #ACK를 받을 라우터 번호 입력
            # router_list[i].reset = 2 #reset receiver
            router_list[i].state = 'ACK'

    #=================sender router devided = 1=============#

    #현재 받는 대상은 1번 라우터로 설정, 추후에는 인접한 라우터 중 무작위로 선정
    #sender: send DATA
    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].backoff_data['R'] == 0 and router_list[i].state == '':
            if len(router_list[i].near_router) == 0: # if no router is nearby, then don't send DATA
                router_list[i].state = 'NO_NEAR_ROUTER'
                continue
            #select random router nearby
            rand_near_router = random.choice(router_list[i].near_router)
            router_list[i].receiver = rand_near_router[0]

            #여기서 데이터 보내기 시작
            #관련 성정하고 최종적으로는 DATA보내는 상태로 빠져나옴
            #이후 receiver가 보내는 데이터 확인하는 부분 필요함
            #============작성필요~~~!!!!===================#
            router_list[i].ctrl_data['noRTS'] = router_list[i].receiver
            router_list[i].time_to_end['DATA'] = supervisor.current_time_slot + setting.DATA_LENGTH - 1#데이터 전송이 끝나는 시기를 입력해 놓는다(보내는 자우터 자신에게 기록, 전송받는 측이 참)
            logging.info("i "+ str(i) + " time to end: " + str(router_list[i].time_to_end['DATA']))
            router_list[i].state = 'DATA_SEND'
            #
        #     router_list[i].time_to_send['RTS'] = supervisor.current_time_slot #add



    #sender
    #count sended data num
    #data = data+1



    #sender
    for i in range(setting.TOTAL_ROUTER_NUM):
        if supervisor.current_time_slot == router_list[i].time_to_end['DATA'] + 1 and \
        router_list[i].state is not 'NO_NEAR_ROUTER':
            #데이터를 다 보낸 경우에만 ACK 기다림
            # logging.debug('1_data_num: ' + str(router_list[router_list[i].receiver].ctrl_data['DATA']))
            # if router_list[router_list[i].receiver].ctrl_data['DATA'] == setting.DATA_LENGTH:
            #ACK 받은 경우
            if router_list[i].time_out['ACK'] is not 0 and \
            router_list[router_list[i].receiver].ctrl_data['ACK'] == i:
                router_list[i].state = 'ACK'
                router_list[i].reset = 1 #reset sender
                router_list[router_list[i].receiver].reset = 2
                router_list[router_list[i].receiver].state = 'ACK'
            #ACK 받지 못한 경우
            elif router_list[i].time_out['ACK'] is not 0 and \
            router_list[router_list[i].receiver].ctrl_data['ACK'] == -1:
                router_list[i].state = 'WAIT_ACK'
            # #ACK time out, K=K+1
            # elif router_list[i].time_out['ACK'] == 0:
            #     router_list[i].backoff_data['K'] = router_list[i].backoff_data['K'] + 1
            #     router_list[i].state = 'ACK_TIMEOUT'

    #================receiver router divided == 1 ==============#
    #receiver: receiving data
    #check who is sending
    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].state == '':
            for j in range(len(router_list[i].near_router)):
                num = router_list[i].near_router[j][0] #router number
                if router_list[num].ctrl_data['noRTS'] == i:
                    router_list[i].sender_list.append(num)

                    logging.debug('appended router num: ' + str(num))
                    logging.debug('len of sender list'+str(i)+': ' + str(len(router_list[i].sender_list)))

            #update state
            if len(router_list[i].sender_list) > 0:
                router_list[i].state = 'DATA_RECEIVE'
            #check is it only one router sending
            if len(router_list[i].sender_list) == 1:
                router_list[i].single_sender = 1


    for i in range(setting.TOTAL_ROUTER_NUM):
        if router_list[i].state == '' or router_list[i].state == 'DATA_RECEIVE':
            temp = []
            for j in range(len(router_list[i].near_router)):
                num = router_list[i].near_router[j][0] #router number
                if router_list[num].ctrl_data['noRTS'] == i:
                    temp.append(num)
                    # router_list[i].sender_list.append(num)

                    # logging.debug('appended router num: ' + str(num))
                    # logging.debug('len of sender list'+str(i)+': ' + str(len(router_list[i].sender_list)))

            if len(temp) > 1:
                router_list[i].single_sender = 0
                # router_list[i].reset = 2
                router_list[i].initialize_receiver()


    #지우고 다 받을 타임이 되면 flag확인하고서 다음 슬랏에 ACK보내기
    for i in range(setting.TOTAL_ROUTER_NUM):
        #DATA 받는 중
        #데이터를 받을 때만 데이터 상테를 표시하도록 조건 정해야함...
        if router_list[i].single_sender == 1:
            num = router_list[i].sender_list[0]
            #데이터 전송 완료된 경우 ACK 시간 세팅 (receiver쪽에서 세팅)
            if supervisor.current_time_slot == router_list[num].time_to_end['DATA']:
                router_list[i].time_to_send['ACK'] = supervisor.current_time_slot + 1

        elif router_list[i].single_sender > 1:
            router_list[i].reset = 2

        # if router_list[i].ctrl_data['DATA'] is not 0 and \
        # supervisor.current_time_slot < router_list[i].time_to_end['DATA']:
        #     router_list[i].state = 'DATA_RECEIVE'
        #     logging.debug('data receiving')


    #======================================#
    #before time slot change (only divided time change)
    #======================================#

    #only do once in each time slot
    for i in range(setting.TOTAL_ROUTER_NUM):
        #debug
        logging.info("i: "+str(i)+ "||state: " + str(router_list[i].state))
        logging.info("backoff R: "+str(router_list[i].backoff_data['R']))
        logging.info("is it idle?: "+str(router_list[i].is_channal_idle_noRTS(router_list)))
        #기다리고 있는 동안 R 1씩 줄이기
        if router_list[i].state == '' and router_list[i].backoff_data['R'] is not 0 and \
        router_list[i].is_channal_idle_noRTS(router_list) == True:
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
        # if router_list[j].state == 'WAIT' or router_list[j].state == '' or \
        # router_list[j].state == 'ACK_TIMEOUT' or router_list[i].state == 'NO_NEAR_ROUTER':
        #     circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='azure')
        #     plt.gca().add_patch(circle)

        if router_list[j].state == 'DATA_SEND':
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

        elif router_list[j].state == '' or router_list[j].state == 'ACK_TIMEOUT' or router_list[i].state == 'NO_NEAR_ROUTER':
            circle = plt.Circle((router_list[j].x, router_list[j].y), radius=setting.ROUTER_RANGE, alpha=0.3, fc='azure')
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
    if(setting.OUTPUT_PNG):
        plt.savefig('./output_noRTS/test%d.png' % timeslot) #uncomment to save as img
    # plt.show() #uncomment to show windows
    plt.gcf().clear()

print supervisor.transfer_success
print "success rate: %0.2f%%" %((supervisor.transfer_success * setting.DATA_LENGTH)/setting.TOTAL_TIME_SLOT * 100)

#================#
#================#
#reset router for next test (WITH RTS, CTS)
#reset without position and near_router info
for reset in range(setting.TOTAL_ROUTER_NUM):
    router_list[reset].initialize_router()




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
    #receiver: check RTS and send CTS
    for i in range(setting.TOTAL_ROUTER_NUM):
        #RTS가 한개만 오면 해당 라우터에 다음 타임슬롯에 모든 라우터에 CTS보낸다
        #범위 내의 라우터 중 RTS를 보내는 라우터가 하나일 때만 CTS 전송(단 라우터 번호는 RTS받은 라우터번호)
        if router_list[i].NAV == 0 and \
        (router_list[i].state == '' or router_list[i].state == 'CTS_TIMEOUT'):
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

    #sender: send RTS
    for i in range(setting.TOTAL_ROUTER_NUM):
        #NAV 에 따른 RTS송신 지연
        # if router_list[i].NAV is not 0:
        #     router_list[i].time_to_send['RTS'] = router_list[i].time_to_send['RTS'] + 1
        #정해진 시간이 되면 RTS를 보낸다
        # if supervisor.current_time_slot == router_list[i].time_to_send['RTS']:
        if router_list[i].backoff_data['R'] == 0 and router_list[i].state == '' and \
        router_list[i].NAV == 0:
            if len(router_list[i].near_router) == 0: # if no router is nearby, then don't send RTS
                continue
            #select random router nearby
            rand_near_router = random.choice(router_list[i].near_router)
            router_list[i].receiver = rand_near_router[0]

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
    plt.xlabel('Time Slot = %d' %(supervisor.current_time_slot-1), fontsize=18)

    #color info bar on top
    plt.text(20, 1045, 'RTS', style='italic',
        bbox={'facecolor':'orange', 'alpha':0.3, 'pad':10})
    plt.text(220, 1045, 'CTS', style='italic',
        bbox={'facecolor':'blue', 'alpha':0.3, 'pad':10})
    plt.text(420, 1045, 'WAIT_CTS', style='italic',
        bbox={'facecolor':'cyan', 'alpha':0.3, 'pad':10})
    plt.text(620, 1045, 'DATA', style='italic',
        bbox={'facecolor':'green', 'alpha':0.3, 'pad':10})
    plt.text(820, 1045, 'ACK', style='italic',
        bbox={'facecolor':'green', 'alpha':0.8, 'pad':10})

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

        #draw arrow (example code)
        # plt.arrow(0, 0, 100, 100, head_width=20, head_length=20, width=5, fc='k', ec='k')

        #draw arrowto notate sending RTS
        if router_list[j].state == 'RTS':
            num = router_list[j].receiver
            plt.arrow(router_list[j].x, router_list[j].y, router_list[num].x -router_list[j].x, router_list[num].y - router_list[j].y, head_width=30, head_length=30, width=5, fc='m', ec='m')

    #END drawing section
    if(setting.OUTPUT_PNG):
        plt.savefig('./output_RTS/test%d.png' % timeslot) #uncomment to save as img
    # plt.show() #uncomment to show windows
    plt.gcf().clear()

print supervisor.transfer_success
print "success rate: %0.2f%%" %((supervisor.transfer_success * setting.DATA_LENGTH)/setting.TOTAL_TIME_SLOT * 100)
