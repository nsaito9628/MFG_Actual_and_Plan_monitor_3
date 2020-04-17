import time
from datetime import datetime, timedelta, timezone, time
import math


#タイムゾーンJST(Tokto/Asis)定義
JST = timezone(timedelta(hours=+9),'JST')

#生産日の取得
dt = datetime.now(JST)
if dt.hour==0 or dt.hour<6: dt = dt - timedelta(days=1)
today = dt.strftime('%Y-%m-%d')

start_time = datetime.strptime((today + " 8:30:00"), '%Y-%m-%d %H:%M:%S')


#不稼働を除いた生産インターバルの開始時間と終了時間(t_list[])、不稼働を除いた加工・ドレスインターバルの開始時間と終了時間(check_point[])を作成する関数
def startend_list_generator(today, start_time, lunch, PM_SP, even_mtg, ely_end1, ely_end2):

    check_point = []
    
    t_list = t_list_generator(today,start_time, lunch, PM_SP, even_mtg,  ely_end1, ely_end2)

    check_point = list_init(t_list,check_point)

    print("t_list length:",len(t_list))
    for i in range(len(t_list)):
        if i != 0: check_point = list_append(i,t_list,check_point)
        
    #for i in range(len(t_list)):print(t_list[i])
    for i in range(len(check_point)):
        print(i,check_point[i][0],check_point[i][1],check_point[i][2],check_point[i][3],check_point[i][4],check_point[i][5],check_point[i][6],check_point[i][7])

    return t_list, check_point


#不稼働条件flagを受け取ってt_list[]を修正する関数
def t_list_generator(today, start_time, lunch, PM_SP, even_mtg,  ely_end1, ely_end2):

    t_list = []
    dt_prod_start = []
    dt_prod_end = []
    sorted_prod_start = []
    sorted_prod_end = []
    sorted_t_list = []

    str_stime = start_time.strftime('%H:%M:%S')

    prod_start = [str_stime,"10:05:00","12:50:00","15:05:00","16:50:00","18:40:00","20:45:00","23:10:00","1:05:00","2:45:00"]
    prod_end = ["10:00:00","12:00:00","15:00:00","16:40:00","18:40:00","20:40:00","22:30:00","1:00:00","2:35:00","4:35:00"]

    if (start_time.hour == 10 and start_time.minute >= 5) or (10 < start_time.hour <12):
        del prod_start[1]
        del prod_end[0]

    if (start_time.hour == 12 and start_time.minute >= 50) or (12 < start_time.hour <15):
        lunch = "0"
        del prod_start[1:3]
        del prod_end[0:2]
    
    if (start_time.hour == 15 and start_time.minute >= 5) or (start_time.hour == 16 and start_time.minute < 40):
        lunch = "0"
        PM_SP = "0"
        del prod_start[1:4]
        del prod_end[0:3]
    
    if (start_time.hour == 16 and start_time.minute >= 40) or (start_time.hour == 18 and start_time.minute < 40):
        lunch = "0"
        PM_SP = "0"
        even_mtg = "0"
        ely_end1 = "0"
        ely_end2 = "0"
        del prod_start[1:5]
        del prod_end[0:4]
        #prod_start.append("18:45:00")
        #prod_start.sort()###
        #prod_end.append("18:40:00")
        #prod_end.sort()###

    if start_time.hour == 18 and start_time.minute >= 40:
        lunch = "0"
        PM_SP = "0"
        even_mtg = "0"
        ely_end1 = "0"
        ely_end2 = "0"
        del prod_start[1:6]
        del prod_end[0:5]

    if lunch == "1" and PM_SP == "0":
        del prod_start[2]
        del prod_end[1]

    if PM_SP == "1" and lunch == "0":
        del prod_start[2:5]
        del prod_end[2:5]
        even_mtg == "0"
        ely_end1 == "0"
        ely_end2 == "0"
        
    if PM_SP == "1" and lunch == "1":
        del prod_start[2:5]
        del prod_end[1:5]
        prod_end.append("12:50:00")
        even_mtg == "0"
        ely_end1 == "0"
        ely_end2 == "0"
        
    if even_mtg == "1" and lunch == "0":
        del prod_end[3]
        prod_end.append("16:10:00")
        #prod_end.sort()###

    if even_mtg == "1" and lunch == "1":
        del prod_end[2]
        prod_end.append("16:10:00")
        #prod_end.sort()###

    if ely_end1 == "1" and PM_SP == "0" and lunch == "0":
        del prod_start[4]
        del prod_end[4]

    if ely_end2 == "1" and PM_SP == "0" and lunch == "0":
        del prod_start[4]
        del prod_end[4]
        prod_start.append("16:45:00")
        prod_end.append("17:40:00")

    if ely_end1 == "1" and PM_SP == "0" and lunch == "1":
        del prod_start[3]
        del prod_end[3]

    if ely_end2 == "1" and PM_SP == "0" and lunch == "1":
        del prod_start[3]
        del prod_end[3]
        prod_start.append("16:45:00")
        prod_end.append("17:40:00")
    
    #print(len(prod_start))
    for i in range(len(prod_start)):
        dt_prod_start.append(datetime.strptime(today +" "+ prod_start[i], '%Y-%m-%d %H:%M:%S'))
        dt_prod_end.append(datetime.strptime(today+" "+prod_end[i], '%Y-%m-%d %H:%M:%S'))

        #if i == 0: dt_downtime.append(timedelta(seconds=0))
        #if 0 < i <= len(prod_start): dt_downtime.append(prod_start[i] - prod_end[i-1])

    sorted_prod_start = sorted(dt_prod_start)
    sorted_prod_end = sorted(dt_prod_end)
    last_end = sorted_prod_end.pop(0)
    sorted_prod_end.append(last_end)


    for i in range(len(prod_start)):
        t_list.append([sorted_prod_start[i],sorted_prod_end[i]])
        if 0 <= t_list[i][0].hour <8 : t_list[i][0] = t_list[i][0] + timedelta(days=1)
        if 0 <= t_list[i][1].hour <8 : t_list[i][1] = t_list[i][1] + timedelta(days=1)
        #print(t_list[i])
    
    sorted_t_list = sorted(t_list, key = lambda s: s[0])
    for i in range(len(prod_start)):
        if i == 0: dt_downtime = timedelta(seconds=0)
        if 0 < i <= len(prod_start): dt_downtime = sorted_t_list[i-1][2] + sorted_t_list[i][0] - sorted_t_list[i-1][1]
        sorted_t_list[i].append(dt_downtime)

        print(sorted_t_list[i][0],sorted_t_list[i][1],sorted_t_list[i][2])

    return sorted_t_list


