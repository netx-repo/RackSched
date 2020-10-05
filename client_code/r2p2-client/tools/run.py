#!/usr/bin/python

import sys, os, time, subprocess, argparse, random
#import paramiko

#********************************************************************
# exe cmd
#********************************************************************
def exe_cmd(cmd):
    subprocess.call(cmd, shell=True)

#********************************************************************
# parameters
#********************************************************************
class Parameters(object):
    def __init__(self):
        self.project_dir = "/home/bfn/netcache"
        #self.project_dir = "/media/sf_in-network-service/kvsrc/netcache"
        self.folders = ["client", "backend", "simple_socket", \
            "simulator", "trace"]

def get_latency_tputs(mode):
    if mode == "c": # cache
        tputs = [i*1000 for i in range(11)]
    else: # backend
        tputs = [500, 2500, 5000, 7500, 10000] \
            + [int(i*50) for i in range(9)] \
            + [int(i*100) for i in range(9)]
        tputs = [500, 2500, 5000, 7500, 10000] + [i*1000 for i in range(11)]
        tputs.sort()
        tputs = list(set(tputs))
        tputs.sort()

    tputs.remove(0)
    return tputs

#********************************************************************
# process results
#********************************************************************
def get_p99(bins):
    total = sum(bins)
    if total == 0:
        return -1
    cur_total = 0
    for idx, bin in enumerate(bins):
        cur_total += bin
        #print "%d-%d us: %.4f" % \
        #    (idx*10, (idx+1)*10, cur_total / float(total))
        print "%.4f" % (cur_total / float(total)),
        if idx == 10:
            print ""
            return 0
        #if cur_total / float(total) > 0.99:
        #    return idx
    return -1

def get_loads(file_name):
    node_loads = []
    with open(file_name, "r") as f:
        line = f.readline()
        for i in range(128):
            line = f.readline()
            node_loads.append(line.strip().split())
        line = f.readline()
        node_loads.append(line.strip().split())
    return node_loads

def get_result_latency(mode):
    begin = 5
    end = 10
    tputs = get_latency_tputs(mode)
    res_latency = {}
    for tput in tputs:
        file_name = "res_latency_tput%d_%s" % (tput, mode)
        if not os.path.isfile(file_name):
            continue
        cur_count = 0
        average_latency = []
        with open(file_name, "r") as f:
            line = f.readline()
            while line != "":
                if line.strip() == "throughput":
                    if cur_count >= begin and cur_count < end:
                        # process throughput
                        for i in range(3):
                            line = f.readline()
                        line = f.readline()
                        items = []
                        # process cache latency
                        line = f.readline()
                        if mode == "c":
                            items = line.strip().split()
                        # process backend latency
                        line = f.readline()
                        if mode == "b":
                            items = line.strip().split()
                        average_latency.append(float(items[4]))
                    cur_count += 1
                line = f.readline()
        res_latency[tput] = sum(average_latency) / len(average_latency)
    return res_latency

def process_result_latency():
    res_latency_c = get_result_latency("c")
    res_latency_b = get_result_latency("b")
    #print node_loads, res_latency_c, res_latency_b

    # process netcache
    res_cache = []
    res_backend = []
    res_total = []
    node_loads = get_loads("load_zipf_99_cache_10000")
    for i in [500, 2500, 5000, 7500, 10000]:
        cache_latency = 0
        backend_latency = 0
        total_latency = 0
        for j in range(128):
            cache_latency += float(node_loads[j][1]) * 7.0
            backend_latency += float(node_loads[j][2]) * res_latency_b[i]
            total_latency += float(node_loads[j][1]) * 7.0 \
                + float(node_loads[j][2]) * res_latency_b[i]
        cache_latency /= float(node_loads[128][1])
        backend_latency /= float(node_loads[128][3])
        total_latency /= (float(node_loads[128][1]) + float(node_loads[128][3]))
        
        res_cache.append(cache_latency)
        res_backend.append(backend_latency)
        res_total.append(total_latency)
    print res_cache, res_backend, res_total

    # process nocache
    node_loads = get_loads("load_zipf_99_cache_0")
    for i in [5000, 10000]:
        backend_latency = 0
        for j in range(128):
            tput = int(float(node_loads[j][2]) / 100 * i)
            #print tput
            if tput <= 1000:
                tput = 1000
            else:
                tput = (tput + 500) / 1000 * 1000
            #print tput
