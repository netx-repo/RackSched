#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#include "../includes/parsers.p4"
#include "../includes/ipv4_route.p4"

#include "lowest_load.p4"

header_type sq_metadata_t {
    fields {
        counter_idx : 8;
        sq_server : 3;
        curserver : 8;
        resubmit_flag : 1;
        is_random : RANDOM_BASE;
    }
}

metadata sq_metadata_t sq_md;

table send_to_curserver {
    reads {
        sq_md.sq_server: exact;
    }
    actions {
        act_rewrite_iface;
    }
}

action act_get_counter_idx() {
    subtract(sq_md.counter_idx, PORT_OFFSET, udp.dstPort);
}

table get_counter_idx {
    actions {act_get_counter_idx;}
    default_action : act_get_counter_idx();
}

action act_get_counter_idx_reply() {
    subtract(sq_md.counter_idx, PORT_OFFSET, udp.srcPort);
}

table get_counter_idx_reply {
    actions {act_get_counter_idx_reply;}
    default_action : act_get_counter_idx_reply();
}

// produce random int between [0, RND_SIZE]
action act_gen_random_server() {
    // modify_field_rng_uniform(sq_md.random_server, 0, RND_SIZE8);
    modify_field_rng_uniform(sq_md.sq_server, 0, RND_SIZE);
}

table gen_random_server {
    actions {act_gen_random_server;}
    default_action : act_gen_random_server();
}

action act_gen_is_random() {
    modify_field_rng_uniform(sq_md.is_random, 0, RANDOM_BASE_MAX);
}

table gen_is_random{
    actions {act_gen_is_random;}
    default_action : act_gen_is_random();
}

action act_get_curserver(serverID) {
    modify_field(sq_md.curserver,serverID);
}

table get_curserver {
    reads {
        ipv4.srcAddr : exact;
    }
    actions {
        act_get_curserver;
    }
}

control ingress {
    if (valid(sq)) {
        if (sq.op_type == TYPE_REQ) {
            apply(get_counter_idx);
            apply(gen_is_random);
            if (sq_md.is_random == 1) {
                apply(gen_random_server);
            }
            else {
                apply(read_llserver);
            }
            apply(send_to_curserver);

        }

    }
    else if (valid(sq_reply)) {
        // QUERY_REPLY
        apply(get_counter_idx_reply);
        apply(get_curserver);
        apply(update_llserver);
        apply(ipv4_route);
    }
    else {
        apply(ipv4_route);
    }
}

control egress {
    apply(set_mac);
}
