'''
A Slack Bot that works like an attendance bot.
The user has 4 options:
-> IN: His time of arrival is stored 
-> OUT: His time of leaving is stored
-> HOLIDAY: He plans to take a holiday
-> ABSENT: He will be absent
'''

from slackeventsapi import SlackEventAdapter
from slackclient import SlackClient
import json
import mysql.connector
import sys
from datetime import datetime

tokens = {}
with open('configs.json') as json_data:
    tokens = json.load(json_data)

slack_events_adapter = SlackEventAdapter(tokens.get("slack_signing_secret"), "/slack/events")
slack_client = SlackClient(tokens.get("slack_bot_token"))




REGION = 'us-east-1'

#AWS RDS Database
rds_host = ".rds.amazonaws.com"      #RDS Host link
name = ""               #Enter name of the user
password1 = ""      #Enter password
db_name = "slackbotdatabase"    #Name of the database

#Calculating date and time
x = str(datetime.now())
print(x)
date = x[0:10]
time = x[11:19]

null = None

#Connecting the program to the database
conn = mysql.connector.connect(host=rds_host, user=name, password=password1, db=db_name, connect_timeout=100)

print('connected!')

#In any event that a user types a message in the AttendanceBot channel
@slack_events_adapter.on("message")
def handle_message(event_data):
    message = event_data["event"]

    #When the user types IN his ID,NAME and TIME of entering is stored in the database
    if message.get("subtype") is None and "IN" in message.get('text'):
        channel = message["channel"]
        name1 = message["user"]
        send_message = "User <@%s> has punched 'IN'." % name1
        slack_client.api_call("chat.postMessage", channel=channel, text=send_message)        
        cur = conn.cursor()
        cur.execute ("insert into employee(id,name,date,time_in,state) values(11,'"+name1+"','"+date+"','"+time+"','Present')")
        
        #If he comes after 2pm a HALF DAY is stored
        if time > '14:00:00':
            cur.execute("update employee set state = 'Half Day' where name = '"+name1+"' ")
        cur.execute("select * from employee")
        result = cur.fetchall()
        conn.commit()
        cur.close()
        print("Reading from RDS...")
        print(result)
        
    #When the user types OUT his time of leaving is stored in the database 
    if message.get("subtype") is None and "OUT" in message.get('text'):
        name1 = message["user"]
        channel = message["channel"]
        send_message = "User <@%s> has punched 'OUT'."%message["user"]
        slack_client.api_call("chat.postMessage",channel=channel, text=send_message)
        cur = conn.cursor()
        cur.execute("update employee set time_out = '"+time+"' where name = '"+name1+"' ")

        #If he leaves before 4pm a HALF DAY is stored
        if time < '16:00:00':
            cur.execute("update employee set state = 'Half Day' where name = '"+name1+"' ")
        cur.execute("select * from employee")
        result = cur.fetchall()
        conn.commit()
        cur.close()
        print("Reading form RDS")
        print(result)
        print(date)
        print(time)
    
    #When the user types HOLIDAY, HOLIDAY is stored in the database 
    if message.get("subtype") is None and "Holiday" in message.get('text'):
        name1 = message["user"]
        channel = message["channel"]
        send_message = "User <@%s> has taken a 'Holiday'."%message["user"]
        slack_client.api_call("chat.postMessage",channel=channel, text=send_message)
        cur = conn.cursor()
        cur.execute ("insert into employee(id,name,date,state) values(94,'"+name1+"','"+date+"','Holiday')")
        cur.execute("select * from employee")
        result = cur.fetchall()
        conn.commit()
        cur.close()
        print("Reading form RDS")
        print(result)

    #When the user types ABSENT, ABSENT is stored in the database
    if message.get("subtype") is None and "Absent" in message.get('text'):
        name1 = message["user"]
        channel = message["channel"]
        send_message = "User <@%s> will be 'Absent'."%message["user"]
        slack_client.api_call("chat.postMessage",channel=channel, text=send_message)
        cur = conn.cursor()
        cur.execute ("insert into employee(id,name,date,state) values(95,'"+name1+"','"+date+"','Absent')")
        cur.execute("select * from employee")
        result = cur.fetchall()
        conn.commit()
        cur.close()
        print("Reading form RDS")
        print(result)


@slack_events_adapter.on("error")
def error_handler(err):
    print("ERROR: " + str(err))

#Starting the slack server
slack_events_adapter.start(port=3306)
