#import multiprocessing
from threading import Thread
from Queue import Queue
import json
import urllib2
import time
import os

hostName = ""
shared_queue = Queue(500)
current_status = []
environments = []
base_url = "https://dweet.io/get/latest/dweet/for/current_status_"
last_update = []
js = []
thing_speak_url = 'https://api.thingspeak.com/update?api_key='
num_sec = 2  # seconds to wait if buffer is not initialized yet before trying again


def get_host_name():
    global hostName
    hostName = raw_input("Enter Host name or host url address = ")
    if hostName == "":
        hostName = "localhost"  # use localhost as a default host if no hostName is entered by the user
        print 'using default host: localhost'
    print "connecting to " + hostName + "..."
    time.sleep(1)
    return


def get_api_key():
    global thing_speak_url
    write_key = raw_input("Please enter the api_key: ")
    if write_key == "":  # if no api_key is entered by user, use the default
        write_key = "J59X807EDCUN7KEO"  # default api_key for my channel
        print 'Using "' + write_key + '" as default api_key:'
    thing_speak_url =  thing_speak_url + write_key

def initialize_environments():
    global environments
    global last_update
    global js
    global current_status
    #initialize default values and get environment names
    for env_file in os.listdir(os.getcwd()+'/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))
        last_update.append("default")
        js.append("default")
        current_status.append('0')
    print 'connected to: ' + hostName
    print 'Available environments: ' + str(environments)



class ToBufferThread(Thread):
    def run(self):
        global shared_queue
        global current_status
        global environments
        global last_update
        while True:
            i = 0
            for env_name in environments:
                response = urllib2.urlopen(base_url + env_name)
                output = response.read()
                js[i] = json.loads(output)
                print js[i]
                if js[i]["this"] == "succeeded":
                    t = js[i]["with"][0]["created"]
                    if str(t) != str(last_update[i]):
                        last_update[i] = t
                        current_status[i] = js[i]["with"][0]["content"]["status"]
                        shared_queue.put(current_status[i])
                        print "status " + str(env_name) + " received: " + str(current_status[i])
                else:
                    print 'nothing received yet!'
                i += 1
            time.sleep(num_sec)


class ToThingSpeakThread(Thread):
    def run(self):
        global shared_queue
        global thing_speak_url
        global environments
        num_sec = 15  # num_sec seconds: minimum time to wait to let ThingSpeak work/react for a given input
        while True:
            fields = ''
            i = 0
            for env in environments:
                value = shared_queue.get()
                # prepare as many fields as the number of environments
                fields += "&field" + str(i+1) + "=" + str(value)
                i += 1
            # updates multiple fields at once
            response = urllib2.urlopen(thing_speak_url + fields)
            print thing_speak_url + fields
            print response.read()  # 0 => writing failed, > 0 writing successful
            print '==================================='
            time.sleep(num_sec)

get_host_name()
get_api_key()
initialize_environments()

ToBufferThread().start()
ToThingSpeakThread().start()