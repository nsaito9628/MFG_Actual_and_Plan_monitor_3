import boto3
from boto3.dynamodb.conditions import Key
import json
import urllib
import time
from datetime import datetime, timedelta, timezone

#dynamoDBオブジェクトを定義
dynamo = boto3.resource('dynamodb')

#タイムゾーンJST(Tokto/Asis)定義
JST = timezone(timedelta(hours=+9),'JST')

#生産日の取得
dt = datetime.now(JST)
if dt.hour==0 or dt.hour<8: dt = dt - timedelta(days=1)
today = dt.strftime('%Y-%m-%d')
print(today)

def decimal_default_proc(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


#Lambda関数
def lambda_handler(event, context):

    #DynamoDBテーブルのオブジェクトを作成し、当日の生産情報を取得
    plan_table = dynamo.Table("Plan_ALL")
    #get_dynamo = plan_table.get_item(
    #    Key={
    #        #主キー情報を設定
    #        'date': today,
    #    }
    #)
    get_dynamo =  plan_table.query(
        KeyConditionExpression = Key('Line_Name').eq('QA1')
    )
    
    #get_dynamo =  plan_table.scan()
    
    print(get_dynamo)

    Item = get_dynamo['Items']

    raw_starttime = Item[0]['start_time']#生産開始時間
    str_starttime = (datetime.strptime(raw_starttime, '%Y-%m-%d %H:%M:%S')).strftime('%H:%M:%S')
    if dt.weekday() == 0: str_starttime = "09:00:00"

    raw_finishtime = Item[0]['finish_time']#生産開始時間
    str_finishtime = (datetime.strptime(raw_finishtime, '%Y-%m-%d %H:%M:%S')).strftime('%H:%M:%S')

    Item[0]['start_time'] = str_starttime
    Item[0]['finish_time'] = str_finishtime
    Item[0]['date'] = today
    
    print(Item)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(Item, default=decimal_default_proc)
    }