#            if tput <= 800:
#                tput = tput / 100 * 100
#            elif tput > 800 and tput < 2500:
#                tput = 800
#            else:
#                tput = tput / 2500 * 2500
            backend_latency += float(node_loads[j][2]) * res_latency_b[tput]
        backend_latency /= float(node_loads[128][3])
        print backend_latency

def process_result_log(file_name):
    begin = 0
    end = 20
    cur_count = 0
    with open(file_name, "r") as f:
        line = f.readline()
        while line != "":
            if line.strip() == "throughput":
                if cur_count >= begin and cur_count < end:
                    
                    # process throughput
                    for i in range(3):
                        line = f.readline()
                    line = f.readline()

                    # process cache latency
                    line = f.readline()
                    #print line
                    bins = []
                    for i in range(100):
                        line = f.readline()
                        items = line.strip().split()
                        bins.append(int(items[2]))
                    #idx = get_p99(bins)
                    #print "cache p99:\t%d us" % (idx*10)
                    
                    # process backend latency
                    line = f.readline()
                    print line.strip()
                    bins = []
                    for i in range(100):
                        line = f.readline()
                        items = line.strip().split()
                        bins.append(int(items[2]))
                    #print bins
                    idx = get_p99(bins)
                    #print "backend p99:\t%d us" % (idx*10)
                    #break
                cur_count += 1
            line = f.readline()

def process_tput_log(file_name):
    begin = 3
    end = 7
    cur_count = 0
    tputs = []
    with open(file_name, "r") as f:
        line = f.readline()
        while line != "":
            if line.strip().split()[0] == "total":
                if cur_count >= begin and cur_count < end:
                    items = line.strip().split()
                    tputs.append(float(items[6]))
                cur_count += 1
            line = f.readline()
    return sum(tputs) / len(tputs)

def process_result_write():
    with open("log", "r") as f:
        line = f.readline()
        while line != "":
            if line.strip().split()[0] == "cluster":
                effective_tputs = []
                total_tputs = []
                for i in range(128):
                    line = f.readline()
                    if line == "":
                        return
                    items = line.strip().split()
                    effective_tputs.append(float(items[1]))
                    total_tputs.append(float(items[2]))
                max_total_tput = max(total_tputs)
                if max_total_tput == 0:
                    print 0
                else:
                    #for i in range(128):
                    #    effective_tputs[i] = effective_tputs[i] \
                    #        / max_total_tput * 10.0
                    print sum(effective_tputs),\
                        sum(effective_tputs) / max_total_tput /100
            line = f.readline()

#********************************************************************
# experiment
#********************************************************************


def clear(parameters):
    for i in parameters.folders:
        cmd = "cd %s/%s && rm -rf build lib" \
            % (parameters.project_dir, i)
        exe_cmd(cmd)

def clean(parameters):
    for i in parameters.folders:
        cmd = "cd %s/%s && make clean" \
            % (parameters.project_dir, i)
        exe_cmd(cmd)

def compile(parameters):
    for i in parameters.folders:
        cmd = "cd %s/%s && make clean && make" \
            % (parameters.project_dir, i)
        exe_cmd(cmd)

def generate_tput_cache(parameters):
    for cache_size in [1, 10, 100]:
        cmd = "cd %s/result " \
            "&& ../simulator/build/simulator -m 0 -z 99 -c %d " \
            "> load_zipf_99_cache_%d" \
            % (parameters.project_dir, cache_size, cache_size)
        print cmd
        exe_cmd(cmd)

