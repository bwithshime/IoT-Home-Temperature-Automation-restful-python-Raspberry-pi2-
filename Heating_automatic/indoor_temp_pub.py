import time
import json
import urllib2
import datetime
import os

environments = []
hostName = ""


#initialize default values and get environment names
def gethostname():
    global hostName
    hostName = raw_input("Enter host name or host url address = ")
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
    print 'Connected to: ' + hostName
    return


def get_indoor_temps(hour):  # indoor temperature sensor simulator for each created environment
    global environments
    #simulated indoor temperatures
    time_t = str(hour) + ":00"
    data_d = []
    for env in environments:
        fp = open(os.getcwd() + '/indoor_temperatures/indoor_temp_' + env + '.txt')
        d = json.loads(fp.read())
        d = d[time_t]
        data_d.append(str(d))
    return time_t, data_d


initialize_environments()
now = datetime.datetime.now()
h = now.hour
url = "https://dweet.io/dweet/for/indoor_temp_"


while True:
    num_sec = 4  # seconds to wait to change the indoor temperature again
    time_t, indoor_temps = get_indoor_temps(h)
    now = datetime.datetime.now()
    minutes = now.minute
    seconds = now.second
    print 'Current Time is: ' + str(h) + ':' + str(minutes) + ':' + str(seconds)
    for env in environments:
        url_tmp = url + str(env) + "?temp=" + str(indoor_temps[environments.index(env)])
        response = urllib2.urlopen(url_tmp)
        print 'Indoor Temperature for ' + env + ' is : ' + str(indoor_temps[environments.index(env)])
        print (response.read())
        time.sleep(2)   # 2 seconds: time to wait for the urlopen to respond for each url_tmp open
        print('result captured for indoor temperature: ' + str(indoor_temps[environments.index(env)]) + " of " + str(env))
    time.sleep(num_sec)  # the temperature sensor (simulator) generates new temperature value every num_sec seconds
    h = (int(h) + 1) % 24  # the value of h is in 24 hour format