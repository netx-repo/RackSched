import pd_base_tests
import pdb
from collections import OrderedDict
from ptf import config
from ptf.testutils import *
from ptf.thriftutils import *

from basic_switch.p4_pd_rpc.ttypes import *
from res_pd_rpc.ttypes import *
from pal_rpc.ttypes import *
from mirror_pd_rpc.ttypes import *
from pkt_pd_rpc.ttypes import *

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

class BasicSwitchTest(pd_base_tests.ThriftInterfaceDataPlane):
    def __init__(self):
        pd_base_tests.ThriftInterfaceDataPlane.__init__(self, ["basic_switch"])

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
            match_spec = basic_switch_ipv4_route_match_spec_t(start_ip+i)
            action_spec = basic_switch_act_rewrite_iface_action_spec_t(switch_portbase-4*i)
            self.client.ipv4_route_table_add_with_act_rewrite_iface(sess_hdl,dev_tgt, match_spec, action_spec)

        # add entries for table "set_mac"
        match_spec = basic_switch_set_mac_match_spec_t(188)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x2e", "\x3c\xfd\xfe\xab\xde\xd8")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(184)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x32", "\x3c\xfd\xfe\xa6\xeb\x10")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(180)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x36", "\x3c\xfd\xfe\xaa\x5d\x00")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(176)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x3a", "\x3c\xfd\xfe\xaa\x46\x68")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(172)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x3e", "\x3c\xfd\xfe\xab\xde\xf0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(168)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x42", "\x3c\xfd\xfe\xab\xdf\x90")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(164)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x46", "\x3c\xfd\xfe\xab\xe0\x50")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(160)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x4a", "\x3c\xfd\xfe\xab\xd9\xf0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(156)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x4e", "\x3c\xfd\xfe\xc3\xdf\xe0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(152)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x52", "\x3c\xfd\xfe\xc3\xe9\xf0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(148)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x56", "\x3c\xfd\xfe\xc3\xe0\x60")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)

        match_spec = basic_switch_set_mac_match_spec_t(144)
        action_spec = basic_switch_act_set_mac_action_spec_t("\xa8\x2b\xb5\xde\x92\x5a", "\x3c\xfd\xfe\xc3\xe9\xb0")
        result = self.client.set_mac_table_add_with_act_set_mac(sess_hdl, dev_tgt, match_spec, action_spec)
