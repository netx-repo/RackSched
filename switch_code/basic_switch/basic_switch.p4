#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/headers.p4"
#include "../includes/parsers.p4"

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

action act_set_mac (smac, dmac) {
    modify_field (ethernet.srcAddr, smac);
    modify_field (ethernet.dstAddr, dmac);
}

table set_mac {
    reads {
        ig_intr_md_for_tm.ucast_egress_port: exact;
    }
    actions {
        act_set_mac;
    }
}

control ingress {
    apply (ipv4_route);
}

control egress {
    apply (set_mac);
}
