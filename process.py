import json
import sys
import requests

cont = True
url = 'https://svr6dlsig3.execute-api.us-east-1.amazonaws.com/cross-pod/cfn/state?'
while cont == True:
    login = raw_input("Enter engineer login: ")
    state = raw_input("Enter desired state: ")

    if login != 'exit' or login != 'e':
        cont = True
        url_end='login='+login+'&state='+state
        url=url+url_end
        print url
        r = requests.post(url)
        print r
    else:
        cont = False
