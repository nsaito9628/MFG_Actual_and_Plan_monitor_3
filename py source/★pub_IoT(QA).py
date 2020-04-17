#IoT coreよりjsonがsubscribeされたらeventが発生して呼び出されるLambda関数

import boto3
from boto3.dynamodb.conditions import Key
import json
import urllib
import time
from datetime import datetime, timedelta, timezone, time
from time_list_gen import t_list_generator


print('Loading function')

get_dynamo = {}
put_dynamo = {}
CT = 10

#dynamoDBオブジェクトを定義
dynamo = boto3.resource('dynamodb')

#IoT-dataオブジェクトとトピックを定義
iot = boto3.client('iot-data')
topic = 'No1QA/plan-actual' #トピックを各Lineに変更してlambdaに実装

#タイムゾーンJST(Tokto/Asis)定義
#JST = timezone(timedelta(hours=+9),'JST')

#生産日の取得
dt = datetime.now() + timedelta(hours=9)
if dt.hour==0 or dt.hour<6: dt = dt - timedelta(days=1)
today = dt.strftime('%Y-%m-%d')
print(today)


#計画不稼働時間を除外して実負荷時間を算出する関数
def exclude_downtime(now, str_starttime, today, lunch, PM_SP, even_mtg, ely_end1, ely_end2):

    t_list = []

    start_time = datetime.strptime(str_starttime, '%Y-%m-%d %H:%M:%S')
    
    t_list = t_list_generator(today, start_time, lunch, PM_SP, even_mtg,  ely_end1, ely_end2)

    #設備稼働中の不稼働時間の折り込み
    for i in range(len(t_list)):
        if t_list[i][0] <= now < t_list[i][1]:
            str_now = (now - t_list[i][2]).strftime('%Y-%m-%d %H:%M:%S') #t_list[i][2]:定常downtime

    #設備停止中の不稼働時間の折り込み
    for i in range(len(t_list)):
        #休憩時間
        if (i < len(t_list)-1) and (t_list[i][1] <= now < t_list[i+1][0]):
            str_now = (t_list[i][1] - t_list[i][2]).strftime('%Y-%m-%d %H:%M:%S') #t_list[i][2]:定常downtime

    print("只今の実負荷時間:",str_now)

    return str_now


#予実の計算結果をIoT coreにpublishする関数
def pub_json(topic,N_plan,N_delta):
    payload = {
        "N_plan": N_plan,
        "N_delta": N_delta
    }
    
    try:
        #メッセージをPublish
        iot.publish(
            topic=topic,
            qos=0,
            payload=json.dumps(payload, ensure_ascii=False)
        )
 
        return "Succeeeded."
    
    except Exception as e:
        print(e)
        return "Failed."


#lambda関数
def lambda_handler(event, context):

    #DynamoDBテーブルのオブジェクトを作成し、Production_Plansテーブルから当日の生産情報を取得
    plan_table = dynamo.Table("Plan_ALL")
    get_dynamo = plan_table.get_item(
        Key={
            #主キーを各Lineに変更してlambdaに実装
            'Line_Name': "QA1",
        }
    )
    #テーブル中でItemにネストされてる条件と項目を抽出
    raw_starttime = get_dynamo['Item']['start_time']#生産開始時間
    num_plan = int(get_dynamo['Item']['prod_num'])#当日生産数
    #lunch = get_dynamo['Item']['lunch_support_QA1']#1S昼稼働
    #PM_SP = get_dynamo['Item']['PMstop1S_QA1']#1S PM停止(作業者半休等)
    #even_mtg = get_dynamo['Item']['even_meeting_QA1']#全体夕礼
    #ely_end1 = get_dynamo['Item']['16:40_end_QA1']#1S 16:40終了
    #ely_end2 = get_dynamo['Item']['17:40_end_QA1']#1S 17:40終了
    #print("start_time: ", str_starttime, "num_plan: ", num_plan)

    str_starttime = today + " " + (datetime.strptime(raw_starttime, '%Y-%m-%d %H:%M:%S')).strftime('%H:%M:%S')
    if dt.weekday() == 0: str_starttime = today + " " + "09:00:00"
    print("raw_time: ",raw_starttime, "str_starttime: ", str_starttime)

    #現在時刻を取得
    now = datetime.now() + timedelta(hours=9)
    
    #start_timeをdatetimeに変換
    start_time = datetime.strptime(str_starttime, '%Y-%m-%d %H:%M:%S')
    print("開始時間: ", start_time)
    
    #現在時刻とのtime_deltaを算出
    time_delta = datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S'),'%Y-%m-%d %H:%M:%S') - start_time
    print("経過時間: ", time_delta)
    
    if  time_delta.total_seconds() >= 0:
        print("now: ",now)
        #正味の積算負荷時間を算出
        str_now = exclude_downtime(now, str_starttime, today, "0", "0", "0", "0", "0")
        print(str_now)

        #str_nowをdatetimeオブジェクトnowに変換
        now = datetime.strptime(str_now, '%Y-%m-%d %H:%M:%S')
        print("now(after_delta): ", now)
    
        #ラズパイからIoT coreにsubscribeされたjsonからトータル実生産数量を抽出
        N_actual = event['dailynumber']
        print("N_actual: ",  N_actual)
    
        #正味の積算負荷時間と現在時刻とのtime_deltaを算出
        time_delta = now - start_time
        print("経過時間: ", time_delta)
    
        #time_deltaをCTで割って現在時刻の予定生産数を算出
        N_plan = int(time_delta.total_seconds() / CT)
        #生産予定漸近線が予定生産数に達したら、それ以降N_planをnum_planに置き換える
        if N_plan > num_plan: N_plan = num_plan
        print("N_plan: ", N_plan)
    
        N_delta = N_actual - N_plan 
        print("N_delta: ", N_delta)
    
        status = pub_json(topic,N_plan,N_delta)
        print(status)