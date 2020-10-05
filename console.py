#!/usr/bin/env python3
"""
@file console.py
@brief The console
@requires Python 3.6+
"""

import sys
import time
import signal
import subprocess, pdb
from paramiko.client import SSHClient, AutoAddPolicy

from config import *


class RSCSConsole(object):
    """
    @brief The RSCS console
    """

    switch_conns = []
    server_conns = []
    client_conns = []

    # ******************************
    # Basics
    # ******************************
    def exe(self, ssh_conn, cmd, sudo=False, bg=False, read=False, verbose=False, pty=False):
        # Need root authorization
        if sudo:
            cmd = f'echo {ssh_conn["password"]} | sudo -S {cmd}'

        # Run in background
        if bg:
            cmd = f'{cmd} > /dev/null 2>&1 &'

        _, stdout, stderr = ssh_conn['connection'].exec_command(cmd, get_pty=pty)

        std_output = None
        std_error = None
        if read or verbose:
            std_output = stdout.read()
            std_error = stderr.read()
            if verbose:
                print(f'stdout: {std_output}\nstderr: {std_error}')
            stdout.flush()
            stderr.flush()

        return std_output

    # Sset up ssh connections
    def connect(self, hosts, conns):
        for host in hosts:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy)
            client.connect(hostname=host['hostname'],
                           username=host['username'],
                           password=host['password'])
            conns.append({'connection': client,
                          'password': host['password'],
                          'ip': host['ip'],
                          'hostnum': host['hostname'].strip('netx').strip('.cs.jhu.edu')})

    # ******************************
    # Install necessary packages
    # ******************************
    def install_gsl(self):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        for client_conn in self.client_conns:
            self.exe(client_conn, f'apt-get install libgsl-dev', sudo=True, bg=True)

    # Install dpdk-16.11.1 and set up correct env variables
    def install_dpdk(self):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        for client_conn in self.client_conns:
            self.exe(
                client_conn,
                f'cd {dpdk_dir}; export passwd={client_conn["password"]}; ./tools.sh install_dpdk',
                bg=True)

        # Wait for installation to complete
        time.sleep(120)

    # ******************************
    # Setup, run, and kill the machines
    # ******************************

    def reboot_servers(self):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        for server_conn in self.server_conns:
            self.exe(server_conn, f'reboot', sudo=True)

    def reboot_clients(self):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        for client_conn in self.client_conns:
            self.exe(client_conn, f'reboot', sudo=True)

    def setup_servers(self, rocks_db=False):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        serv_dir = server_dir
        if rocks_db:
            serv_dir = rocksdb_server_dir

        for server_conn in self.server_conns:
            # Install required libs
            self.exe(
                server_conn, f'apt-get install libconfig-dev libnuma-dev', sudo=True, bg=True)

            # Install required libs for rocksdb version of server
            if rocks_db:
                self.exe(
                    server_conn, f'apt-get install liblz4-dev libsnappy-dev libtool-bin', sudo=True, bg=True)

            # Fetch dependencies
            self.exe(
                server_conn,
                f'cd {serv_dir}; echo {server_conn["password"]} | sudo -S ./deps/fetch-deps.sh', bg=True)

        # Wait for pulling up dependencies
        if rocks_db:
            time.sleep(90)
        else:
            time.sleep(60)

    # Build customized dpdk for r2p2 servers
    def setup_r2p2_server(self):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        for server_conn in self.server_conns:
            self.exe(
                server_conn, f'cd {R2P2_RTE_SDK}; echo {server_conn["password"]} | sudo -S rm -rf x86_64-native-linuxapp-gcc; make install T={RTE_TARGET} DESTDIR={R2P2_RTE_SDK}',
                bg=True)
            self.exe(
                server_conn,
                f'cd {R2P2_RTE_SDK}; echo -e "export RTE_SDK={R2P2_RTE_SDK}\\nexport RTE_TARGET=x86_64-native-linuxapp-gcc" > .env')

        # Wait for building customized dpdk
        time.sleep(180)

    # Install GSL and DPDK on clients
    def setup_clients(self):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        self.install_gsl()
        self.install_dpdk()

    def setup_all(self):
        self.setup_servers()
        self.setup_r2p2_server()
        self.setup_clients()

    # Set the correct configuration (e.g., preemption_delay, host_addr) in shinjuku.conf
    def config_servers(self, rocks_db=False, r2p2=False):
        # No need to configure r2p2 servers
        if r2p2:
            return

        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        if rocks_db:
            serv_dir = rocksdb_server_dir
        else:
            serv_dir = server_dir

        for server_conn in self.server_conns:
            # Copy from the sample file to ensure integrity and consistency
            self.exe(server_conn, f'cp {serv_dir}/shinjuku.conf.sample {serv_dir}/shinjuku.conf')

            # Change the host addr in each shinjuku.conf file respectively
            self.exe(
                server_conn,
                f"sed -i '/^host_addr/ chost_addr=\"{server_conn['ip']}\"' {serv_dir}/shinjuku.conf", bg=True)

            if rocks_db:
                self.exe(
                    server_conn,
                    f"sed -i '/^preemption_delay/ cpreemption_delay=500000' {serv_dir}/shinjuku.conf", bg=True)

    # Kill the process of p4 program in the switch
    def kill_switch(self):
        if self.switch_conns == []:
            self.connect(switch, self.switch_conns)

        self.exe(self.switch_conns[0], "ps -ef | grep switchd | grep -v grep | "
                 "awk '{print $2}' | xargs kill -9")
        self.exe(self.switch_conns[0], "ps -ef | grep run_p4_test | grep -v grep | "
                 "awk '{print $2}' | xargs kill -9")
        self.exe(self.switch_conns[0], "ps -ef | grep tofino | grep -v grep | "
                 "awk '{print $2}' | xargs kill -9")
        time.sleep(1)

    def kill_server(self):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        for server_conn in self.server_conns:
            self.exe(server_conn, f'pkill shinjuku', sudo=True)
            self.exe(server_conn, f'pkill main', sudo=True)  # Kill r2p2 server

    def kill_client(self):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        for client_conn in self.client_conns:
            self.exe(client_conn, f'pkill dpdk_client --signal 2', sudo=True)

    def kill_all(self):
        self.kill_switch()
        self.kill_server()
        self.kill_client()

    # Run tp4 program, including control plane and data plane
    def run_switch(self, policy):
        if self.switch_conns == []:
            self.connect(switch, self.switch_conns)

        # Stop the currently running switch
        self.kill_switch()

        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {scheduling_cmds[policy][0]}', bg=True)
        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {scheduling_cmds[policy][1]} > {remote_switch_dir}switch_code/logs/run_ptf_test.log 2>&1 &', bg=False)

        # Wait for switch to finish setting up
        time.sleep(60)

    def build_and_run_servers(self, rocks_db=False):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        # Stop the currently running server
        self.kill_server()
        time.sleep(1)
        serv_dir = server_dir
        if rocks_db:
            serv_dir = rocksdb_server_dir

            # Special makefile for those machines
            for server_conn in self.server_conns:
                if server_conn['hostnum'] in rocksdb_modify_servers:
                    self.exe(
                        server_conn,
                        f'cd {rocksdb_server_dir}; cp ./makefiles/dbMakefile db/Makefile; cp ./makefiles/dpMakefile dp/Makefile',
                        bg=True)

        # Build the Shinjuku servers
        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f'cd {serv_dir}; echo {server_conn["password"]} | sudo -S ./setup.sh', bg=True)

        # Wait for building (the first time is long, other times very fast)
        if rocks_db:
            time.sleep(40)
        else:
            time.sleep(20)
        # time.sleep(15)

        # Start each server
        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f'cd {serv_dir}; echo {server_conn["password"]} | sudo -S ./build_and_run.sh', bg=True)

        # Wait for servers to spin up
        if rocks_db:
            time.sleep(30)
        else:
            time.sleep(15)
        # time.sleep(15)

    def build_clients(self, cli_dir=client_dir):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        # Build client
        for client_conn in self.client_conns:
            self.exe(client_conn, f'ifconfig enp5s0f0 down', sudo=True, bg=True)
            self.exe(
                client_conn,
                f'cd {cli_dir}; echo -e "export RTE_SDK={RTE_SDK}\\nexport RTE_TARGET=x86_64-native-linuxapp-gcc" > .env')
            self.exe(
                client_conn, f'cd {cli_dir}; . .env; make', bg=True)
            self.exe(
                client_conn,
                f'cd {cli_dir}; . .env; export passwd={client_conn["password"]}; ./tools/tools.sh setup_dpdk',
                read=True)

    # Compile p4 program
    def compile_switch(self, prog_name):
        if self.switch_conns == []:
            self.connect(switch, self.switch_conns)

        p4_build = switch_sde_dir + "/p4_build.sh"
        prog_path = remote_switch_dir + "switch_code/" + prog_name + ".p4"
        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {p4_build} {prog_path} > {remote_switch_dir}switch_code/logs/p4_compile.log 2>&1 &', bg=False)

    # Set up env for R2P2 worker
    def run_r2p2_server_1(self):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        # self.reboot_servers()

        # Wait for rebooting
        # time.sleep(120)

        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f'cd {R2P2_RTE_SDK}; . .env; export passwd={server_conn["password"]}; echo {server_conn["password"]} | sudo -S rmmod i40e; chmod +x ./tools/dpdk-devbind.py; ./tools/tools.sh setup_dpdk',
                read=True)
            self.exe(
                server_conn,
                f'echo {server_conn["password"]} | sudo -S bash -c "echo 8 > /sys/bus/pci/devices/0000\:05\:00.0/max_vfs"',
                read=True)
            bind_cmd = f'cd {R2P2_RTE_SDK}/tools; echo {server_conn["password"]} | sudo -S ./dpdk-devbind.py --bind=igb_uio'
            self.exe(server_conn, f'{bind_cmd} 05:02.0', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.1', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.2', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.3', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.4', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.5', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.6', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.7', read=True)

            self.exe(
                server_conn,
                f'cd {r2p2_dir}/r2p2_worker; . {R2P2_RTE_SDK}/.env; make clean; make',
                bg=True)

        # Wait for building r2p2 workers
        time.sleep(30)

        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f'cd {r2p2_dir}/r2p2_worker; echo {server_conn["password"]} | sudo -S bash -c "./build/main" > {server_log_dir}/r2p2.log 2>&1 &')

        time.sleep(5)

    def run_r2p2_server_2(self):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        for server_conn in self.server_conns:
            bind_cmd = f'cd {R2P2_RTE_SDK}/tools; echo {server_conn["password"]} | sudo -S ./dpdk-devbind.py --bind=igb_uio'
            self.exe(server_conn, f'{bind_cmd} 05:02.0', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.1', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.2', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.3', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.4', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.5', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.6', read=True)
            self.exe(server_conn, f'{bind_cmd} 05:02.7', read=True)

        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f'cd {r2p2_dir}/r2p2_worker; echo {server_conn["password"]} | sudo -S bash -c "./build/main" > {server_log_dir}/r2p2.log 2>&1 &')

        time.sleep(5)

    def run_r2p2_server(self):
        self.run_r2p2_server_1()
        self.run_r2p2_server_2()

    # ******************************
    # Reproduce the result
    # ******************************

    def print_result(self, results):
        for policy, dists_data in results.items():
            print(f'\n========== {policy} ==========')
            for dist, types in dists_data.items():
                print(f'[{dist}]')
                for data_type, data in types.items():
                    print(f'Type: {data_type}')
                    print('---------------------')
                    print('Load  |  99th Latency')
                    print('---------------------')
                    for point in data:
                        print(f'{point[0]}   {point[1].decode("utf-8").strip()}')
                    print()
            print()

    # Change queue setting for "port" distributions in "shinjuku.conf"
    def set_server_queue_to_head(self, dist, recover=False, rocks_db=False):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        # Determine server director
        serv_dir = server_dir
        if rocks_db:
            serv_dir = rocksdb_server_dir

        # Determine the new setting
        if recover:
            new_setting = 'false'
        else:
            # Determine queue length needed
            if 'port_bimodal' in dist:
                queue_len = 2
            elif 'port_trimodal' in dist:
                queue_len = 3
            else:  # Restore to default
                queue_len = 1
            new_setting = 'true' + ',true' * (queue_len - 1)

        # Change the config correspondingly
        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f"sed -i '/^queue_setting/ cqueue_setting=\[{new_setting}\]' {serv_dir}/shinjuku.conf",
                bg=True)

        # Restart the servers to reflect changes
        self.build_and_run_servers(rocks_db=rocks_db)
        print(f'\nServer queue setting updated\n')

    # Helper for fig.11: configure server 5-8 to use less cores
    # Change the number of workers in shinjuku.conf
    def reduce_server_cores(self, recover=False):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        # Determine the num of cores
        if recover:
            cores = r'\[0\,8\,1\,2\,3\,4\,5\,6\,7\]'
        else:
            cores = r'\[0\,8\,1\,2\,3\,4\]'

        # Update the num of cores in config
        for server_conn in self.server_conns[4:]:
            self.exe(server_conn, f"sed -i '/^cpu/ ccpu={cores}' {server_dir}/shinjuku.conf", bg=True)
        print(f'\nServer[5-8] num cores updated\n')

    # Helper for fig.16: let servers to track us (only for int3 distribution)
    def set_server_track_us(self, recover=False):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)

        # Determine the source files
        if recover:
            src_path = f'{server_dir}/track_us/original'
        else:
            src_path = f'{server_dir}/track_us'

        # Replace the files
        for server_conn in self.server_conns:
            self.exe(
                server_conn,
                f"cd {src_path}; cp dispatcher.c {server_dir}/dp/core/dispatcher.c; cp worker.c {server_dir}/dp/core/worker.c; cp dispatch.h {server_dir}/inc/ix/dispatch.h",
                bg=True)

        # Rebuild and restart the servers to reflect changes
        self.build_and_run_servers()
        print(f'\nServer track_us setting updated\n')

    def run_server(self, rocks_db=False, r2p2=False):
        if r2p2:
            self.run_r2p2_server()
        else:
            self.build_and_run_servers(rocks_db)

    # The general function to run a test, including run the servers, teh switch and the clients
    def run_test(self, scheduling_policies, dist_loads, hetero=False, rocks_db=False, r2p2=False, cs_cli=False, run_s=10):
        if self.client_conns == []:
            self.connect(clients, self.client_conns)

        # Set different client settings
        scale = 50
        cli_dir = client_dir
        cli_extra_arg = ''
        if rocks_db:
            cli_extra_arg = '-r 1'
        if r2p2:
            cli_dir = r2p2_client_dir
        if cs_cli:
            cli_dir = cs_client_dir
            cli_extra_arg = '-n 100 -z 0'

        # Reset the server config and run
        self.config_servers(rocks_db=rocks_db, r2p2=r2p2)
        if hetero:
            self.reduce_server_cores()
        self.run_server(rocks_db=rocks_db, r2p2=r2p2)
        print('\nServers are ready...\n')

        results = {}
        for policy in scheduling_policies:
            results[policy] = {}
            self.run_switch(policy)
            print(f'\nScheduling policy "{policy}" is ready...\n')

            # Special case: need to change server setting for policy 'int3'
            if policy == 'int3':
                self.set_server_track_us()

            for dist, loads in dist_loads.items():
                results[policy][dist] = {}
                results[policy][dist]['normal'] = []
                results[policy][dist]['short'] = []
                results[policy][dist]['long'] = []

                # Change the queue setting for "port" distributions
                is_port_dist = 'port' in dist
                if is_port_dist and not r2p2:
                    self.set_server_queue_to_head(dist, rocks_db=rocks_db)

                time.sleep(10)
                for load in loads:
                    # Only execute specified loads for the current policy
                    if load[2][0] == 'all' or policy in load[2]:
                        # Start the batch client
                        if not cs_cli:
                            self.exe(
                                self.client_conns[0],
                                f'cd {cli_dir}; echo {self.client_conns[0]["password"]} | sudo -S ./build/dpdk_client -l 0 -- -l 0 -c 11 -s 1 -d {dist} -q {load[0]} -x {scale} > {client_log_dir}/client.log 2>&1 &')

                        # Start the latency client
                        self.exe(
                            self.client_conns[1],
                            f'cd {cli_dir}; echo {self.client_conns[1]["password"]} | sudo -S ./build/dpdk_client -l 0,1 -- -l 1 -c 12 -s 1 -d {dist} -q {load[1]} -x {scale} {cli_extra_arg} > {client_log_dir}/client.log 2>&1 &')

                        # Kill clients after some time
                        time.sleep(run_s)
                        self.kill_client()

                        # Collect latency result
                        latency = self.exe(self.client_conns[1], f'cd {cli_dir}; \
                                python3 parselats.py --latency ./results/output', read=True)
                        results[policy][dist]['normal'].append((load[0] + load[1], latency))
                        if rocks_db and dist == 'db_port_bimodal':
                            short_latency = self.exe(self.client_conns[1], f'cd {cli_dir}; \
                                    python3 parselats.py --latency ./results/output.short', read=True)
                            long_latency = self.exe(self.client_conns[1], f'cd {cli_dir}; \
                                    python3 parselats.py --latency ./results/output.long', read=True)
                            results[policy][dist]['short'].append((load[0] + load[1], short_latency))
                            results[policy][dist]['long'].append((load[0] + load[1], long_latency))
                        print(results[policy])
                        print()

                # Recover the default queue setting
                if is_port_dist and not r2p2:
                    self.set_server_queue_to_head(dist, recover=True, rocks_db=rocks_db)

            # Reverse the setting change due to 'int3'
            if policy == 'int3':
                self.set_server_track_us(recover=True)

        if hetero:
            self.reduce_server_cores(recover=True)

        # Terminate the server and switch
        self.kill_server()
        self.kill_switch()

        # Print result
        self.print_result(results)

    # Synthetic workloads with homogeneous servers
    def fig_10(self):
        scheduling_policies = ['rscs', 'random']

        # Load: (batch_load, latency_load, dists_that_run)
        exp_loads = [
            (100000, 100000, ['all']),
            (250000, 100000, ['all']),
            (400000, 100000, ['all']),
            (550000, 100000, ['all']),
            (700000, 100000, ['all']),
            (750000, 100000, ['all']),
            (800000, 100000, ['all']),
            (820000, 100000, ['all']),
            (835000, 100000, ['all']),
            (840000, 100000, ['all']),
            (850000, 100000, ['all'])
        ]
        bimodal_loads = [
            (90000, 10000, ['all']),
            (190000, 10000, ['all']),
            (290000, 10000, ['all']),
            (390000, 10000, ['all']),
            (490000, 10000, ['all']),
            (550000, 10000, ['all']),
            (570000, 10000, ['all']),
            (590000, 10000, ['all']),
            (620000, 10000, ['all']),
            (630000, 10000, ['rscs']),
            (640000, 10000, ['rscs'])
        ]
        port_bimodal_loads = [
            (10000, 10000, ['all']),
            (40000, 10000, ['all']),
            (70000, 10000, ['all']),
            (100000, 10000, ['all']),
            (130000, 10000, ['all']),
            (150000, 10000, ['all']),
            (160000, 10000, ['all']),
            (165000, 10000, ['all']),
            (170000, 10000, ['all']),
            (180000, 10000, ['rscs']),
            (181000, 10000, ['rscs']),
            (182000, 10000, ['rscs'])
        ]
        port_trimodal_loads = [
            (10000, 10000, ['all']),
            (20000, 10000, ['all']),
            (30000, 10000, ['all']),
            (40000, 10000, ['all']),
            (50000, 10000, ['all']),
            (60000, 10000, ['all']),
            (63000, 10000, ['all']),
            (64000, 10000, ['all']),
            (65000, 10000, ['all']),
            (69000, 10000, ['rscs']),
            (70000, 10000, ['rscs'])
        ]
        dist_loads = {'exp': exp_loads, 'bimodal': bimodal_loads,
                      'port_bimodal': port_bimodal_loads, 'port_trimodal': port_trimodal_loads}

        self.run_test(scheduling_policies, dist_loads)

    # Synthetic workloads with heterogeneous servers
    def fig_11(self):
        scheduling_policies = ['rscs', 'random']

        # Load: (batch_load, latency_load, dists_that_run)
        exp_loads = [
            (90000, 10000, ['all']),
            (100000, 100000, ['all']),
            (200000, 100000, ['all']),
            (300000, 100000, ['all']),
            (400000, 100000, ['all']),
            (450000, 100000, ['all']),
            (470000, 100000, ['all']),
            (480000, 100000, ['all']),
            (490000, 100000, ['all']),
            (500000, 100000, ['all']),
            (600000, 100000, ['rscs']),
            (650000, 100000, ['rscs']),
            (670000, 100000, ['rscs']),
            (680000, 100000, ['rscs'])
        ]
        bimodal_loads = [
            (90000, 10000, ['all']),
            (190000, 10000, ['all']),
            (290000, 10000, ['all']),
            (340000, 10000, ['all']),
            (350000, 10000, ['all']),
            (360000, 10000, ['all']),
            (370000, 10000, ['all']),
            (390000, 10000, ['all']),
            (440000, 10000, ['rscs']),
            (490000, 10000, ['rscs']),
            (540000, 10000, ['rscs']),
            (550000, 10000, ['rscs'])
        ]
        port_bimodal_loads = [
            (10000, 10000, ['all']),
            (30000, 10000, ['all']),
            (50000, 10000, ['all']),
            (70000, 10000, ['all']),
            (90000, 10000, ['all']),
            (100000, 10000, ['all']),
            (110000, 10000, ['all']),
            (130000, 10000, ['rscs']),
            (140000, 10000, ['rscs']),
            (150000, 10000, ['rscs'])
        ]
        port_trimodal_loads = [
            (9000, 1000, ['all']),
            (10000, 10000, ['all']),
            (20000, 10000, ['all']),
            (30000, 10000, ['all']),
            (35000, 10000, ['all']),
            (36000, 10000, ['all']),
            (37000, 10000, ['all']),
            (38000, 10000, ['all']),
            (40000, 10000, ['all']),
            (50000, 10000, ['rscs']),
            (53000, 10000, ['rscs']),
            (54000, 10000, ['rscs'])
        ]
        dist_loads = {'exp': exp_loads, 'bimodal': bimodal_loads,
                      'port_bimodal': port_bimodal_loads, 'port_trimodal': port_trimodal_loads}

        self.run_test(scheduling_policies, dist_loads, hetero=True)

    # Scalability results
    def fig_12(self):
        scheduling_policies = ['rscs', 'rscs4', 'rscs2', 'random', 'random4', 'random2', 'basic']

        # Load: (batch_load, latency_load, dists_that_run)
        bimodal_loads = [
            (40000, 10000, ['all']),
            (55000, 10000, ['basic']),
            (80000, 10000, ['basic']),
            (90000, 10000, ['all']),
            (100000, 10000, ['basic']),
            (102000, 10000, ['basic']),
            (110000, 10000, ['basic']),
            (130000, 10000, ['random2']),
            (140000, 10000, ['rscs', 'random', 'rscs4', 'random4', 'rscs2', 'random2']),
            (145000, 10000, ['rscs2', 'random2']),
            (150000, 10000, ['rscs2', 'random2']),
            (155000, 10000, ['rscs2']),
            (190000, 10000, ['rscs', 'random', 'rscs4', 'random4']),
            (240000, 10000, ['rscs4', 'random4']),
            (290000, 10000, ['rscs', 'random', 'rscs4', 'random4']),
            (300000, 10000, ['rscs4', 'random4']),
            (310000, 10000, ['rscs4', 'random4']),
            (320000, 10000, ['rscs4', 'random4']),
            (390000, 10000, ['rscs', 'random']),
            (490000, 10000, ['rscs', 'random']),
            (550000, 10000, ['rscs', 'random']),
            (570000, 10000, ['rscs', 'random']),
            (590000, 10000, ['rscs', 'random']),
            (630000, 10000, ['rscs', 'random']),
            (640000, 10000, ['rscs', 'random'])
        ]
        dist_loads = {'bimodal': bimodal_loads}

        self.run_test(scheduling_policies, dist_loads)

    # Experimental results for RocksDB
    def fig_13(self):
        scheduling_policies = ['rscs', 'random']

        # Load: (batch_load, latency_load, dists_that_run)
        db_bimodal_loads = [
            (40000, 10000, ['all']),
            (90000, 10000, ['all']),
            (140000, 10000, ['all']),
            (190000, 10000, ['all']),
            (240000, 10000, ['all']),
            (290000, 10000, ['all']),
            (340000, 10000, ['all']),
            (390000, 10000, ['all']),
            (420000, 10000, ['all']),
            (450000, 10000, ['all']),
            (480000, 10000, ['rscs']),
            (490000, 10000, ['rscs']),
            (495000, 10000, ['rscs'])
        ]
        db_port_bimodal_loads = [
            (20000, 10000, ['all']),
            (40000, 10000, ['all']),
            (60000, 10000, ['all']),
            (80000, 10000, ['all']),
            (100000, 10000, ['all']),
            (110000, 10000, ['all']),
            (120000, 10000, ['all']),
            (125000, 10000, ['all']),
            (130000, 10000, ['rscs']),
            (133000, 10000, ['rscs']),
            (135000, 10000, ['rscs'])
        ]
        dist_loads = {'db_bimodal': db_bimodal_loads,
                      'db_port_bimodal': db_port_bimodal_loads}

        self.run_test(scheduling_policies, dist_loads, rocks_db=True)

    def fig_14_client(self):
        scheduling_policies = ['client']

        # Load: (batch_load, latency_load, dists_that_run)
        bimodal_loads = [
            (0, 100000, ['all']),
            (0, 200000, ['all']),
            (0, 300000, ['all']),
            (0, 400000, ['all']),
            (0, 500000, ['all']),
            (0, 560000, ['all']),
            (0, 570000, ['all']),
            (0, 600000, ['all']),
            (0, 630000, ['all'])
        ]
        port_bimodal_loads = [
            (0, 20000, ['all']),
            (0, 50000, ['all']),
            (0, 80000, ['all']),
            (0, 110000, ['all']),
            (0, 140000, ['all']),
            (0, 160000, ['all']),
            (0, 170000, ['all']),
            (0, 175000, ['all']),
            (0, 180000, ['all'])
        ]
        dist_loads = {'bimodal': bimodal_loads,
                      'port_bimodal': port_bimodal_loads}

        self.run_test(scheduling_policies, dist_loads, cs_cli=True)

    def fig_14_r2p2(self):
        scheduling_policies = ['r2p2']

        # Load: (batch_load, latency_load, dists_that_run)
        bimodal_loads = [
            (90000, 10000, ['all']),
            (190000, 10000, ['all']),
            (290000, 10000, ['all']),
            (390000, 10000, ['all']),
            (440000, 10000, ['all']),
            (490000, 10000, ['all']),
            (510000, 10000, ['all'])
        ]
        port_bimodal_loads = [
            (10000, 10000, ['all']),
            (40000, 10000, ['all']),
            (70000, 10000, ['all']),
            (100000, 10000, ['all']),
            (130000, 10000, ['all']),
            (150000, 10000, ['all']),
            (160000, 10000, ['all']),
            (170000, 10000, ['all']),
            (171000, 10000, ['all']),
            (172000, 10000, ['all']),
            (175000, 10000, ['all'])
        ]
        dist_loads = {'bimodal': bimodal_loads,
                      'port_bimodal': port_bimodal_loads}

        self.run_test(scheduling_policies, dist_loads, r2p2=True)

    def fig_15(self):
        scheduling_policies = ['rr', 'shortest', 'sampling-4']

        # Load: (batch_load, latency_load, dists_that_run)
        bimodal_loads = [
            (90000, 10000, ['all']),
            (190000, 10000, ['all']),
            (290000, 10000, ['all']),
            (390000, 10000, ['all']),
            (490000, 10000, ['all']),
            (550000, 10000, ['all']),
            (570000, 10000, ['all']),
            (590000, 10000, ['all']),
            (620000, 10000, ['all']),
            (630000, 10000, ['all']),
            (640000, 10000, ['shortest', 'sampling-4']),
            (641000, 10000, ['shortest'])
        ]
        port_bimodal_loads = [
            (10000, 10000, ['all']),
            (40000, 10000, ['all']),
            (70000, 10000, ['all']),
            (100000, 10000, ['all']),
            (130000, 10000, ['all']),
            (150000, 10000, ['all']),
            (160000, 10000, ['all']),
            (165000, 10000, ['all']),
            (170000, 10000, ['all']),
            (173000, 10000, ['all']),
            (180000, 10000, ['shortest', 'sampling-4']),
            (181000, 10000, ['shortest', 'sampling-4']),
            (182000, 10000, ['shortest', 'sampling-4']),
            (183000, 10000, ['shortest', 'sampling-4'])
        ]
        dist_loads = {'bimodal': bimodal_loads,
                      'port_bimodal': port_bimodal_loads}

        self.run_test(scheduling_policies, dist_loads)

    def fig_16(self):
        scheduling_policies = ['int2', 'int3', 'proactive']

        # Load: (batch_load, latency_load, dists_that_run)
        bimodal_loads = [
            (90000, 10000, ['all']),
            (190000, 10000, ['all']),
            (290000, 10000, ['all']),
            (390000, 10000, ['all']),
            (490000, 10000, ['all']),
            (550000, 10000, ['all']),
            (570000, 10000, ['all']),
            (590000, 10000, ['all']),
            (620000, 10000, ['all']),
            (630000, 10000, ['all']),
            (640000, 10000, ['int2', 'int3']),
            (650000, 10000, ['int2'])
        ]
        port_bimodal_loads = [
            (10000, 10000, ['all']),
            (40000, 10000, ['all']),
            (70000, 10000, ['all']),
            (100000, 10000, ['all']),
            (130000, 10000, ['all']),
            (150000, 10000, ['all']),
            (160000, 10000, ['all']),
            (165000, 10000, ['all']),
            (170000, 10000, ['all']),
            (175000, 10000, ['proactive']),
            (180000, 10000, ['all']),
            (181000, 10000, ['int2', 'int3']),
            (182000, 10000, ['int2', 'int3']),
            (184000, 10000, ['int2']),
            (189000, 10000, ['int2']),
            (190000, 10000, ['int2'])
        ]
        dist_loads = {'bimodal': bimodal_loads,
                      'port_bimodal': port_bimodal_loads}

        self.run_test(scheduling_policies, dist_loads)

    def fig_17_failure(self):
        if self.server_conns == []:
            self.connect(servers, self.server_conns)
        if self.client_conns == []:
            self.connect(clients, self.client_conns)
        # Reset the server config and run
        self.config_servers(rocks_db=False, r2p2=False)
        self.run_server(rocks_db=False, r2p2=False)
        print('\nServers are ready...\n')

        # run switch
        if self.switch_conns == []:
            self.connect(switch, self.switch_conns)
        # Stop the currently running switch
        self.kill_switch()
        policy = 'switch_failure'
        cli_dir = switch_failure_client_dir

        # Run data plane
        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {scheduling_cmds[policy][0]}', bg=True)
        time.sleep(60)
        # start the control plane
        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {scheduling_cmds[policy][1]}', bg=True)

        # Start the latency client
        time.sleep(10)
        print("=== start client ===")
        self.exe(
            self.client_conns[1],
            f'cd {cli_dir}; echo {self.client_conns[1]["password"]} | sudo -S ./build/dpdk_client -l 0,1 -- -l 1 -c 12 -s 1 -d exp -q 850000 -x 50',
            bg=True)

        # Kill clients after some time
        time.sleep(60)
        self.kill_client()

        # Collect latency result
        output = self.exe(self.client_conns[1], f'cd {cli_dir}; \
                python3 parselats.py --tput ./results/tput', read=True)

        print("==== real-time tput (every 0.1 s) recovery under switch failure")
        print(output)

    def fig_17_reconfig(self):
        policy = 'reconfig'
        cli_dir = reconfig_client_dir

        if self.server_conns == []:
            self.connect(servers, self.server_conns)
        if self.client_conns == []:
            self.connect(clients, self.client_conns)


        # # Reset the server config and run
        self.config_servers(rocks_db=False, r2p2=False)
        self.run_server(rocks_db=False, r2p2=False)
        print('\nServers are ready...\n')
        #
        # run switch
        if self.switch_conns == []:
            self.connect(switch, self.switch_conns)
        # Stop the currently running switch
        self.kill_switch()
        # Run data plane
        print("start data plane...")
        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {scheduling_cmds[policy][0]}', bg=True)
        time.sleep(60)
        print("start control plane...")
        # start the control plane
        self.exe(
            self.switch_conns[0],
            f'cd {switch_sde_dir}; . ./set_sde.bash; {scheduling_cmds[policy][1]}', bg=True)

        print("start client...")
        time.sleep(15)
        self.exe(
            self.client_conns[1],
            f'cd {cli_dir}; echo {self.client_conns[1]["password"]} | sudo -S ./build/dpdk_client -l 0,1 -- -l 1 -c 12 -s 1 -d exp -q 500000 -x 50',
            bg=True)

        # Kill clients after some time
        time.sleep(60)
        self.kill_client()
        print("kill_client...")
        time.sleep(10)
        # Collect latency result
        latency = self.exe(self.client_conns[1], f'cd {cli_dir}; \
                python3 parselats.py --latency ./results/output ./results/output.reply_ns', read=True)

        print("==== real-time latency under server reconfiguration")
        print(latency)


    # ******************************
    # Initialize the console
    # ******************************
    def __init__(self):
        super().__init__()

    # ******************************
    # sync files, run in local machine
    # ******************************
    def sync_client(self):
        for host in clients:
            cmd = "sshpass -p %s rsync -r client_code %s@%s:%s" % (host['password'], host['username'], host['hostname'], rscs_dir)
            subprocess.call(cmd, shell = True)

    def sync_server(self):
        for host in servers:
            cmd = "sshpass -p %s rsync -r server_code %s@%s:%s" % (host['password'], host['username'], host['hostname'], rscs_dir)
            subprocess.call(cmd, shell = True)

    def sync_switch(self):
        for host in switch:
            cmd = "sshpass -p %s rsync -r switch_code %s@%s:%s" % (host['password'], host['username'], host['hostname'], remote_switch_dir)
            subprocess.call(cmd, shell = True)

