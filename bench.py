import os
from posixpath import splitdrive
from subprocess import PIPE, Popen
import math

from numpy import alltrue, true_divide

num_thread = ['16', '32', '64']
omp_places = ['threads', 'cores', 'sockets']
proc_bindings = ['master', 'clode', 'spread']
#input file generated using generate_hg.sh in /home/hpc2/Hpc-LabelPropagation-Project/LabelPropagation-C++/tools
input_file = '/path/to/hg_5000_300_2500.hgr'
output_perf = 'output_perf.txt'
#program = './benchmark_opt_3' when testing the original code
#program = './benchmark_opt_5' when testing w/o modifying the pragmas
#program = './benchmark_opt_6' when testing with modified pragmas w/o perf
program = ['perf', 'stat', '-e', 'node-loads', '-e', 'node-stores', '-e', 'node-loads-misses', '-e', 'node-stores-misses', '-o', output_perf, '--append', './benchmark_opt_6', input_file]
output_file_result = "5000_300_2500_results"
res = [0, 0, 0, 0]
limit = 10
all_tests = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
variance = 0
mediana = 0
useful = ['node-loads', 'node-stores', 'node-loads-misses', 'node-stores-misses', 'user\n', 'sys\n']
perf_ten_test = {}
variance_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0, 'time_sys': 0, 'time_user': 0}
media_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0, 'time_sys': 0, 'time_user': 0}
p_media_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0}
mediana_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0, 'time_sys': 0, 'time_user': 0}


#Used to write on the final file the information obtained with perf
def write_result():
    f.write('\n \n')
    for x in media_perf:
        f.write('MEDIA '+x+ ': '+ str(media_perf[x])+'\n')
        f.write('VARIANZA '+x+ ': '+ str(variance_perf[x])+'\n')
        f.write('MEDIANA '+x+ ': '+ str(mediana_perf[x])+'\n')
    for w in p_media_perf:
        f.write('MEDIA PERF '+w+ ': '+ str(p_media_perf[w])+'\n')

#Used to obtain the output of perf from a temp file
def calculatePerf():
    lista_buona = [] 
    node_loads = []
    p_node_loads = []
    node_stores = []
    p_node_stores = []
    node_load_misses = []
    p_node_load_misses = []
    node_store_misses = []
    p_node_store_misses = []
    time_sys = []
    time_user = []
    f1 = open(output_perf, "r")
    file_readed = f1.readlines()
    file_readed.remove(file_readed[0])
    file_readed.remove(file_readed[1])
    for line in file_readed:
        if len(line) > 1:
            l = line.split(' ')
            splittedLin = [value for value in l if value != '']
            for word in useful:
                if word in splittedLin:
                    lista_buona.append(splittedLin)  
    i = 0
    count = 0
    while i < len(lista_buona):
        lista_temp = []
        for i in range(i, i+6):
            lista_temp.append(lista_buona[i])
        perf_ten_test[count] = lista_temp
        i += 1
        count += 1
    for k in perf_ten_test:
        node_loads.append(perf_ten_test[k][0][0])
        p_node_loads.append(perf_ten_test[k][0][2])
        node_stores.append(perf_ten_test[k][1][0])
        p_node_stores.append(perf_ten_test[k][1][2])
        node_load_misses.append(perf_ten_test[k][2][0])
        p_node_load_misses.append(perf_ten_test[k][2][2]) 
        node_store_misses.append(perf_ten_test[k][3][0])
        p_node_store_misses.append(perf_ten_test[k][3][2])
        time_sys.append(perf_ten_test[k][5][0])
        time_user.append(perf_ten_test[k][4][0])
    for j in range(limit):
        media_perf['node_loads'] += float(node_loads[j].replace(',', '.'))
        media_perf['node_stores'] += float(node_stores[j].replace(',', '.'))
        media_perf['node_loads_misses'] += float(node_load_misses[j].replace(',', '.'))
        media_perf['node_stores_misses'] += float(node_store_misses[j].replace(',', '.'))
        media_perf['time_sys'] += float(time_sys[j])
        media_perf['time_user'] += float(time_user[j])
        p_media_perf['node_loads'] += float(p_node_loads[j].split('%')[0].split('(')[1])
        p_media_perf['node_stores'] += float(p_node_stores[j].split('%')[0].split('(')[1])
        p_media_perf['node_loads_misses'] += float(p_node_load_misses[j].split('%')[0].split('(')[1])
        p_media_perf['node_stores_misses'] += float(p_node_store_misses[j].split('%')[0].split('(')[1])
    for l in media_perf:
        media_perf[l] /= limit
    '''media_perf['node_loads'] /= limit
    media_perf['node_stores'] /= limit 
    media_perf['node_loads_misses'] /= limit
    media_perf['node_stores_misses'] /= limit
    media_perf['time_sys'] /= limit
    media_perf['time_user'] /= limit'''
    for l in p_media_perf:
        p_media_perf[l] /= limit
    '''p_media_perf['node_loads'] /= limit
    p_media_perf['node_stores'] /= limit 
    p_media_perf['node_loads_misses'] /= limit
    p_media_perf['node_stores_misses'] /= limit'''
    for j in range(limit):
        tmp = float(node_loads[j][0]) - media_perf['node_loads']
        variance_perf['node_loads'] += math.pow(tmp, 2)
        tmp = float(node_stores[j][0]) - media_perf['node_stores']
        variance_perf['node_stores'] += math.pow(tmp, 2)
        tmp = float(node_load_misses[j][0]) - media_perf['node_loads_misses']
        variance_perf['node_loads_misses'] += math.pow(tmp, 2)
        tmp = float(node_store_misses[j][0]) - media_perf['node_stores_misses']
        variance_perf['node_stores_misses'] += math.pow(tmp, 2)
        tmp = float(time_sys[j]) - media_perf['time_sys']
        variance_perf['time_sys'] += math.pow(tmp, 2)
        tmp = float(time_user[j]) - media_perf['time_user']
        variance_perf['time_user'] += math.pow(tmp, 2)  
    for l in variance_perf:
          variance_perf[l] = (variance_perf[l]/limit)*100
    '''variance_perf['node_loads'] = (variance_perf['node_loads']/limit)*100
    variance_perf['node_stores'] = (variance_perf['node_stores']/limit)*100
    variance_perf['node_loads_misses'] = (variance_perf['node_loads_misses']/limit)*100
    variance_perf['node_store_misses'] = (variance_perf['node_stores_misses']/limit)*100
    variance_perf['time_sys'] = (variance_perf['time_sys']/limit)*100
    variance_perf['time_user'] = (variance_perf['time_user']/limit)*100'''
    node_loads.sort()
    node_stores.sort()
    node_load_misses.sort()
    node_store_misses.sort()
    time_sys.sort()
    time_user.sort()
    
    mediana_perf['node_loads'] = (float(node_loads[4][0]) + float(node_loads[5][0]))/2
    mediana_perf['node_stores'] = (float(node_stores[4][0]) + float(node_stores[5][0]))/2
    mediana_perf['node_loads_stores'] = (float(node_load_misses[4][0]) + float(node_load_misses[5][0]))/2
    mediana_perf['node_stores_misses'] = (float(node_store_misses[4][0]) + float(node_store_misses[5][0]))/2
    mediana_perf['time_sys'] = (float(time_sys[4]) + float(time_sys[5]))/2
    mediana_perf['time_user'] = (float(time_user[4]) + float(time_user[5]))/2
    
