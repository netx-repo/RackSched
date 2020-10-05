## 0. Introduction<br>

This repository contains the source code for our OSDI'20 paper
["RackSched: A Microsecond-Scale Scheduler for Rack-Scale Computers"](https://www.usenix.org/conference/osdi20/presentation/zhu).

## 1. Content<br>

- client_code/<br>
  - client/: dpdk code for default client.<br>
  - cs-client/: `Client(100)` in Figure 14, where the clients track the queue lengths.<br>
  - failure-client/: used in Figure 17(a).<br>
  - r2p2-client/: used for `R2P2` in Figure 14.<br>
  - reconfig-client/: used in Figure 17(b).<br>
- server_code/<br>
  - r2p2/: used for `R2P2` in Figure 14.<br>
  - shinjuku/: default Shinjuku server.<br>
  - shinjuku-rocskdb/: used in Figure 13.<br>
- switch_code/<br>
  - basic_switch/: only do ipv4 routing.
  - ht/: multi-stage register arrays for `ReqTable`.
  - includes/: packet header, parser and routing table.
  - qlen/: register arrays for `LoadTable`.
  - int2/: used in Figure 16, which only tracks the minimum number of outstanding requests.
  - p4_sq/: used for `Sampling-4` in Figure 15.
  - proactive/: used for `Proactive` in Figure 16.
  - r2p2/: used for `R2P2` in Figure 14.
  - random_schedule/: used for `Shinjuku` by default.
  - random_schedule_2server/: used for `Shinjuku(2)` in Figure 12.
  - random_schedule_4server/: used for `Shinjuku(4)` in Figure 12.
  - rr_schedule/: used for `RR` in Figure 15.
  - rscs/: used for `RSCS` by default.
  - rscs_2server/: used for `RSCS(2)` in Figure 12.
  - rscs_4server/: used for `RSCS(4)` in Figure 12.
  - rscs_multi/: used in Figure 17(a), which has the `ReqTable` to store the connection states.
  - server_reconfig/: used in Figure 17(b).
  - shortest/: used for `Shortest` in Figure 15.
  - po2.p4: used for power-of-2 choices
- console.py: A script to help run evaluations.<br>
- config.py: Some parameters to configure.<br>
- README.md: This file.<br>

## 2. Environment requirement<br>

- Hardware
  - A Barefoot Tofino switch.<br>
  - Servers with a DPDK-compatible NIC (we used an Intel XL710 for 40GbE QSFP+) and multi-core CPU.<br>
- Software<br>
  The current version of RSCS is tested on:<br>
  - Barefoot P4 Studio (version 8.9.1 or later).<br>
  - DPDK (16.11.1) for the clients.<br>
  - Linux kernel 4.4 and gcc version 5.5 for Shinjuku servers.<br>
  We provide easy-to-use scripts to run the experiments and to analyze the results. To use the scripts, you need:
  - Python 3.6+, paramiko at your endhost.<br>
    `pip3 install paramiko`

## 3. How to run<br>

- Configure the parameters in the files based on your environment<br>
  - `config.py`: provide the information of your servers (username, passwd, hostname, dir).<br>
- Environment setup<br>
  - Setup the switch<br>
    - Setup the necessary environment variables to point to the appropriate locations.<br>
    - Copy the files to the switch.<br>
    - `python3 console.py sync_switch`<br>
  - Compile p4 programs.<br>
    - `python3 console.py compile_switch <prog_name>`<br>
      This will take **a couple of minutes**. You can check `switch_code/logs/p4_compile.log` in the switch to see if it's finished.
      Example: `python3 console.py compile_switch rscs`
- Setup the servers<br>
  - Setup DPDK environment (install dpdk, and set correct environment variables).<br>
  - Copy the files to the servers.<br>
    - `python3 console.py sync_server`<br>
  - For Shinjuku-based basic and RocksDB servers: install the necessary libraries and pull the dependencies<br>
    - `python3 console.py setup_basic_server` or `python3 console.py setup_rocksdb_server`<br>
    - Note that depending on your specific machine configuration and networking condition, the time to finish the above command may vary. We have reserved 60s for basic server and 90s for RocksDB server.<br>
    - Also note that sometimes the dependency source will randomly reset the connection when too many servers fetch dependencies at the same time, causing some servers successfully fetch the dependencies while the others fail. In this case, please try running the command for another time or manually fetch the dependency by running `./deps/fetch-deps.sh` in the corresponding server directory.
  - For R2P2 server: build the customized DPDK and setup the DPDK related environment variables<br>
    - `python3 console.py setup_r2p2_server`<br>
    - Building DPDK takes time, we reserved 180s for it to complete.<br>
  - Building the server is incorporated in running the server.<br>
- Build the clients<br>
  - For all kinds of clients, install DPDK, and set correct environment variables).<br>
    - `python3 console.py install_dpdk` <br>
  - make/build the client.<br>
