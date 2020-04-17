import boto3
import json
import urllib
import time
from datetime import datetime, timedelta, timezone

dynamo = boto3.resource('dynamodb')

def ordered_time_table_creation(DB_name, t_list, start_time, prod_num):

    endflag = 0
    order_table = dynamo.Table(DB_name)

    if "BUFF" in DB_name: CT = 9
    elif "CNC" in DB_name: CT = 20
    else: CT = 10

    #print(DB_name)
    for i in range(len(t_list)):
        downtime = t_list[i][2]
        actual_time = t_list[i][1] - downtime - start_time

        tmp_time = t_list[i][1].strftime('%H:%M')
        plan = int(actual_time.total_seconds()/CT)
        actual = str(actual_time)
        planed_down = str(downtime)
        
        print(plan, prod_num)

        if plan >= int(prod_num) and endflag == 0: 
            delta_N_last = int(prod_num) - int((t_list[i][1]-start_time-downtime).total_seconds() / CT)
            #print(delta_N_last)
            delta_t_last = int(delta_N_last * CT)
            finish_time = str(t_list[i][1] + timedelta(seconds=delta_t_last))
            #print('finish_time:', finish_time)

            endflag = 1
        
        if endflag == 1: plan = int(prod_num)

        order_table.put_item(
            Item = {
                "id" : i+1,
                "time" : tmp_time, 
                "plan" : plan,
                "actual_time" : actual,
                "downtime" : planed_down
            }
        )
    
    if int(prod_num) == 0 or prod_num is None: finish_time = str(start_time)

    return finish_time