#Check variance
def checkVariance(var):
    if var < 5:
        return False
    return True

#Run all the tests needed
def runTest(res, all_tests):
    for x in range(limit):
                print(str(x) + ' out of ' + str(limit))
                proc = Popen(program, stdout=PIPE)
                proc.wait()
                output = proc.communicate()[0]
                outputDecoded = output.decode('utf-8')
                splittedString = outputDecoded.split('\n')
                res[0] += float(splittedString[1].split(':')[1])
                res[1] += float(splittedString[2].split(':')[1])
                res[2] += float(splittedString[3].split(':')[1])
                res[3] += float(splittedString[4].split(':')[1])
                all_tests[x] = float(splittedString[4].split(':')[1])


f = open(output_file_result, 'a')

for th in num_thread:
    os.environ['OMP_NUM_THREADS'] = th
    for elem in omp_places:
        os.environ['OMP_PLACES'] = elem
        for bind in proc_bindings:
            os.environ ['OMP_PROC_BIND'] = bind
            print('VARIANILE THREADS = ' + os.environ['OMP_NUM_THREADS'] + ' VARIABILE BIND = ' + os.environ['OMP_PLACES'] + ' VARIABILE PROC_BIND = '+  os.environ['OMP_PROC_BIND'])
            runTest(res, all_tests)
            res[0] = res[0]/limit
            res[1] = res[1]/limit
            res[2] = res[2]/limit
            res[3] = res[3]/limit
            for j in range(limit):
                tmp = all_tests[j] - res[3]
                variance += math.pow(tmp, 2)
            variance = (variance/limit)*100
            #Repeat the tests for this configuration if variance is too high
            while checkVariance(variance):
                runTest(res, all_tests)
                res[0] = res[0]/limit
                res[1] = res[1]/limit
                res[2] = res[2]/limit
                res[3] = res[3]/limit
                for j in range(limit):
                    tmp = all_tests[j] - res[3]
                variance += math.pow(tmp, 2)
                variance = (variance/limit)*100
            f.write('VARIANILE THREADS = ' + th + ' VARIABILE PLACES = ' + elem + ' VARIABILE PROC_BIND = '+  bind +'\n')
            f.write('Medie:')
            f.write(str(res))
            f.write("\n")
            all_tests.sort()
            var1 = all_tests[4]
            var2 = all_tests[5]
            mediana = (all_tests[4] + all_tests[5])/2
            f.write('Mediana:')
            f.write(str(mediana))
            f.write("\n")
            f.write('Varianza: ')
            f.write(str(variance))
            calculatePerf()
            write_result()
            f.write("\n\n")
            res = [0, 0, 0, 0]
            variance = 0
            mediana = 0
            perf_ten_test = {}
            variance_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0, 'time_sys': 0, 'time_user': 0}
            media_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0, 'time_sys': 0, 'time_user': 0}
            p_media_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0}
            mediana_perf = { "node_loads": 0, "node_stores": 0, 'node_loads_misses': 0, 'node_stores_misses': 0, 'time_sys': 0, 'time_user': 0}
            os.remove(output_perf)
f.close()
    
        