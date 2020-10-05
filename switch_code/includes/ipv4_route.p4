action _drop () {
    drop();
}

table drop_pkt {
    actions {_drop;}
    default_action : _drop();
}

action act_rewrite_iface(iface) {
    modify_field(ig_intr_md_for_tm.ucast_egress_port,iface);
}

table ipv4_route {
    reads {
        ipv4.dstAddr : exact;
    }
    actions {
        act_rewrite_iface;
    }
}

action act_set_mac(smac, dmac, dip) {
    modify_field(ethernet.srcAddr, smac);
    modify_field(ethernet.dstAddr, dmac);
    modify_field(ipv4.dstAddr, dip);
}

table set_mac {
    reads {
        ig_intr_md_for_tm.ucast_egress_port: exact;
    }
    actions {
        act_set_mac;
    }
    size : 512;
}
