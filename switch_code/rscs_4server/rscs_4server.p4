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

#include "../po2.p4"

// override the two constants
#define RNDSERVER_SIZE_4SERVER 2
#define RND_SIZE_4SERVER 3

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
        random_server1 : RNDSERVER_SIZE_4SERVER;
        random_server2 : RNDSERVER_SIZE_4SERVER;
        qlen_random1 : 32;
        qlen_random2 : 32;
        min_random_qlen : 32;
        is_random : RANDOM_BASE;
        serverid : 3;
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
action act_gen_random_server1() {
    modify_field_rng_uniform(sq_md.random_server1, 0, RND_SIZE_4SERVER);
}

table gen_random_server1 {
    actions {act_gen_random_server1;}
    default_action : act_gen_random_server1();
}

// produce random int between [0, RND_SIZE]
action act_gen_random_server2() {
    modify_field_rng_uniform(sq_md.random_server2, 0, RND_SIZE_4SERVER);
}

table gen_random_server2 {
    actions {act_gen_random_server2;}
    default_action : act_gen_random_server2();
}

control ingress {
    if (valid(sq)) {
        apply(get_counter_idx);
        apply(gen_random_server1);
        apply(gen_random_server2);
        if (sq_md.random_server1 == sq_md.random_server2) {
            apply(assign_curserver_random1);
        }
        else {
            apply(read_qlen1);
            apply(read_qlen2);
            apply(read_qlen3);
            apply(read_qlen4);
            apply(read_qlen5);
            apply(read_qlen6);
            apply(read_qlen7);
            apply(read_qlen8);

            apply(assign_qlen_random1);
            apply(assign_qlen_random2);
            // if (sq_md.random_server1==0) {
            //     apply(random1_qlen1);
            // }
            // else if (sq_md.random_server1==1) {
            //     apply(random1_qlen2);
            // }
            // else if (sq_md.random_server1==2) {
            //     apply(random1_qlen3);
            // }
            // else if (sq_md.random_server1==3) {
            //     apply(random1_qlen4);
            // }
            // else if (sq_md.random_server1==4) {
            //     apply(random1_qlen5);
            // }
            // else if (sq_md.random_server1==5) {
            //     apply(random1_qlen6);
            // }
            // else if (sq_md.random_server1==6) {
            //     apply(random1_qlen7);
            // }
            // else if (sq_md.random_server1==7) {
            //     apply(random1_qlen8);
            // }
            //
            // if (sq_md.random_server2==0) {
            //     apply(random2_qlen1);
            // }
            // else if (sq_md.random_server2==1) {
            //     apply(random2_qlen2);
            // }
            // else if (sq_md.random_server2==2) {
            //     apply(random2_qlen3);
            // }
            // else if (sq_md.random_server2==3) {
            //     apply(random2_qlen4);
            // }
            // else if (sq_md.random_server2==4) {
            //     apply(random2_qlen5);
            // }
            // else if (sq_md.random_server2==5) {
            //     apply(random2_qlen6);
            // }
            // else if (sq_md.random_server2==6) {
            //     apply(random2_qlen7);
            // }
            // else if (sq_md.random_server2==7) {
            //     apply(random2_qlen8);
            // }
            apply(cmp_random_qlen);

            if (sq_md.min_random_qlen == sq_md.qlen_random1) {
                apply(assign_curserver_random1);
            }
            else {
                apply(assign_curserver_random2);
            }
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