- Run the programs<br>
  - Run p4 program on the switch<br>
    - `python3 console.py run_switch rscs`<br>
      It will bring up both the data-plane module and the control-plane module. It may take **up to 150 seconds** (may vary between devices). You can check `switch_code/logs/run_ptf_test.log` in the switch to see if it's finished (it will output the real-time queue length list).
  - Run Shinjuku servers and clients to reproduce results in the paper<br>
    - `python3 console.py fig_*`<br>
- Kill the processes<br>
  - Kill the switch process
    - `python3 console.py kill_switch`
  - Kill the Shinjuku or R2P2 processes
    - `python3 console.py kill_server`
  - Kill the client processes
    - `python3 console.py kill_client`
  - Kill all the processes (switch, servers, clients)
    - `python3 console.py kill_all`
- Other commands<br>
  There are also some other commands you can use:
  - `python3 console.py sync_switch`<br>
    copy the local "switch_code" to the switch
  - `python3 console.py sync_server`<br>
    copy the local "server_code" to the servers
  - `python3 console.py sync_client`<br>
    copy the local "client_code" to the clients

## 4. How to reproduce the results<br>

**NOTE**
We recommend running RocksDB(`python3 console.py fig_13`) and R2P2(`python3 console.py fig_14_r2p2`) at last, as these experiments may require server reboot.

- Configure the parameters in the files based on your environment
  - `config.py`: provide the information of your servers (username, passwd, hostname, dir).<br>
- Setup the switch
  - Setup the necessary environment variables to point to the appropriate locations.<br>
  - Copy the files to the switch: `python3 console.py sync_switch`<br>
  - Compile the rscs: `python3 console.py compile_switch`<br>
    Again it will take **a couple of minutes**. You can check `switch_code/logs/p4_compile.log` in the switch to see if it's finished.
- Setup the servers
  - Copy the necessary files to server: `python3 console.py sync_server`<br>
  - Setup the basic server, RocksDB server (for Figure 13), and R2P2 server (for Figure 14) before reproducing the figures.<br>
    - Basic Shinjuku server: `python3 console.py setup_basic_server`<br>
    - RocksDB Shinjuku server: `python3 console.py setup_rocksdb_server`<br>
    - R2P2 server: `python3 console.py setup_r2p2_server`<br>
- Build the clients
  - Basic client: `python3 console.py build_basic_client`<br>
  - CS client: `python3 console.py build_cs_client`<br>
  - Failure client: `python3 console.py build_failure_client`<br>
  - R2P2 client: `python3 console.py build_r2p2_client`<br>
  - Reconfig client: `python3 console.py build_reconfig_client`<br>
- After both the switch and the servers are correctly configured, you can replay the results by running console.py. The following command will execute the switch program, shinjuku server programs, and client programs automatically and output the results to the terminal.<br>
  - Figure 10: `python3 console.py fig_10`<br>
  - Figure 11: `python3 console.py fig_11`<br>
  - Figure 12: `python3 console.py fig_12`<br>
  - Figure 13: `python3 console.py fig_13`<br>
  - `R2P2` in Figure 14: `python3 console.py fig_14_r2p2`<br>
  - `Client(100)` in Figure 11: `python3 console.py fig_14_client`<br>
  - Figure 15: `python3 console.py fig_15`<br>
  - Figure 16: `python3 console.py fig_16`<br>
  - Figure 17(a): `python3 console.py fig_17_failure`<br>
  - Figure 17(b): `python3 console.py fig_17_reconfig`<br>

## 5. Contact<br>

For any question, please contact `hzhu at jhu dot edu`.
