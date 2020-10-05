#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#include "../includes/parsers.p4"
#include "../includes/ipv4_route.p4"

#include "../qlen/qlen1.p4"
#include "../qlen/qlen2.p4"
#include "../qlen/qlen3.p4"
#include "../qlen/qlen4.p4"
#include "../qlen/qlen5.p4"
#include "../qlen/qlen6.p4"
#include "../qlen/qlen7.p4"
#include "../qlen/qlen8.p4"

#include "po4.p4"

header_type sq_metadata_t {
    fields {
        qlen1 : 32;
        qlen2 : 32;
        qlen3 : 32;
        qlen4 : 32;
        qlen5 : 32;
        qlen6 : 32;
        qlen7 : 32;
        qlen8 : 32;
        counter_idx : 8;
        sq_server : 3;
        random_server1 : 3;
        random_server2 : 3;
        random_server3 : 3;
        random_server4 : 3;
        qlen_random1 : 32;
        qlen_random2 : 32;
        qlen_random3 : 32;
        qlen_random4 : 32;
        min_random_qlen_all : 32;
        min_random_qlen12 : 32;
        min_random_qlen34 : 32;
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
        // _drop;
    }
    // default_action : _drop;
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
action act_gen_random_server1() {
    // modify_field_rng_uniform(sq_md.random_server, 0, RND_SIZE8);
    modify_field_rng_uniform(sq_md.random_server1, 0, RND_SIZE);
}

table gen_random_server1 {
    actions {act_gen_random_server1;}
    default_action : act_gen_random_server1();
}

// produce random int between [0, RND_SIZE]
action act_gen_random_server2() {
    // modify_field_rng_uniform(sq_md.random_server, 0, RND_SIZE8);
    modify_field_rng_uniform(sq_md.random_server2, 0, RND_SIZE);
}

table gen_random_server2 {
    actions {act_gen_random_server2;}
    default_action : act_gen_random_server2();
}

action act_gen_random_server3() {
    // modify_field_rng_uniform(sq_md.random_server, 0, RND_SIZE8);
    modify_field_rng_uniform(sq_md.random_server3, 0, RND_SIZE);
}

table gen_random_server3 {
    actions {act_gen_random_server3;}
    default_action : act_gen_random_server3();
}

action act_gen_random_server4() {
    // modify_field_rng_uniform(sq_md.random_server, 0, RND_SIZE8);
    modify_field_rng_uniform(sq_md.random_server4, 0, RND_SIZE);
}

table gen_random_server4 {
    actions {act_gen_random_server4;}
    default_action : act_gen_random_server4();
}

control ingress {
    if (valid(sq)) {
        apply(get_counter_idx);
        apply(gen_random_server1);
        apply(gen_random_server2);
        apply(gen_random_server3);
        apply(gen_random_server4);
        apply(read_qlen1);
        apply(read_qlen2);
        apply(read_qlen3);
        apply(read_qlen4);
        apply(read_qlen5);
        apply(read_qlen6);
        apply(read_qlen7);
        apply(read_qlen8);

        apply(assign_random1);
        apply(assign_random2);
        apply(assign_random3);
        apply(assign_random4);

        apply(cmp_random_qlen_pair);
        apply(cmp_random_qlen_all);

        if (sq_md.min_random_qlen_all == sq_md.qlen_random1) {
            apply(assign_curserver_random1);
        }
        else if (sq_md.min_random_qlen_all == sq_md.qlen_random2) {
            apply(assign_curserver_random2);
        }
        else if (sq_md.min_random_qlen_all == sq_md.qlen_random3) {
            apply(assign_curserver_random3);
        }
        else if (sq_md.min_random_qlen_all == sq_md.qlen_random4) {
            apply(assign_curserver_random4);
        }
        apply(send_to_curserver);

    }
    else if (valid(sq_reply)) {
        // QUERY_REPLY
        apply(get_counter_idx_reply);
        apply(update_qlen1);
        apply(update_qlen2);
        apply(update_qlen3);
        apply(update_qlen4);
        apply(update_qlen5);
        apply(update_qlen6);
        apply(update_qlen7);
        apply(update_qlen8);
        apply(ipv4_route);
    }
    else {
        apply(ipv4_route);
    }
}

control egress {
    apply(set_mac);
}
