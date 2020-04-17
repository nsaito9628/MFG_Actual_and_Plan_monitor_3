import boto3
import json
import urllib
import time
from datetime import datetime, timedelta, timezone
from time_list_gen import t_list_generator, t_list_generator_buff
from ordered_time_table import ordered_time_table_creation


print('Loading function')
dynamo = boto3.resource('dynamodb')

#タイムゾーンJST(Tokto/Asis)を定義
JST = timezone(timedelta(hours=+9),'JST')
#生産開始時刻を'%Y-%m-%d %H:%M:%S'で取得する関数
def get_starttime(start_date,start_hour,start_min):
    start_time = start_date + " " + start_hour + ":" + start_min + ":" + "00"
    #print("start_time", start_time)
    return start_time
    
#Lambda関数
def lambda_handler(event, context):
    #print(json.dumps(event, indent=2))

    Line_name = "CNC1", "CNC2", "CNC3", "CNC4", "BUFF1", "BUFF2", "BUFF3", "QA1", "QA2"
    data_type = "prod_type", "prod_num", "start_hour", "start_min"
    orderDB_name = {"CNC1" : "Order_CNC1", "CNC2" : "Order_CNC2", "CNC3" : "Order_CNC3", "CNC4" : "Order_CNC4", "BUFF1" : "Order_BUFF1", "BUFF2" : "Order_BUFF2", "BUFF3" : "Order_BUFF3", "QA1" : "Order_QA1", "QA2" : "Order_QA2"}
    planDB_name = "Plan_ALL"

    #web画面で入力された初期値の獲得
    get_json = dict(event['body']) 
    #print(get_json)

    #生産日の取得
    dt = datetime.now(JST)
    if dt.hour==0 or dt.hour<8: dt = dt - timedelta(days=1)
    today = dt.strftime('%Y-%m-%d')

    #生産開始時刻、連続稼働の切れる時刻と定時刻毎の不稼働時間積算リストを取得   
    str_start_time = {}
    start_time = {}
    t_list = {}
    finish_time = {}

    for Line in Line_name:
        str_start_time[Line] = get_starttime(today, get_json[Line]['start_hour'],get_json[Line]['start_min'])
        start_time[Line] = datetime.strptime(str_start_time[Line], '%Y-%m-%d %H:%M:%S')
        if "BUFF" in Line: 
            t_list[Line] = t_list_generator_buff(today, start_time[Line], "0", "0", "0", "0", "0")
            finish_time[Line] = ordered_time_table_creation(orderDB_name[Line], t_list[Line], start_time[Line], get_json[Line]['prod_num'])
            continue
        t_list[Line] = t_list_generator(today, start_time[Line], "0", "0", "0", "0", "0")
        finish_time[Line] = ordered_time_table_creation(orderDB_name[Line], t_list[Line], start_time[Line], get_json[Line]['prod_num'])

    plan_table = dynamo.Table(planDB_name)
    for Line in Line_name:
        plan_table.put_item(
            Item = {
                'Line_Name' : Line,
                'date' : today,
                'prod_type' : get_json[Line]['prod_type'],
                'prod_num' : get_json[Line]['prod_num'],
                'start_time' : str_start_time[Line],
                'finish_time' : finish_time[Line]
            }
        )
 