def init(parameters):
    print "begin initialization"
    exe_cmd("cd %s && rm -rf result && mkdir result" % parameters.project_dir)

    print "generate key"
    cmd = "cd %s/result " \
            "&& ../simulator/build/simulator -m 2 " \
            "> hot_key_hash_100K" \
            % parameters.project_dir
    exe_cmd(cmd)

    print "generate trace"
    for zipf in [90, 95, 99]:
        cmd = "cd %s && ./trace/build/trace -z %d " \
            "> result/trace_zipf_%d_key_1M_len_10M" \
            % (parameters.project_dir, zipf, zipf)
        exe_cmd(cmd)

    print "generate load"
    for zipf in [90, 95, 99]:
        for cache_size in [0, 1000, 10000]:
            cmd = "cd %s/result " \
                "&& ../simulator/build/simulator -m 0 -z %d -c %d " \
                "> load_zipf_%d_cache_%d" \
                % (parameters.project_dir, zipf, cache_size, zipf, cache_size)
            #print cmd
            exe_cmd(cmd)

    print "finish initialization"

def stop(parameters, backend = None):
    cmd = "ps -ef | grep client | grep -v grep | awk '{print $2}' " \
        "| xargs sudo kill -9"
    exe_cmd(cmd)

    flag = True
    if backend is None:
        flag = False
        backend = paramiko.SSHClient()
        backend.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        backend.connect("10.201.124.42", username = "bfn", password = "Ronald12")
    cmd = "ps -ef | grep backend | grep -v grep | awk '{print $2}' " \
        "| xargs sudo kill -9"
    backend.exec_command(cmd)
    if not flag:
        backend.close()

def run_expr_write_uniform(parameters):
    # run experiment
    for w in [0, 20, 40, 60, 80, 100]:
        cmd = "cd %s/result " \
                "&& ../simulator/build/simulator -m 0 -z 99 -c 10000 -w %d " \
                "> load_zipf_99_cache_10000_w_%d_uniform" \
                % (parameters.project_dir, w, w)
        print cmd
        exe_cmd(cmd)

    # process log
    tputs = []
    for w in [0, 20, 40, 60, 80, 100]:
        file_name = "load_zipf_99_cache_10000_w_%d_uniform" % w
        with open(file_name, "r") as f:
            items = f.readlines()[-1].strip().split()
            tput = float(items[-1]) / 10000
            if tput > 2:
                tput = 2
            tputs.append(tput)
    print tputs

def run_expr_write_skew_help(parameters, node_loads, zipf, node_num, w):
    print "run experiment write raio: %d" % w

    backend = paramiko.SSHClient()
    backend.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    backend.connect("10.201.124.42", username = "bfn", password = "Ronald12")
    stop(parameters, backend)
    for i in range(node_num):
        kv_trace_p = int(float(node_loads[i][3]) + 0.5)
        
        # start client and backend
        cmd = "cd %s/result && sudo ../client/build/client -l 0,2 " \
            "-- -z %d -n %d -k %d -m 1000 -w %d -s 1 " \
            "> log_client_zipf_%d_cache_10000_node_%d_w_%d_skew 2>&1 &" \
            % (parameters.project_dir, zipf, i, kv_trace_p, w, zipf, i, w)
        print cmd
        exe_cmd(cmd)
        cmd = "cd %s/result && sudo ../backend/build/backend -l 0 -- -n %d " \
                "> log_backend_zipf_%d_cache_10000_node_%d_w_%d_skew 2>&1 &" \
            % (parameters.project_dir, i, zipf, i, w)
        print cmd
        backend.exec_command(cmd)
        
        time.sleep(30)
        stop(parameters)
        time.sleep(1)
    backend.close()

