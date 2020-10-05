import pd_base_tests
import pdb, sys
from collections import OrderedDict
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *

from r2p2.p4_pd_rpc.ttypes import *
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
        pd_base_tests.ThriftInterfaceDataPlane.__init__(self, ["r2p2"])

    def runTest(self):
        sess_hdl = self.conn_mgr.client_init()
        dev_tgt = DevTarget_t(0, hex_to_i16(0xFFFF))
        addPorts(self)

        start_ip = 0x0a010001
        switch_portbase = 188
        server_num = 12
        core_num = 8

        ## write to register
        jbsq_n = 3
        self.client.register_write_jbsq_n(sess_hdl, dev_tgt, 0, jbsq_n)
        time.sleep(1)
        flags = r2p2_register_flags_t(read_hw_sync = True)
        jbsq_value = self.client.register_read_jbsq_n(sess_hdl, dev_tgt, 0, flags)
        print "jbsq_value", jbsq_value

        for i in range(server_num):
            match_spec = r2p2_ipv4_route_match_spec_t(start_ip+i)
            action_spec = r2p2_act_rewrite_iface_action_spec_t(switch_portbase-4*i)
            self.client.ipv4_route_table_add_with_act_rewrite_iface(sess_hdl,dev_tgt, match_spec, action_spec)

        netx_mac_list = ["\x00\x00\x00\x00\x00\x01", "\x00\x00\x00\x00\x00\x02",\
            "\x00\x00\x00\x00\x00\x03", "\x00\x00\x00\x00\x00\x04",\
            "\x00\x00\x00\x00\x00\x05", "\x00\x00\x00\x00\x00\x06",\
            "\x00\x00\x00\x00\x00\x07", "\x00\x00\x00\x00\x00\x08"]

        for i in xrange(server_num):
            for j in xrange(core_num):
                match_spec = r2p2_send_to_curserver_match_spec_t(i, j)
                dst_mac = netx_mac_list[j]
                action_spec = r2p2_act_set_vfip_action_spec_t(switch_portbase-4*i,start_ip+i,dst_mac)
                self.client.send_to_curserver_table_add_with_act_set_vfip(sess_hdl,dev_tgt, match_spec, action_spec)

        # add entries for table "set_mac"

        match_spec = r2p2_set_mac_match_spec_t(188)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x2e", "\x3c\xfd\xfe\xab\xde\xd8")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(184)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x32", "\x3c\xfd\xfe\xa6\xeb\x10")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(180)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x36", "\x3c\xfd\xfe\xaa\x5d\x00")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(176)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x3a", "\x3c\xfd\xfe\xaa\x46\x68")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(172)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x3e", "\x3c\xfd\xfe\xab\xde\xf0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(168)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x42", "\x3c\xfd\xfe\xab\xdf\x90")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(164)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x46", "\x3c\xfd\xfe\xab\xe0\x50")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(160)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x4a", "\x3c\xfd\xfe\xab\xd9\xf0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(156)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x4e", "\x3c\xfd\xfe\xc3\xdf\xe0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(152)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x52", "\x3c\xfd\xfe\xc3\xe9\xf0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(148)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x56", "\x3c\xfd\xfe\xc3\xe0\x60")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        match_spec = r2p2_set_mac_match_spec_t(144)
        action_spec = r2p2_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x5a", "\x3c\xfd\xfe\xc3\xe9\xb0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
        handle_mac.append(result)

        self.conn_mgr.complete_operations(sess_hdl);
        queue_list = [0]*8
        core_idx = 1
        while True:
            time.sleep(1)
            flags = r2p2_register_flags_t(read_hw_sync = True)
            for i in xrange(8):
                if i == 0:
                    value_t = self.client.register_read_server_qlen1(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 1:
                    value_t = self.client.register_read_server_qlen2(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 2:
                    value_t = self.client.register_read_server_qlen3(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 3:
                    value_t = self.client.register_read_server_qlen4(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 4:
                    value_t = self.client.register_read_server_qlen5(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 5:
                    value_t = self.client.register_read_server_qlen6(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 6:
                    value_t = self.client.register_read_server_qlen7(sess_hdl, dev_tgt, core_idx, flags)
                elif i == 7:
                    value_t = self.client.register_read_server_qlen8(sess_hdl, dev_tgt, core_idx, flags)
                queue_list[i] = value_t[1].f1
            print queue_list
            print '\n'
            sys.stdout.flush()