#BUFFの加工・ドレスインターバルを加味したt_listを作成する関数
def t_list_generator_buff(today, start_time, lunch, PM_SP, even_mtg, ely_end1, ely_end2):

    check_point = []
    
    t_list = t_list_generator(today,start_time, lunch, PM_SP, even_mtg,  ely_end1, ely_end2)

    check_point = list_init(t_list,check_point)

    print("t_list length:",len(t_list))
    for i in range(len(t_list)):
        if i != 0: check_point = list_append(i,t_list,check_point)
        
    #for i in range(len(t_list)):print(t_list[i])
    #for i in range(len(check_point)):
    #    print(i,check_point[i][0],check_point[i][1],check_point[i][2],check_point[i][3],check_point[i][4],check_point[i][5],check_point[i][6],check_point[i][7])

    for i in range(len(t_list)):
        for j in range(len(check_point)):
            if t_list[i][1] == check_point[j][2]:
                t_list[i][2] = t_list[i][2] + check_point[j][5]*timedelta(seconds=600)
                print(t_list[i][0],t_list[i][1],t_list[i][2])

    return t_list


#不稼働条件修正済みのt_list[]を受け取って、check_point[]内の変数定義と生産開始時(一回目)の加工サイクル開始終了時刻計算する関数
def list_init(t_list,check_point):
    
    #リスト内変数要素の初期化
    op_start = t_list[0][0] -timedelta(seconds=0)
    op_end = timedelta(seconds=0)
    dress_end = t_list[0][0]-timedelta(seconds=0)
    op_remained = timedelta(seconds=0)
    dr_remained = timedelta(seconds=0)
    
    cycle_count = -1

    OP_flag = 0
    DR_flag = 0
    
    #生産開始時のドレス回数
    dress_num = (t_list[0][1]-t_list[0][0]).total_seconds()/3096
    count = math.ceil(dress_num)
    #print(dress_num,count)
    
    #加工サイクル開始終了時刻の計算
    for i in range(count):
        op_start = dress_end
        op_end = op_start + timedelta(seconds=2496)
        dress_end = op_start + timedelta(seconds=3096)
        if op_end >= t_list[0][1]:
            op_remained = op_end - t_list[0][1]
            op_end = t_list[0][1]
            dr_remained = timedelta(minutes=10)
            dress_end = t_list[0][1]
            OP_flag = 1
        if dress_end >= t_list[0][1] and op_end < t_list[0][1]:
            dr_remained = dress_end - t_list[0][1]
            dress_end = t_list[0][1].hour
            DR_flag = 1

        cycle_count = cycle_count + 1
        check_point.append([op_start, op_end, dress_end, op_remained, dr_remained, cycle_count, OP_flag, DR_flag])
        #print(op_start,op_end,dress_end,cycle_count,op_remained, dr_remained, OP_flag, DR_flag, cycle_count)
        #print(check_point[i])
    return check_point


