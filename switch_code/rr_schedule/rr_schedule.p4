#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#include "../includes/parsers.p4"
#include "../includes/ipv4_route.p4"

header_type sq_metadata_t {
    fields {
        curserver : 8;
        counter_idx : 8;
    }
}

metadata sq_metadata_t sq_md;

register current_server {
    width : 16;
    instance_count : 4;
}

// round-roubin

action act_get_counter_idx() {
    subtract(sq_md.counter_idx, PORT_OFFSET, udp.dstPort);
}

table get_counter_idx {
    actions {act_get_counter_idx;}
    default_action : act_get_counter_idx;
}

blackbox stateful_alu salu_exe_curserver {
    reg : current_server;
    //WARN: sth may be wrong, it should be >=, but turned out > works well
    //alu_lo should be the value after modification, but
    condition_lo : register_lo >= SERVER_NUM8-1;
    update_lo_1_predicate : condition_lo;
    update_lo_1_value : 0;
    update_lo_2_predicate : not condition_lo;
    update_lo_2_value : register_lo + 1;
    output_value : alu_lo;
    output_dst : sq_md.curserver;
}

action act_exe_curserver() {
    salu_exe_curserver.execute_stateful_alu(sq_md.counter_idx);
}

table exe_curserver {
    actions {act_exe_curserver;}
    default_action : act_exe_curserver;
}


table send_to_curserver {
    reads {
        sq_md.curserver: exact;
    }
    actions {
        act_rewrite_iface;
        _drop;
    }
    default_action : _drop;
}

control ingress {
    if (valid(sq)) {
        if (sq.op_type == TYPE_REQ) {
            apply(get_counter_idx);
            apply(exe_curserver);
            apply(send_to_curserver);
        }
        else{
            apply(ipv4_route);
        }
    }
    else {
        apply(ipv4_route);
    }
}

control egress {
    apply(set_mac);
}