def run_expr_write_skew(parameters):
    node_num = 128
    zipf = 90
    write_ratios = [0, 20, 40, 60, 80, 100]

    # read load file
    file_name = "%s/result/load_zipf_%d_cache_10000" \
        % (parameters.project_dir, zipf)
    #file_name = "load_zipf_%d_cache_10000" % zipf
    node_loads = get_loads(file_name)

    # process each write ratio
    for w in write_ratios:
        #run_expr_write_skew_help(parameters, node_loads, zipf, node_num, w)
        pass

    # process log
    # get traffic ratio for each node
    file_name = "%s/result/load_zipf_%d_cache_0" \
        % (parameters.project_dir, zipf)
    #file_name = "load_zipf_99_cache_0"
    traffic_ratio = get_loads(file_name)
    traffic_ratio = [float(i[2]) for i in traffic_ratio[0:-1]]
    #print traffic_ratio[0:node_num]
    # compute tput
    result = [[], [], []]
    for w in write_ratios:
        client_tputs = []
        backend_tputs = []
        for i in range(node_num):
            file_name = "log_client_zipf_%d_cache_10000_node_%d_w_%d_skew" \
                % (zipf, i, w)
            client_tput = process_tput_log(file_name)
            client_tputs.append(client_tput)

            file_name = "log_backend_zipf_%d_cache_10000_node_%d_w_%d_skew" \
                % (zipf, i, w)
            #cmd = "scp bfn@10.201.124.42:~/netcache/result/%s ./" % file_name
            #exe_cmd(cmd)
            backend_tput = process_tput_log(file_name)
            backend_tputs.append(backend_tput)
        
        #print ""
        #print client_tputs
        #print backend_tputs
        #print ""

        # normalize according to traffic ratio
        for i in range(node_num):
            client_tputs[i] = client_tputs[i] * traffic_ratio[i] / 100
            backend_tputs[i] = backend_tputs[i] * traffic_ratio[i] / 100
        #print client_tputs
        #print backend_tputs
        #print ""

        # normalize to the bottleneck backend
        normalizer = max(backend_tputs)
        client_tputs = [i/normalizer*10 for i in client_tputs]
        backend_tputs = [i/normalizer*10 for i in backend_tputs]
        #print client_tputs
        #print backend_tputs
        result[0].append(w)
        result[1].append(sum(client_tputs))
        result[2].append(sum(backend_tputs))
    print result

def run_expr_latency(parameters, mode):
    tputs = get_latency_tputs(mode)

    backend = paramiko.SSHClient()
    backend.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    backend.connect("10.201.124.42", username = "bfn", password = "Ronald12")
    stop(parameters, backend)
    for tput in tputs:
        if mode == "c":
            cmd = "cd %s/result && sudo ../client/build/client -l 0,2 " \
                "-- -c 1 -m %d " \
                "> res_latency_tput%d_c 2>&1 &" \
                % (parameters.project_dir, tput, tput)
            print cmd
            exe_cmd(cmd)
        else:

            cmd = "cd %s/result && sudo ../client/build/client -l 0,2 " \
                "-- -z 99 -n 7 -k 100 -m %d " \
                "> res_latency_tput%d_%s 2>&1 &" \
                % (parameters.project_dir, tput, tput, mode)
            print cmd
            exe_cmd(cmd)
            cmd = "cd %s/result && sudo ../backend/build/backend -l 0 " \
                "-- -n 7 " \
                "> res_latency_tput%d_%s 2>&1 &" \
                % (parameters.project_dir, tput, mode)
            print cmd
            backend.exec_command(cmd)
        time.sleep(20)
        stop(parameters, backend)
        time.sleep(1)
    backend.close()