#不稼働条件修正済みのt_list[]を受け取って、二回目以降の加工サイクル開始終了時刻計算してcheck_point[]で返すする関数
def list_append(i,t_list,check_point):

    #生産開始時のドレス回数
    #print(i,check_point[-1][3],check_point[-1][4],check_point[-1][6],check_point[-1][7])
    dress_num = (t_list[i][1]-t_list[i][0]-check_point[-1][3]-check_point[-1][4]).total_seconds()/3096
    count = math.ceil(dress_num)
    #print(dress_num,count)
    
    op_start = t_list[i][0]#ユニットごとの生産開始は不稼働終了時間
    cycle_count = check_point[-1][5]
    

    if check_point[-1][6] == 1:#OP_flag
        op_end = op_start + check_point[-1][3]
        #print(op_end)
        
        dress_end = op_end + check_point[-1][4]
        #print(dress_end)

        OP_flag = 0
        DR_flag = 0
        op_remained = timedelta(seconds=0)
        dr_remained = timedelta(seconds=0)
        
        check_point.append([op_start, op_end, dress_end, op_remained, dr_remained, cycle_count, OP_flag, DR_flag])

    elif check_point[-1][7] == 1:#DR_flag
        op_end = op_start
        #print(op_end)

        dress_end = op_end + check_point[-1][4]
        
        #print(dress_end)

        OP_flag = 0
        DR_flag = 0
        op_remained = timedelta(seconds=0)
        dr_remained = timedelta(seconds=0)
        
        check_point.append([op_start, op_end, dress_end, op_remained, dr_remained, cycle_count, OP_flag, DR_flag])        

    #print(op_start,op_end,dress_end,cycle_count,op_remained, dr_remained, OP_flag, DR_flag, cycle_count)
    
    for j in range(count):
        op_start = dress_end
        op_end = op_start + timedelta(seconds=2496)
        dress_end = op_start + timedelta(seconds=3096)
        if op_end >= t_list[i][1]:
            op_remained = op_end - t_list[i][1]
            op_end = t_list[i][1]
            dr_remained = timedelta(minutes=10)
            dress_end = t_list[i][1]
            OP_flag = 1
            #print(op_remained)
            #print(dr_remained)
        if dress_end >= t_list[i][1] and op_end < t_list[i][1]:
            dr_remained = dress_end -t_list[i][1]
            dress_end = t_list[i][1]
            DR_flag = 1
            #print(op_remained)
            #print(dr_remained)
        
        cycle_count = cycle_count +1
        check_point.append([op_start, op_end, dress_end, op_remained, dr_remained, cycle_count, OP_flag, DR_flag])
        #print(op_start,op_end,dress_end,cycle_count,op_remained, dr_remained, OP_flag, DR_flag, cycle_count)

    return check_point

if __name__ == '__main__':

    now = datetime.now(JST)

    #t_list = t_list_generator(today,start_time, 0, 0, 0, 0, 0)
    t_list, check_point = startend_list_generator(today, start_time, "0", "0", "0", "0", "0")
    t_list = t_list_generator_buff(today, start_time, "0", "0", "0", "0", "0")
    #startend_list_generator(today, start_time, lunch, PM_SP, even_mtg, ely_end1, ely_end2):

    #for i in range(len(t_list)):print(t_list[i])
    #for i in range(len(t_list)):
        #print(t_list[i][0], t_list[i][1], t_list[i][2])
    #for i in range(len(check_point)):
        #print(check_point[i][0],check_point[i][1],check_point[i][2],check_point[i][3],check_point[i][4],check_point[i][5],check_point[i][6],check_point[i][7])
