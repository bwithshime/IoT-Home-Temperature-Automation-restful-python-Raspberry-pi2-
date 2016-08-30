import time
import urllib2
import datetime
import os
import random


presence_time_array = []
max_temp = 23
new_env = "new_environment"

last_presence = -1
presence_time = -1
cur_hour = 0
cur_minutes = 0
cur_seconds = 0
current_time = "00:00:00"

x1 = "23:59:59"  # default morning presence start time
y1 = "07:30:00"  # default morning presence end time
x2 = "18:30:00"  # default afternoon presence start time
y2 = "00:00:00"  # default afternoon presence end time

base_url = "https://dweet.io/dweet/for/presence_"
environments = []

flag=0
invalid_filename_chars = set('#%&{}\\<>*?/$!\'":@+|=')

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


def validate_time_format(pres_time, prompt):
    while not len(pres_time) == 8:
        print 'Invalid time format! Please enter in the format "HH:MM:SS"'
        pres_time = raw_input(prompt)
    while not len(pres_time)==8 or not pres_time[2] == ':' or not pres_time[5] == ':' or not pres_time[:2].isdigit() or not pres_time[3:5].isdigit() \
    or not pres_time[-2:].isdigit():
        print 'Invalid time value! Please enter a valid time number in the format "HH:MM:SS"'
        pres_time = raw_input(prompt)
    while not len(pres_time)==8 or not pres_time[2] == ':' or not pres_time[5] == ':' or not pres_time[:2].isdigit() or not pres_time[3:5].isdigit() \
    or not pres_time[-2:].isdigit() or int(pres_time[:2])>24 or int(pres_time[3:5])>59 or int(pres_time[-2:])>59:
        print 'Invalid time value! Please enter a valid time in the range "00:00:00 - 23:59:59"'
        pres_time = raw_input(prompt)
    return pres_time


def get_user_presence_time():  # gets new presence time from user
    global x1
    global y1
    global x2
    global y2
    s1 = "morning presence start time     = "
    s2 = "morning presence end time       = "
    s3 = "afternoon presence start time   = "
    s4 = "afternoon presence end time     = "

    x1 = validate_time_format(raw_input(s1), s1)
    y1 = validate_time_format(raw_input(s2), s2)
    x2 = validate_time_format(raw_input(s3), s3)
    y2 = validate_time_format(raw_input(s4), s4)
    return


def read_user_presence_time(file_path):  # reads presence time from file
    global x1
    global y1
    global x2
    global y2
    lines = []
    global max_temp
    with open(file_path, "r") as f:
        first_line = f.readline()  # first line of all environments file is the Max_temp value
        max_temp = first_line.rstrip('\n')
        for line in f:
            line = line.rstrip('\r\n')#.rstrip('\r\n') removes the newline and carriage return characters if any
            for l in line.split(','):
                lines.append(l)
        print 'Max_temp: ' + max_temp + '\npresence_time: '
        print lines
        f.close()
        x1 = lines[0]  # morning presence start time
        y1 = lines[1]  # morning presence end time
        x2 = lines[2]  # afternoon presence start time
        y2 = lines[3]  # afternoon presence end time
        print 'x1: '+x1+' \n y1:' + y1 + '\n x2:' + x2 + '\ny2:'+y2
    return


def create_temperature_files():
    global environments
    j = 1

    # delete all temperature files(that have no corresponding environment files), if any from ../indoor_temperatures directory
    for root, dirs, files in os.walk(os.getcwd() + '/indoor_temperatures'):
        for indoor_temperatures_file in files:
            file_name = indoor_temperatures_file.strip('indoor_temp_')
            if file_name.strip('.txt') not in environments:
                os.unlink(os.path.join(root, indoor_temperatures_file))

    for env in environments:
        print base_url + env + '?indoor_temp_' + env + '='
        j += 1

    for env in environments:
        # if a JSON formatted temperature file doesn't exist for an environment, create default and initialize to
        # random values
        if find('indoor_temp_' + env+'.txt', os.getcwd() + '/indoor_temperatures/') == 'false':
            file_name = os.getcwd() + '/indoor_temperatures/' + 'indoor_temp_' + env + '.txt'
            # creates a JSON formatted temperature file for the 24 hours of the new environment
            fp = open(file_name, 'w')
            fp.write('{\n')
            for i in xrange(22):
                fp.write('\t"' + str(i) + ':00" ' + str(random.randint(5, 40)) + ',\n')
            fp.write('\t"' + str(i) + ':00" ' + str(random.randint(5, 40)) + '\n}')
            fp.close()
            print 'A default temperature file named: ' + 'indoor_temp_' + env + '.txt' + ' is created'
    return

