import boto3
import json
import urllib
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal


#dynamoDBオブジェクトを定義
dynamo = boto3.resource('dynamodb')

#タイムゾーンJST(Tokto/Asis)定義
JST = timezone(timedelta(hours=+9),'JST')

#生産日の取得
dt = datetime.now(JST)
if dt.hour==0 or dt.hour<8: dt = dt - timedelta(days=1)
today = dt.strftime('%Y-%m-%d')
print(today)


#生産開始時刻を'%Y-%m-%d %H:%M:%S'で取得する関数
def get_starttime(start_date,start_hour,start_min):
    start_time = start_date + " " + start_hour + ":" + start_min + ":" + "00"
    #print("start_time", start_time)
    return start_time


def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


#Lambda関数
def lambda_handler(event, context):

    #DynamoDBテーブルのオブジェクトを作成し、当日の生産情報を取得
    order_table = dynamo.Table("Order_QA1")
    get_dynamo = order_table.scan()
    #for i in range(7):
    #    get_dynamo = order_table.get_item(
    #        Key={
    #            #主キー情報を設定
    #            'id': i+1,
    #        }
    #   )

    print(get_dynamo)
    
    Item = get_dynamo['Items']
    #Items = {
    #    'items' : Item 
    #}
    
    print(Item)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(Item, default=decimal_default_proc)
    }
