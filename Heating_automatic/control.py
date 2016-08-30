#import paho.mqtt.client as mqtt
import json
import time
import urllib2
import os

indoor_temp = []
in_temp = "10" #default temp
environments = []
src = []
presence = []
current_status = []
max_temp = []
command = []
d1 = []
d2 = []
d3 = []
d4 = []
hostName = ""
num_sec = 2  # seconds to wait before reopening the same url again

def gethostname():
    global hostName
    hostName = raw_input("Enter Host name or host url address = ")
    if hostName == "":
        hostName = "localhost"  # use localhost as a default host if no hostName is entered by the user
        print 'using default host: localhost'
        print "connecting to " + hostName + "..."
    return


#initialize default values and get environment names
def initialize_environments():
    global environments
    global src
    global presence
    global current_status
    global max_temp
    global command
    global d1
    global d2
    global d3
    global d4
    for env_file in os.listdir(os.getcwd()+'/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))
        src.append('default')
        presence.append('-1')  # default presence is -1
        current_status.append('0')
        max_temp.append('23')
        command.append('0')
        d1.append('')
        d2.append('')
        d3.append('')
        d4.append('')
    print environments
    return


def get_presence(env_name):
    url = "https://dweet.io/get/latest/dweet/for/presence_" + env_name
    response = urllib2.urlopen(url)
    output = response.read()
    js = json.loads(output)
    return js


def get_current_status(env_name):
    url = "https://dweet.io/get/latest/dweet/for/current_status_" + env_name
    response = urllib2.urlopen(url)
    output = response.read()
    js = json.loads(output)
    return js


# we assume the same indoor temperature for all environments in a city
def get_indoor_temp(env):
    url = "https://dweet.io/get/latest/dweet/for/indoor_temp_" + env
    response = urllib2.urlopen(url)
    output = response.read()
    js = json.loads(output)
    return js


def set_next_status(env, next_status):
    url = "https://dweet.io/dweet/for/next_status_" + env + "?status=" + next_status + "?source=control"
    response = urllib2.urlopen(url)
    output = response.read()
    js = json.loads(output)
    return js


def on_message():
    global current_status
    global presence
    global indoor_temp
    global in_temp
    global src
    global d1
    global d2
    global d3
    global d4
    global environments
    while True:
        i = 0
        for env_name in environments:
            d1[i] = get_current_status(env_name)
            print d1
            if d1[i]["this"] == "Succeeded":
                current_status[i] = d1[i]["with"][0]["content"]["status"]
                # src[i] = d1[i]["with"][0]["source"]
                print "status " + str(env_name) + " received: " + str(current_status[i])

            # reads aggregate user_presence and presence_interval (0=no_user_presence and out of interval)
            #(1=no_user_presence but during interval), (2=user_presence and whatever interval)
            d2[i] = get_presence(env_name)
            print d2
            if d2[i]["this"] == "Succeeded":
                presence[i] = d2[i]["with"][0]["content"]["presence"]
                print "presence " + str(env_name) + ": " + str(presence[i])

            d3[i] = get_indoor_temp(env_name)
            print d3
            if d3[i]["this"] == "Succeeded":
                indoor_temp[i] = d3[i]["with"][0]["content"]["temp"]
                print "Indoor temperature of " + str(env_name) + " is: " + str(indoor_temp[i])
            if src[i] == "switch":
                n = 6  # this could be an input from a form
                time.sleep(n)  # for n seconds the user can interrupt the automatic mode, then the system comes back to
                # automatic mode
                src[i] = "default"
            #check if there's someone and the indoor temperature is not enough
            if presence[i] == "2" and int(indoor_temp[i]) < int(max_temp[i]):
                command[i] = "1"
            elif presence[i] == "1" and int(indoor_temp[i]) < 20:
                command[i] = "1"
            else:
                command[i] = "0"
            print "command " + str(env_name) + ': ' + str(command[i])
            print "current status of " + str(env_name) + ': ' + str(current_status[i])

            if current_status[i] == command[i]:
                print "The web switch for " + str(env_name) + " is already " + str(command[i])
            else:
                # send a command to change the status
                d4[i] = set_next_status(env_name, current_status[i])
                current_status[i] = command[i]
                if d4["this"] == "succeeded":
                    print "A message has been sent to set the web switch status of " + str(env_name) + " to : " + \
                          str(current_status[i])

            i += 1
        time.sleep(num_sec)
gethostname()
initialize_environments()
on_message()