# check if a file 'file_name' exists in a directory 'path'
def find(file_name, path):
    for root, dirs, files in os.walk(path):
        if file_name in files:
            return 'true'
        else:
            return 'false'


# prints a menu option
def show_menu():
    global environments
    i = 0
    # os.system('cls' if os.name == 'nt' else 'clear')  # to clear the screen
    print 'Which environment you regulate temperature? choose the number'
    for env in environments:
        print('' + str(i+1) + ': ' + env + '')
        i += 1
    print ('' + str(i+1) + ': ' + 'Add New Environment')
    print ('' + str(i+2) + ': ' + 'Remove Environment')
    print ('' + str(i+3) + ': ' + 'Exit application')
    opt = raw_input()
    while not(opt.isdigit()) or int(opt) > (len(environments)+3) or int(opt) < 1:
        print 'Invalid option! please choose the correct option'
        opt = raw_input()
    return opt


# delete environment presence time file and corresponding indoor_temperatures file
def remove_env_files(dir_path, env_name):
    environments.remove(env_name)
    for root, dirs, files in os.walk(dir_path):
            for f in files:
                    if f.strip('.txt') == env_name or f.strip('.txt') == 'indoor_temp_'+ env_name:
                        os.unlink(os.path.join(root, f))
    print "An environment named: '" + env_name + "' is successfully deleted!"
    return


def get_new_environment():
    new_env = raw_input('Your new environment name: ')
    while any((c in invalid_filename_chars) for c in set(new_env.lower())) or new_env == '':
        print 'Invalid special characters used for environment name!'
        print invalid_filename_chars
        print ' please enter a valid name again!'
        new_env = raw_input('Your new environment name:')
    return new_env


