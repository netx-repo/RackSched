"""
@file config.py
@brief The file to input your configs
"""

# Change these to your own username, host address, and password
switch = [{'hostname': 'netxy.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': ''}]
servers = [{'hostname': 'netx1.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.1/24'},
           {'hostname': 'netx2.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.2/24'},
           {'hostname': 'netx3.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.3/24'},
           {'hostname': 'netx4.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.4/24'},
           {'hostname': 'netx5.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.5/24'},
           {'hostname': 'netx6.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.6/24'},
           {'hostname': 'netx7.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.7/24'},
           {'hostname': 'netx8.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.8/24'}]
clients = [{'hostname': 'netx11.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.11/24'},
           {'hostname': 'netx12.cs.jhu.edu', 'username': 'username', 'password': 'userpassword', 'ip': '10.1.0.12/24'}]

remote_switch_dir = '/home/hz/RSCS/'
switch_sde_dir = '/home/hz/bf-sde-8.9.1-pg/bf-sde-8.9.1'
scheduling_cmds = {'basic': ('./run_switchd.sh -p basic_switch', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/basic_switch/ptf-tests/'),
                   'rscs': ('./run_switchd.sh -p rscs', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/rscs/ptf-tests/'),
                   'rscs4': ('./run_switchd.sh -p rscs_4server', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/rscs_4server/ptf-tests/'),
                   'rscs2': ('./run_switchd.sh -p rscs_2server', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/rscs_2server/ptf-tests/'),
                   'random': ('./run_switchd.sh -p random_schedule', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/random_schedule/ptf-tests/'),
                   'random4': ('./run_switchd.sh -p random_schedule_4server', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/random_schedule_4server/ptf-tests/'),
                   'random2': ('./run_switchd.sh -p random_schedule_2server', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/random_schedule_2server/ptf-tests/'),
                   'rr': ('./run_switchd.sh -p rr_schedule', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/rr_schedule/ptf-tests/'),
                   'shortest': ('./run_switchd.sh -p shortest', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/shortest/ptf-tests/'),
                   'sampling-4': ('./run_switchd.sh -p p4_sq', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/p4_sq/ptf-tests/'),
                   'int2': ('./run_switchd.sh -p int2', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/int2/ptf-tests/'),
                   'int3': ('./run_switchd.sh -p rscs', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/rscs/ptf-tests/'),
                   'proactive': ('./run_switchd.sh -p proactive', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/proactive/ptf-tests/'),
                   'client': ('./run_switchd.sh -p basic_switch', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/basic_switch/ptf-tests/'),
                   'r2p2': ('./run_switchd.sh -p r2p2', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/r2p2/ptf-tests/'),
                   'switch_failure': ('./run_switchd.sh -p rscs_multi', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/rscs_multi/ptf-tests/'),
                   'reconfig': ('./run_switchd.sh -p server_reconfig', './run_p4_tests.sh -t /home/hz/RSCS/switch_code/server_reconfig/ptf-tests/')
                   }

rocksdb_modify_servers = ['2', '3', '4', '5', '6', '7']

rscs_dir = '/home/username/RSCS'  # Change this to the location of this repo
server_dir = f'{rscs_dir}/server_code/shinjuku'
rocksdb_server_dir = f'{rscs_dir}/server_code/shinjuku-rocksdb'
r2p2_dir = f'{rscs_dir}/server_code/r2p2'

client_dir = f'{rscs_dir}/client_code/client'
r2p2_client_dir = f'{rscs_dir}/client_code/r2p2-client'
cs_client_dir = f'{rscs_dir}/client_code/cs-client'
switch_failure_client_dir = f'{rscs_dir}/client_code/failure-client'
reconfig_client_dir = f'{rscs_dir}/client_code/reconfig-client'

# r2p2_dpdk_dir = f'{r2p2_dir}/dpdk-stable-16.11.1'
dpdk_dir = f'{client_dir}/tools'
server_log_dir = f'{rscs_dir}/server_code/logs'
client_log_dir = f'{rscs_dir}/client_code/logs'

RTE_SDK = '/home/username/dpdk/dpdk-stable-16.11.1'
R2P2_RTE_SDK = f'{r2p2_dir}/dpdk-stable-16.11.1'
RTE_TARGET = 'x86_64-native-linuxapp-gcc'
