import urllib2
import json
import time
import os

hostName = ""
environments = []
current_status = []
last_update1 = []
last_update2 = []
js_in1 = []
js_in2 = []
js_out = []


url1 = "https://dweet.io/get/latest/dweet/for/change_request_"
url2 = "https://dweet.io/get/latest/dweet/for/next_status_"
url3 = "https://dweet.io/dweet/for/current_status_"


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
    global current_status
    for env_file in os.listdir(os.getcwd()+'/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))
        current_status.append('0')
        last_update1.append("default")
        last_update2.append("default")
        js_in1.append("default")
        js_in2.append("default")
        js_out.append("default")
    print 'connected to: ' + hostName
    return


def open_url(url):
    response = urllib2.urlopen(url)
    output = response.read()
    js = json.loads(output)
    return js, output


def on_message():
    global environments
    global current_status
    global last_update1
    global last_update2
    global js_in1
    global js_in2
    global js_out
    global url1
    global url2
    global url3
    first_time = True
    t1 = "default"
    t2 = "default"
    while True:
        num_sec = 2  # seconds to wait before checking the change request again
        i = 0  # just to avoid to publish the I time (old values)
        for env_name in environments:
            js_in1[i], output = open_url(url1 + env_name)
            js_in2[i], output1 = open_url(url2 + env_name)
            print output
            print output1
            if js_in1[i]["this"] == "succeeded":
                t1 = js_in1[i]["with"][0]["created"]
            if not first_time:
                if js_in2[i]["this"] == "succeeded":
                    t2 = js_in2[i]["with"][0]["created"]
            if str(t1) != str(last_update1[i]) or str(t2) != str(last_update2[i]):
                last_update1[i] = t1
                last_update2[i] = t2
                if current_status[i] == '0':
                    current_status[i] = "1"
                else:
                    current_status[i] = "0"
                js_out[i], output = open_url(url3 + env_name + "?status=" + current_status[i])   # + "source=switch")
                print output
                if js_out[i]["this"] == "succeeded":
                    print "NEXT_STATUS_SUB: current_status for " + env_name + " is changed to: " + str(current_status[i])
                if i == 2:
                    first_time = False
            else:
                print 'nothing changed yet!'
            i += 1
            time.sleep(num_sec)

gethostname()
initialize_environments()
on_message()
