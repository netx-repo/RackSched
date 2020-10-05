import pd_base_tests
import pdb
from collections import OrderedDict
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *

from p4_sq.p4_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *
from pal_rpc.ttypes import *
from mirror_pd_rpc.ttypes import *
from pkt_pd_rpc.ttypes import *

import time


dev_id = 0
handle_ipv4 = []
handle_mac = []

def addPorts(test):
    swports = [188, 184, 180, 176, 172, 168, 164, 160, 156, 152, 148, 144]
    test.pal.pal_port_add_all(dev_id, pal_port_speed_t.BF_SPEED_40G, pal_fec_type_t.BF_FEC_TYP_NONE)
    test.pal.pal_port_enable_all(dev_id)
    ports_not_up = True
    print "Waiting for ports to come up..."
    sys.stdout.flush()
    num_tries = 12
    i = 0
    while ports_not_up:
        ports_not_up = False
        for p in swports:
            x = test.pal.pal_port_oper_status_get(dev_id, p)
            if x == pal_oper_status_t.BF_PORT_DOWN:
                ports_not_up = True
                print "  port", p, "is down"
                sys.stdout.flush()
                time.sleep(3)
                break
        i = i + 1
        if i >= num_tries:
            break
    assert ports_not_up == False
    print "All ports up."
    sys.stdout.flush()
    return