def run_expr_tput(parameters, zipf_alpha, cache_size):
    print "run experiment zipf: %d cache size: %d" % (zipf_alpha, cache_size)

    node_num = 128
    node_loads = []

    # read load file
    file_name = "%s/result/load_zipf_%d_cache_%d" \
        % (parameters.project_dir, zipf_alpha, cache_size)
    node_loads = get_loads(file_name)
    print node_loads[node_num]

    total_sw = 0
    total_server = 0
    for i in range(node_num):
        total_pct = float(node_loads[i][3]) + float(node_loads[i][4])
        total_sw += float(node_loads[i][1])
        total_server += float(node_loads[i][2])
    print total_sw, total_server

    # iterate over machines
    backend = paramiko.SSHClient()
    backend.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    backend.connect("10.201.124.42", username = "bfn", password = "Ronald12")
    for i in range(node_num):
        kv_trace_p = int(float(node_loads[i][3]) + 0.5)
        pkts_send_limit_ms = int(float(node_loads[i][3]) / 100 * 10 * 1000)
        
        # start client and backend
        cmd = "cd %s/result && sudo ../client/build/client -l 0,2 " \
            "-- -z %d -n %d -k %d -m %d " \
            "> log_client_zipf_%d_cache_%d_node_%d 2>&1 &" \
            % (parameters.project_dir, zipf_alpha,
                i, kv_trace_p, pkts_send_limit_ms,
                zipf_alpha, cache_size, i)
        print cmd
        exe_cmd(cmd)
        cmd = "cd %s/result && sudo ../backend/build/backend -l 0 -- -n %d" \
                "> log_backend_zipf_%d_cache_%d_node_%d 2>&1 &" \
            % (parameters.project_dir, i, zipf_alpha, cache_size, i)
        print cmd
        backend.exec_command(cmd)
        
        time.sleep(20)
        stop(parameters)
        time.sleep(1)
    backend.close()

    # get statistics
    pass

def run_old(parameters):
    tofino = paramiko.SSHClient()
    tofino.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    tofino.connect("10.201.124.31", username = "admin12", password = "bfn123")
    for cache_size in [0, 10000]:
        cmd = "echo '%d' | ./tools/run_p4_tests.sh -p netcache" % cache_size
        print cmd
        #tofino.exec_command(cmd)
        for zipf_alpha in [0, 90, 99]:
            run_single_experiment(parameters, zipf_alpha, cache_size)
    tofino.close()

def run(parameters):
    pass

def bind(parameters, port):
    other_port = ""
    if port == "tofino":
        port = "05:00.0"
        other_port = "05:00.1"
    else:
        port = "05:00.1"
        other_port = "05:00.0"
    cmd = "sudo ${RTE_SDK}/tools/dpdk-devbind.py -u %s" % other_port
    print cmd
    exe_cmd(cmd)
    cmd = "sudo ${RTE_SDK}/tools/dpdk-devbind.py -b igb_uio %s" % port
    print cmd
    exe_cmd(cmd)

#********************************************************************
# main
#********************************************************************
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NetKV demo")
    parser.add_argument("-option",
        help=("choose action: run"),
        type=str, action="store", required=True)
    args = parser.parse_args()

    parameters = Parameters()
    if args.option == "run":
        run(parameters)
    elif args.option == "stop":
        stop(parameters)
    elif args.option == "init":
        init(parameters)
    elif args.option == "compile":
        compile(parameters)
    elif args.option == "clean":
        clean(parameters)
    elif args.option == "clear":
        clear(parameters)
    elif args.option == "bind-tofino":
        bind(parameters, "tofino")
    elif args.option == "bind-direct":
        bind(parameters, "direct")
    elif args.option == "run-latency-c":
        run_expr_latency(parameters, "c")
    elif args.option == "run-latency-b":
        run_expr_latency(parameters, "b")
    elif args.option == "run-write-uniform":
        run_expr_write_uniform(parameters)
    elif args.option == "run-write-skew":
        run_expr_write_skew(parameters)
    elif args.option == "res-latency":
        process_result_latency()
    elif args.option == "gen-tput-cache":
        generate_tput_cache(parameters)
    elif args.option == "process-res-write":
        process_result_write()
    else:
        #process_result_log(args.option)
        print "Not supported option"
