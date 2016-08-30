import time
import random
import urllib2
import datetime
import os

hour = "8:00"  # default current hour
url = "https://dweet.io/dweet/for/indoor_temp_"

environments = []
hostName = ""

#initialize default values and get environment names
def gethostname():
    global hostName
    hostName = raw_input("Enter Host name or host url address = ")
    if hostName == "":
        hostName = "localhost"  # use localhost as a default host if no hostName is entered by the user
        print 'using default host: localhost'
        print "connecting to " + hostName + "..."
    return
gethostname()


def initialize_environments():
    global environments
    for env_file in os.listdir(os.getcwd()+'/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))
    print 'connected to: ' + hostName
    return


def get_indoor_temps():
    indoor_temperatures = []
    for env in environments:
         # the user can (if he wishes) update the value of the indoor temperature manually
        indoor_temperature = raw_input("Enter current indoor temperature for " + env + ": ")
        while not indoor_temperature.isdigit():
            print('Invalid value for indoor temperature! Please enter again!')
            indoor_temperature = raw_input("Enter current indoor temperature for " + env + ": ")
        indoor_temperatures.append(indoor_temperature)
    return indoor_temperatures


now = datetime.datetime.now()
h = now.hour
initialize_environments()
while True:
    #ts = int(time.time())
    num_sec = 4  # seconds to wait to change the indoor temperature again
    hour = str(h) + ":00"
    indoor_temps = get_indoor_temps()
    print indoor_temps
    for env in environments:
        url_tmp = url + str(env) + "?temp=" + str(indoor_temps[environments.index(env)])
        response = urllib2.urlopen(url_tmp)
        print(response.read())
        time.sleep(2)   # 2 seconds: time to wait for the urlopen to respond for each url_tmp
        print('result captured for indoor temperature: ' + str(indoor_temps[environments.index(env)]) + " of "+str(env))
    time.sleep(num_sec)  # the user can (if he wishes) update the value of the indoor temperature sensor manually
    # every num_sec seconds