class Test(pd_base_tests.ThriftInterfaceDataPlane):
    def __init__(self):
        pd_base_tests.ThriftInterfaceDataPlane.__init__(self, ["p4_sq"])

    # veth0 and veth2 are clients.
    # veth4 is the primary server while veth6 and veth8 are the backups
    def runTest(self):
        sess_hdl = self.conn_mgr.client_init()
        dev_tgt = DevTarget_t(0, hex_to_i16(0xFFFF))
        addPorts(self)

        start_ip = 0x0a010001
        switch_portbase = 188
        server_num = 12

        for i in range(server_num):
            match_spec = p4_sq_ipv4_route_match_spec_t(start_ip+i)
            action_spec = p4_sq_act_rewrite_iface_action_spec_t(switch_portbase-4*i)
            self.client.ipv4_route_table_add_with_act_rewrite_iface(sess_hdl,dev_tgt, match_spec, action_spec)
            if i < 8:
                match_spec = p4_sq_send_to_curserver_match_spec_t(i)
                action_spec = p4_sq_act_rewrite_iface_action_spec_t(switch_portbase-4*i)
                self.client.send_to_curserver_table_add_with_act_rewrite_iface(sess_hdl,dev_tgt, match_spec, action_spec)


        for i in xrange(server_num):
            match_spec = p4_sq_assign_random1_match_spec_t(i)
            if i == 0:
                 self.client.assign_random1_table_add_with_act_random1_qlen1(sess_hdl,dev_tgt,match_spec)
            elif i == 1:
                 self.client.assign_random1_table_add_with_act_random1_qlen2(sess_hdl,dev_tgt,match_spec)
            elif i == 2:
                 self.client.assign_random1_table_add_with_act_random1_qlen3(sess_hdl,dev_tgt,match_spec)
            elif i == 3:
                 self.client.assign_random1_table_add_with_act_random1_qlen4(sess_hdl,dev_tgt,match_spec)
            elif i == 4:
                 self.client.assign_random1_table_add_with_act_random1_qlen5(sess_hdl,dev_tgt,match_spec)
            elif i == 5:
                 self.client.assign_random1_table_add_with_act_random1_qlen6(sess_hdl,dev_tgt,match_spec)
            elif i == 6:
                 self.client.assign_random1_table_add_with_act_random1_qlen7(sess_hdl,dev_tgt,match_spec)
            elif i == 7:
                 self.client.assign_random1_table_add_with_act_random1_qlen8(sess_hdl,dev_tgt,match_spec)

        for i in xrange(server_num):
            match_spec = p4_sq_assign_random2_match_spec_t(i)
            if i == 0:
                 self.client.assign_random2_table_add_with_act_random2_qlen1(sess_hdl,dev_tgt,match_spec)
            elif i == 1:
                 self.client.assign_random2_table_add_with_act_random2_qlen2(sess_hdl,dev_tgt,match_spec)
            elif i == 2:
                 self.client.assign_random2_table_add_with_act_random2_qlen3(sess_hdl,dev_tgt,match_spec)
            elif i == 3:
                 self.client.assign_random2_table_add_with_act_random2_qlen4(sess_hdl,dev_tgt,match_spec)
            elif i == 4:
                 self.client.assign_random2_table_add_with_act_random2_qlen5(sess_hdl,dev_tgt,match_spec)
            elif i == 5:
                 self.client.assign_random2_table_add_with_act_random2_qlen6(sess_hdl,dev_tgt,match_spec)
            elif i == 6:
                 self.client.assign_random2_table_add_with_act_random2_qlen7(sess_hdl,dev_tgt,match_spec)
            elif i == 7:
                 self.client.assign_random2_table_add_with_act_random2_qlen8(sess_hdl,dev_tgt,match_spec)

        for i in xrange(server_num):
            match_spec = p4_sq_assign_random3_match_spec_t(i)
            if i == 0:
                 self.client.assign_random3_table_add_with_act_random3_qlen1(sess_hdl,dev_tgt,match_spec)
            elif i == 1:
                 self.client.assign_random3_table_add_with_act_random3_qlen2(sess_hdl,dev_tgt,match_spec)
            elif i == 2:
                 self.client.assign_random3_table_add_with_act_random3_qlen3(sess_hdl,dev_tgt,match_spec)
            elif i == 3:
                 self.client.assign_random3_table_add_with_act_random3_qlen4(sess_hdl,dev_tgt,match_spec)
            elif i == 4:
                 self.client.assign_random3_table_add_with_act_random3_qlen5(sess_hdl,dev_tgt,match_spec)
            elif i == 5:
                 self.client.assign_random3_table_add_with_act_random3_qlen6(sess_hdl,dev_tgt,match_spec)
            elif i == 6:
                 self.client.assign_random3_table_add_with_act_random3_qlen7(sess_hdl,dev_tgt,match_spec)
            elif i == 7:
                 self.client.assign_random3_table_add_with_act_random3_qlen8(sess_hdl,dev_tgt,match_spec)

        for i in xrange(server_num):
            match_spec = p4_sq_assign_random4_match_spec_t(i)
            if i == 0:
                 self.client.assign_random4_table_add_with_act_random4_qlen1(sess_hdl,dev_tgt,match_spec)
            elif i == 1:
                 self.client.assign_random4_table_add_with_act_random4_qlen2(sess_hdl,dev_tgt,match_spec)
            elif i == 2:
                 self.client.assign_random4_table_add_with_act_random4_qlen3(sess_hdl,dev_tgt,match_spec)
            elif i == 3:
                 self.client.assign_random4_table_add_with_act_random4_qlen4(sess_hdl,dev_tgt,match_spec)
            elif i == 4:
                 self.client.assign_random4_table_add_with_act_random4_qlen5(sess_hdl,dev_tgt,match_spec)
            elif i == 5:
                 self.client.assign_random4_table_add_with_act_random4_qlen6(sess_hdl,dev_tgt,match_spec)
            elif i == 6:
                 self.client.assign_random4_table_add_with_act_random4_qlen7(sess_hdl,dev_tgt,match_spec)
            elif i == 7:
                 self.client.assign_random4_table_add_with_act_random4_qlen8(sess_hdl,dev_tgt,match_spec)
        # add entries for table "set_mac"

        match_spec = p4_sq_set_mac_match_spec_t(188)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x2e", "\x3c\xfd\xfe\xab\xde\xd8", start_ip)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(184)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x32", "\x3c\xfd\xfe\xa6\xeb\x10", start_ip+1)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(180)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x36", "\x3c\xfd\xfe\xaa\x5d\x00", start_ip+2)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(176)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x3a", "\x3c\xfd\xfe\xaa\x46\x68", start_ip+3)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(172)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x3e", "\x3c\xfd\xfe\xab\xde\xf0", start_ip+4)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(168)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x42", "\x3c\xfd\xfe\xab\xdf\x90", start_ip+5)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(164)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x46", "\x3c\xfd\xfe\xab\xe0\x50", start_ip+6)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(160)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x4a", "\x3c\xfd\xfe\xab\xd9\xf0", start_ip+7)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(156)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x4e", "\x3c\xfd\xfe\xc3\xdf\xe0", start_ip+8)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(152)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x52", "\x3c\xfd\xfe\xc3\xe9\xf0", start_ip+9)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(148)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x56", "\x3c\xfd\xfe\xc3\xe0\x60", start_ip+10)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = p4_sq_set_mac_match_spec_t(144)
        action_spec = p4_sq_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x5a", "\x3c\xfd\xfe\xc3\xe9\xb0", start_ip+11)
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        self.conn_mgr.complete_operations(sess_hdl);


        queue_list = [0]*8
        while True:
            time.sleep(1)
            flags = p4_sq_register_flags_t(read_hw_sync = True)
            for i in xrange(8):
                if i == 0:
                    value_t = self.client.register_read_server_qlen1(sess_hdl, dev_tgt, 2, flags)
                elif i == 1:
                    value_t = self.client.register_read_server_qlen2(sess_hdl, dev_tgt, 2, flags)
                elif i == 2:
                    value_t = self.client.register_read_server_qlen3(sess_hdl, dev_tgt, 2, flags)
                elif i == 3:
                    value_t = self.client.register_read_server_qlen4(sess_hdl, dev_tgt, 2, flags)
                elif i == 4:
                    value_t = self.client.register_read_server_qlen5(sess_hdl, dev_tgt, 2, flags)
                elif i == 5:
                    value_t = self.client.register_read_server_qlen6(sess_hdl, dev_tgt, 2, flags)
                elif i == 6:
                    value_t = self.client.register_read_server_qlen7(sess_hdl, dev_tgt, 2, flags)
                elif i == 7:
                    value_t = self.client.register_read_server_qlen8(sess_hdl, dev_tgt, 2, flags)
                queue_list[i] = value_t[1].f1
            # print value1[1], value2[1]
            print queue_list
            print '\n'
