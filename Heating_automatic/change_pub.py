import json
import urllib2
import time
import os


base_url = "https://dweet.io/dweet/for/change_request_"
last_update = "default"
fail = 0

environments = []
fail = []
last_update = []
flag = []

hostName = ""


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
    global fail
    global last_update
    global flag
    for env_file in os.listdir(os.getcwd()+'/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))
        fail.append(0)
        last_update.append("default")
        flag.append(0)  # just to avoid publishing the Ith time (old values) again
    return


# automatically generates and publishes a 'change' status for the switch on the topic 'web_switch/change_request_' for
# each environment
def change_switch_auto(env):
        i = 0  # just to avoid to publish the I time (old values)
        response = urllib2.urlopen(base_url + env + "?status=change")
        output = response.read()
        js = json.loads(output)
        if js["this"] == "succeeded":
            t = js["with"]["created"]
            if str(t) != str(last_update[i]):
                last_update[i] = t
                ts = int(time.time())
                print "Switch status change request sent to " + env + " heater system or broker!"
        else:
            t = js["with"]["created"]
            if str(t) != str(last_update[i]):
                print 'failed to send a switch change request!'
        i += 1

initialize_environments()

# publishes (every num_sec seconds) a 'change' string as a value on the topic: 'web_switch/change_request_envName' where
# envName is the name of each available environment
while True:
    num_sec = 4  # seconds to wait to change the switch state again
    for env_name in environments:
        change_switch_auto(env_name)  # auto switch status changer
        #change = raw_input("Press any key to change the switch state manually for " + env_name + " ")  # manual switch changer
        #print "switch change status request sent to " + env + " heater system or broker!"
    print "\nAfter " + str(num_sec) + " seconds, switch status change request will be sent again"
    time.sleep(num_sec)  # the change_pub or the user (if he wishes) publishes the 'change' status of the switch manually
        # or automatically for each environment every num_sec seconds