def sigint_handler(sig, frame):
    RSCSConsole().kill_all()
    print("\nConsole exited\n")
    sys.exit(0)


def print_usage():
    print('Usage:')
    print('\tconsole.py setup_{{basic, rocksdb, r2p2}_server, client, all}')
    print('\tconsole.py build_{basic, cs, failure, r2p2, reconfig}_client')
    print('\tconsole.py run_{[switch] [policy], {basic, rocksdb, r2p2}_server}')
    print('\tconsole.py compile_switch')
    print('\tconsole.py kill_{switch, server, client, all}')
    print('\tconsole.py sync_{server, client}')
    print('\tconsole.py fig_{10, 11, 12, 13, 14_{r2p2, client}, 15, 16, 17_{failure, reconfig}}')
    print('\tconsole.py install_{dpdk, gsl}')


if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print_usage()
        sys.exit(0)

    # signal.signal(signal.SIGINT, sigint_handler)

    console = RSCSConsole()

    arg = sys.argv[1]
    if arg == 'setup_basic_server':
        console.setup_servers()
    elif arg == 'setup_rocksdb_server':
        console.setup_servers(rocks_db=True)
    elif arg == 'setup_r2p2_server':
        console.setup_r2p2_server()
    elif arg == 'setup_client':
        console.setup_clients()
    elif arg == 'setup_all':
        console.setup_all()
    elif arg == 'build_basic_client':
        console.build_clients()
    elif arg == 'build_cs_client':
        console.build_clients(cs_client_dir)
    elif arg == 'build_failure_client':
        console.build_clients(switch_failure_client_dir)
    elif arg == 'build_r2p2_client':
        console.build_clients(r2p2_client_dir)
    elif arg == 'build_reconfig_client':
        console.build_clients(reconfig_client_dir)
    elif arg == "sync_server":
        console.sync_server()
    elif arg == "reboot_servers":
        console.reboot_servers()
    elif arg == "sync_client":
        console.sync_client()
    elif arg == 'run_switch':
        policy = sys.argv[2]
        if not policy:
            print_usage()
        else:
            console.run_switch(policy)
    elif arg == 'compile_switch':
        console.compile_switch(sys.argv[2])
    elif arg == 'run_basic_server':
        console.build_and_run_servers()
    elif arg == 'run_rocksdb_server':
        console.build_and_run_servers(rocks_db=True)
    elif arg == 'run_r2p2_server':
        console.run_r2p2_server()
    elif arg == 'kill_switch':
        console.kill_switch()
    elif arg == 'sync_switch':
        console.sync_switch()
    elif arg == 'sync_client':
        console.sync_client()
    elif arg == 'kill_server':
        console.kill_server()
    elif arg == 'kill_client':
        console.kill_client()
    elif arg == 'kill_all':
        console.kill_all()
    elif arg == 'fig_10':
        console.fig_10()
    elif arg == 'fig_11':
        console.fig_11()
    elif arg == 'fig_12':
        console.fig_12()
    elif arg == 'fig_13':
        console.fig_13()
    elif arg == 'fig_14_r2p2':
        console.fig_14_r2p2()
    elif arg == 'fig_14_client':
        console.fig_14_client()
    elif arg == 'fig_15':
        console.fig_15()
    elif arg == 'fig_16':
        console.fig_16()
    elif arg == 'fig_17_failure':
        console.fig_17_failure()
    elif arg == 'fig_17_reconfig':
        console.fig_17_reconfig()
    elif arg == 'install_gsl':
        console.install_gsl()
    elif arg == 'install_dpdk':
        console.install_dpdk()
    else:
        print_usage()
