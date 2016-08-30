import  os
import random

environments = []

def initialize_environments():
    global environments
    #initialize default values and get environment names
    for env_file in os.listdir(os.getcwd()+'/envs'):
        if env_file.endswith(".txt"):
            environments.append(env_file.strip('.txt'))


# check if a file 'file_name' exists in a directory 'path'
def find(file_name, path):
    for root, dirs, files in os.walk(path):
        if file_name in files:
            return 'true'
        else:
            return 'false'


initialize_environments()
for env in environments:
    #if a temperature file doesn't exist for an environment, create and initialize it to 0
    if find('indoor_temp_' + env+'.txt', os.getcwd() + '/indoor_temperatures/') == 'false':
        file_name = os.getcwd() + '/indoor_temperatures/' + 'indoor_temp_' + env + '.txt'
        fp = open(file_name, 'w')
        fp.write('{\n')
        for i in xrange(22):
            fp.write('\t"' + str(i) + ':00" ' + str(random.randint(5, 40)) + ',\n')
        fp.write('\t"' + str(i) + ':00" ' + str(random.randint(5, 40)) + '\n}')
        fp.close()
        print 'A default temperature file named: ' + 'indoor_temp_' + env + '.txt' + ' is created'