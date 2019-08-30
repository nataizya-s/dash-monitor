import json
import requests
import boto3
import urllib2
import time
from datetime import datetime

phone_stats = "http://phonestats.amazon.com/agent/get-agent-statistics-multiple-sites?sites=AWS_PS_NA&report=active-agents&attribute=state&attribute=num-of-active-chats&attribute=durations-of-active-chats&attribute=num-of-active-phones&attribute=durations-of-active-phones"

def get_engineers_from_dash():
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
      engineer_record = {
        'login': login,
        'state': state
        }
      engineers_on_dash.append(engineer_record)
  return engineers_on_dash

while True:
  e = get_engineers_from_dash() 
  for i in e:
    if i['state'] == 'On':
      print(i['login'])