def environment_management():
    global x1
    global y1
    global x2
    global y2
    #global ask_new
    global max_temp
    global new_env
    global cur_seconds
    global cur_minutes
    global cur_hour
    global current_time
    global environments
    environments = []
    for env_file in os.listdir(os.getcwd() + '/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))
    option = show_menu()
    choice = int(option)  # or parseStr(option)

    while len(environments)+2 <= choice <= len(environments)+3:
        if choice == len(environments)+3:  # selects application exit option
            app_exit = raw_input('Are you sure you want to exit? (yes/no): ')
            while not (app_exit.lower()=='yes' or app_exit.lower()=='no'):
                app_exit = raw_input ('Invalid option! please say "yes" or "no": ')
            if app_exit.lower() == "yes":
                exit()  # Closes the application
        elif choice == len(environments)+2:  # selects environment delete option
            env_name = raw_input('Environment name to delete: ')
            while not env_name in environments:
                print "There is no such environment named '" + env_name + "' to be deleted! please enter again!"
                env_name = raw_input('Environment name to delete: ')
            confirm = raw_input("Are you sure you want to delete environment '" + env_name + "'? (yes/no?): ")
            while not (confirm.lower() == 'yes' or confirm.lower() == 'no'):
                confirm = raw_input('Invalid option! please say "yes" or "no": ')
            if confirm.lower() == "yes":
                remove_env_files(os.getcwd(), env_name)
        option = show_menu()
        choice = int(option)  # or parseStr(option)

    if choice == len(environments)+1:
        new_env = get_new_environment()
        while new_env in environments:
            print "An environment named: '" + new_env + "' already exists! Do you want to overwrite it?(yes/no)"
            confirm = raw_input()
            while not (confirm.lower() == 'yes' or confirm.lower() == 'no'):
                confirm = raw_input('Invalid option! please say "yes" or "no": ')
            if confirm.lower() == "no":
                new_env = get_new_environment()
            else:
                break;
        if new_env not in environments:
            environments.append(new_env)
        #fp = open(os.getcwd()+'/envs\/' + new_env, 'w')#if the environment already exists it overrides the previous presence time
        print "Please Fill the presence time for the '" + new_env + "' environment!"
        get_user_presence_time()
        confirm = raw_input('Do you want to change the Maximum Temperature for environment ' + new_env +'? yes/no\n')
        while not (confirm.lower()=='yes' or confirm.lower()=='no'):
            print 'Invalid option! please say "yes" or "no"'
            confirm = raw_input('Do you want to change the Maximum Temperature for environment ' + new_env +'? yes/no\n')
        if confirm.lower() == "yes":
            max_temp = raw_input('Max_temp: ')
            while not max_temp.isdigit():
                print 'Invalid value for maximum temperature! please enter a valid number again'
                max_temp = raw_input('Max_temp: ')
        print 'A new environment named : ' + new_env + ' is created!'
    else:
        file_name = os.getcwd()+'/envs/' + environments[(choice-1)] + '.txt'
        read_user_presence_time(file_name)  # if the environment already exists, read the previous max_temp and presence time
        option2 = raw_input('Do you want to change the Maximum Temperature for environment ' + environments[(choice-1)] + '? yes/no\n')
        while not (option2.lower()=='yes' or option2.lower()=='no'):
            print 'Invalid option! please say "yes" or "no"'
            option2 = raw_input('Do you want to change the Maximum Temperature for environment ' + environments[(choice-1)]+ '? yes/no\n')
        if option2.lower() == 'yes':
            max_temp = raw_input('Max_temp: ')
            while not max_temp.isdigit():
                print 'Invalid value for maximum temperature! please enter a valid number again'
                max_temp = raw_input('Max_temp: ')
        option3 = raw_input('Do you want to change the default presence time for environment ' + environments[(choice-1)]+ '? yes/no\n')
        while not (option3.lower()=='yes' or option3.lower()=='no'):
            print 'Invalid option! please say "yes" or "no"'
            option3 = raw_input('Do you want to change the default presence time for environment ' + environments[(choice-1)]+ '? yes/no\n')
        if option3.lower() == 'yes':
            get_user_presence_time()
    file_name = os.getcwd()+'/envs/' + environments[(choice-1)] + '.txt'
    fp = open(file_name, 'w')#if the environment already exists it preserves or changes the previous presence time
    fp.write(str(max_temp)+'\n')
    fp.write(x1 + ',' + y1 + ',' + x2 + ',' + y2+'\n')
    fp.close()
    print 'file named: ' + environments[(choice-1)] + '.txt ' +' is modified'
    create_temperature_files()
    time_format = '%H:%M:%s'
    now = datetime.datetime.now()
    cur_hour = format(now.hour, '02d')  # or str(num).rjust(2, '0')
    cur_minutes = format(now.minute, '02d')
    cur_seconds = format(now.second, '02d')
    current_time = str(cur_hour) + ':' + str(cur_minutes) + ':' + str(cur_seconds)

# week_day's and week_end's presence time values differ for different environments
# presence_time = 0 => absence_time, presence_time = 1 => presence time


def check_presence_time():
    print 'current time: ' + str(current_time)
    if (current_time >= x1) and (current_time <= y1) or (current_time >= x2) and (current_time <= y2):
        presence_time = '1'
    else:
        presence_time = '0'
    return presence_time


def presence_sensor():  # user presence sensor (simulated by the user's input)
    x = 'simulates presence sensor'
    user_presence = []
    for env in environments:
        print 'Simulate presence sensor for ' + env + ' (1=presence/0=absence):'
        presence = raw_input()
        while not(presence.isdigit()) or int(presence) > 1 or int(presence) < 0:
            print('Invalid value/characters for presence: please enter (1=presence/0=absence):')
            presence = raw_input()
        user_presence.append(str(presence))
    return user_presence


def pseudo_presence_generator():  # pseudo user presence generator for all environments
    user_presence = []
    for env in environments:
        presence = random.randint(0,1)
        user_presence.append(str(presence))
    return user_presence

environment_management()
while True:  # not stop == 'q' or stop == 'Q':  # press q, Q key to return to the menu, any key to continue.
    num_sec = 3  # seconds to wait to change the user presence again
    user_presence = []
    #user_presence = presence_sensor()  # manually simulate user presence every time
    user_presence = pseudo_presence_generator()  # simulates user presence automatically
    #user_presence = get_pdf_presence()  # pdf based presence simulator
    i = 0
    for u_pres in user_presence:
        file_name = os.getcwd() + '/envs/' + environments[i] + '.txt'
        print 'Environment Name: ' + environments[i]
        read_user_presence_time(file_name)
        presence_time = check_presence_time()
        print 'user presence: ' + str(u_pres)
        print 'presence time: ' + str(presence_time)
        if str(u_pres) == '0' and str(presence_time) == '0':
            last_presence = '0'  # to turn of the heater if on
        elif str(u_pres) == '0' and str(presence_time) == '1':
            last_presence = '1'  # to prepare the temp till 20 degree centigrade
        else:
            last_presence = '2'  # to increase the temp until max_temp degree centigrade
        ts = int(time.time())
        url_tmp = base_url + environments[i] + '?presence=' + str(last_presence)
        response = urllib2.urlopen(url_tmp)
        print url_tmp + '\n' + response.read()
        i += 1
        time.sleep(2)   # 2 seconds: time to wait for the urlopen to respond for each url_tmp
    print 'successful!'
    #flag=1
    now = datetime.datetime.now()
    cur_hour = format((int(cur_hour) + 1) % 24, '02d')
    cur_minutes = format(now.minute, '02d')
    cur_seconds = format(now.second, '02d')
    current_time = str(cur_hour) + ':' + str(cur_minutes) + ':' + str(cur_seconds)
    time.sleep(num_sec)  # the user presence simulator is executed every num_sec seconds for each environment.




