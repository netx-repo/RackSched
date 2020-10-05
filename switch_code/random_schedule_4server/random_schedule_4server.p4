#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#include "../includes/parsers.p4"
#include "../includes/ipv4_route.p4"

#define RNDSERVER_SIZE_4SERVER 2
#define RND_SIZE_4SERVER 3

header_type sq_metadata_t {
    fields {
        random_server : RNDSERVER_SIZE_4SERVER;
        server_num : 3;
    }
}

metadata sq_metadata_t sq_md;

// produce random int between [0, RND_SIZE]
action act_gen_random_server() {
    modify_field_rng_uniform(sq_md.random_server, 0, RND_SIZE_4SERVER);
}

table gen_random_server {
    actions {act_gen_random_server;}
    default_action : act_gen_random_server;
}

table send_to_curserver {
    reads {
        sq_md.random_server: exact;
    }
    actions {
        act_rewrite_iface;
        _drop;
    }
    default_action : _drop;
}

action act_adjust_randomserver4() {
    shift_right(sq_md.random_server, sq_md.random_server, 1);
}

table adjust_randomserver4 {
    actions {act_adjust_randomserver4;}
}

action act_adjust_randomserver2() {
    shift_right(sq_md.random_server, sq_md.random_server, 2);
}

table adjust_randomserver2 {
    actions {act_adjust_randomserver2;}
}

action act_adjust_randomserver1() {
    shift_right(sq_md.random_server, sq_md.random_server, 3);
}

table adjust_randomserver1 {
    actions {act_adjust_randomserver1;}
}

action act_set_servernum(server_num) {
    modify_field(sq_md.server_num, server_num);
}

table set_servernum {
    actions {act_set_servernum;}
}

control ingress {
    if (valid(sq)) {
        if (sq.op_type == TYPE_REQ) {
            apply(gen_random_server);
            apply(set_servernum);
            apply(send_to_curserver);
        }
        else {
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
