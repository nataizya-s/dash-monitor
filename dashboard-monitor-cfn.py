import os
import sys
from sys import exit
import json
import requests
import boto3
import urllib2
import time
from datetime import datetime

# Check-On* Functions Index:
# 0 = engineer
# 1 = state
# 2 = num-of-active-chats
# 3 = durations-of-active-chats
# 4 = num-of-active-phones
# 5 = durations-of-active-phones

#webhook URL
webhook_url = "https://svr6dlsig3.execute-api.us-east-1.amazonaws.com/cross-pod/cfn?function=lc_taken&login="

#phonestats
phone_stats = "http://phonestats.amazon.com/agent/get-agent-statistics-multiple-sites?sites=AWS_PS_NA&report=active-agents&attribute=state&attribute=num-of-active-chats&attribute=durations-of-active-chats&attribute=num-of-active-phones&attribute=durations-of-active-phones"

#table definition - should scan through all the CPT engineer tables to create one consolidated table
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('CfnAvailability')

def checkOnChatContact(engineer):
  if engineer['chat_count'] == 1:
     return True
  else:
     return False

def checkOnCallContact(engineer):
  if engineer['call_count'] == 1:
    return True
  else:
    return False

def get_engineers_from_table():
  #read the engineer availability table
  response = table.scan()

  #get each engineer login
  engineers = []
  for i in response['Items']:
    engineers.append(i['login'])

  return engineers

def get_engineers_from_dash():
  try:  
    text = urllib2.urlopen(phone_stats)
    response = text.read()
    response = response.split('\n')
    engineers_on_dash = []
  #agentLogin,state, state_duration(s),number of active chats, number of chats in ACW, durations for all active chats(s), durations for all chats in ACW(s), number of missed chats
  #e.g. mitayshd,Available,0,0,0,0

    for i in response:
      #the url returns 2 blank lines at the end, so check length of response entry first to avoid out of range errors
      if len(i) > 1:
        engineer_entry = i.split(',')
        login = engineer_entry[0]
        state = engineer_entry[1]
        chat_count = engineer_entry[2]
        call_count = engineer_entry[4]
        engineer_record = {
          'login': login,
          'state': state,
          'chat_count': chat_count,
          'call_count': call_count
        }
        engineers_on_dash.append(engineer_record)
    return engineers_on_dash

  except:
    get_engineers_from_dash()


#site is based on the dynamodb table engineers
def get_engineers_from_dash_in_site(engineers_on_dash, engineers):
  cpt_engineers = []
  for i in engineers_on_dash:
    login = i['login']
    for j in engineers:
       if j == login:
         cpt_engineers.append(i)

  return cpt_engineers

if __name__ == "__main__":
  engineers = get_engineers_from_table()
  engineers_on_dash = get_engineers_from_dash()
  cpt_engineers = get_engineers_from_dash_in_site(engineers_on_dash, engineers)
  on_live_contact = []

  try:
    while True:
      #read engineers on the dash
      engineers_on_dash = get_engineers_from_dash()
      cpt_engineers = get_engineers_from_dash_in_site(engineers_on_dash, engineers)

      #check if any of the engineers states have changed
      for i in cpt_engineers:
        #chats
        if i['chat_count'] == '1' and i['login'] not in on_live_contact:
          on_live_contact.append(i['login'])
          #time = datetime.now()
          #print(i['login'] + " is on a chat an LC at " + time)
          print("An LC (chat) has been taken "+i['login'])
          #update chime
          requests.get(webhook_url + i['login'])
        elif i['call_count'] == '1' and i['login'] not in on_live_contact:
          on_live_contact.append(i['login'])
          #time = datetime.now()
          #print(i['login'] + " is on a call an LC at " + time)
          print("An LC (call) has been taken " + i['login'])
          #update chime
          requests.get(webhook_url + i['login'])
        elif i['chat_count'] == '0' and i['call_count'] == '0' and i['login'] in on_live_contact:
          on_live_contact.remove(i['login'])
          #time = datetime.now()
          print(i['login'] + " just got off a chat at ")
      print("Processing...")
      time.sleep(30)
  except KeyboardInterrupt:
      print('Interrupted')
      sys.exit(0)
