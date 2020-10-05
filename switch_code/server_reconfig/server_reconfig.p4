#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#define FAILURE
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

#include "ht/ht1.p4"
#include "ht/ht2.p4"
#include "ht/ht3.p4"

#include "rand_sample.p4"
// #include "adapt.p4"
#define SERVER_NUM 8
#define SERVER_NUM_POW 3

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
        sq_server : 4;
        hash_sq_server : 4;
        random_server1 : RNDSERVER_SIZE;
        random_server2 : RNDSERVER_SIZE;
        qlen_random1 : 32;
        qlen_random2 : 32;
        min_random_qlen : 32;
        is_random : RANDOM_BASE;
        serverid : 3;
        server_num : 4;
        stored_server : 1;
        req_id : 32;
        hash_int : 15;
    }
}

metadata sq_metadata_t sq_md;

field_list sq_hash_field {
    sq_md.req_id;
}

table send_to_curserver {
    reads {
        sq_md.sq_server: exact;
    }
    actions {
        act_rewrite_iface;
    }
}

// server ID from 0
table send_to_curserver_from0 {
    reads {
        sq_md.hash_sq_server: exact;
    }
    actions {
        act_rewrite_iface;
    }
}

table send_to_rand_server {
    reads {
        sq_md.random_server1: exact;
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

action act_set_servernum(servernum) {
    modify_field(sq_md.server_num, servernum);
}

table set_servernum {
    actions {
        act_set_servernum;
    }
}

field_list_calculation hash_select {
    input {sq_hash_field;}
    algorithm : crc_16_dect;
    output_width : SERVER_NUM_POW;
}

action act_hash_select_server() {
    modify_field_with_hash_based_offset(sq_md.hash_sq_server, 0, hash_select, SERVER_NUM);
}

table hash_select_server {
    actions {act_hash_select_server;}
    default_action : act_hash_select_server();
}

field_list_calculation hash_select_random7 {
    input {sq_hash_field;}
    algorithm : crc_16_dect;
    output_width : 15;
}

action act_gen_hash_int() {
    modify_field_with_hash_based_offset(sq_md.hash_int, 0, hash_select_random7, 32768);
}

table gen_hash_int {
    actions {act_gen_hash_int;}
    default_action : act_gen_hash_int();
}

action act_assign_hash_int_to_random_7(random_num) {
    modify_field(sq_md.hash_sq_server, random_num);
}

table hash_int_to_random_7 {
    reads {
        sq_md.hash_int: range;
    }
    actions {
        act_assign_hash_int_to_random_7;
        drop_packet;
    }
    default_action: drop_packet();
}

action act_sq_reqid_md() {
    modify_field(sq_md.req_id, sq.req_id);
}

table sq_reqid_md {
    actions {act_sq_reqid_md;}
    default_action : act_sq_reqid_md();
}

action act_sqreply_reqid_md() {
    modify_field(sq_md.req_id, sq_reply.req_id);
}

table sqreply_reqid_md {
    actions {act_sqreply_reqid_md;}
    default_action : act_sqreply_reqid_md();
}

register drop_counter {
    width : 64;
    instance_count : 1;
}

blackbox stateful_alu salu_drop_counter {
    reg : drop_counter;
    update_lo_1_value: register_lo + 1;
}

action act_drop_counter() {
    salu_drop_counter.execute_stateful_alu(0);
}

table count_drop {
    actions {act_drop_counter;}
    default_action : act_drop_counter();
}

control ingress {
    if (valid(sq)) {
        apply(sq_reqid_md);
        apply(set_servernum);
        if (sq.op_type == TYPE_REQ) {
            apply(get_counter_idx);
            apply(read_qlen1);
            apply(read_qlen2);
            apply(read_qlen3);
            apply(read_qlen4);
            apply(read_qlen5);
            apply(read_qlen6);
            apply(read_qlen7);
            apply(read_qlen8);
            if (sq_md.server_num==8) {
                // sample two random servers from [0,7]
                apply(gen_random_server1);
                apply(gen_random_server2);
            }
            else if (sq_md.server_num==7) {
                apply(gen_random_int);
                apply(int1_to_random_7);
                apply(int2_to_random_7);
            }
            if (sq_md.random_server1 == sq_md.random_server2) {
                apply(assign_curserver_random1);
            }
            else {
                apply(assign_qlen_random1);
                apply(assign_qlen_random2);
                apply(cmp_random_qlen);

                if (sq_md.min_random_qlen == sq_md.qlen_random1) {
                    apply(assign_curserver_random1);
                }
                else {
                    apply(assign_curserver_random2);
                }
            }
            // try to write to hash table
            apply(write_sq_ht1);

            if (sq_md.stored_server == 0) {
                // hash-based
                apply(count_drop);
                apply(hash_select_server);
                // if (sq_md.server_num==8) {
                //     apply(hash_select_server);
                // }
                // if (sq_md.server_num==7) {
                //     apply(gen_hash_int);
                //     apply(hash_int_to_random_7);
                // }
                // apply(send_to_curserver_from0);
                apply(drop_pkt);
            }
            else {
                apply(send_to_curserver);
            }
        }
        else if (sq.op_type == TYPE_REQ_FOLLOW) {
            // the following pkt in a request
            apply(read_sq_ht1);
            if (sq_md.sq_server == 0) {
                // hash-based
                // apply(count_drop);
                // apply(hash_select_server);
                // if (sq_md.server_num==8) {
                //     apply(hash_select_server);
                // }
                // else if (sq_md.server_num==7) {
                //     apply(gen_hash_int);
                //     apply(hash_int_to_random_7);
                // }
                // apply(send_to_curserver_from0);
                apply(drop_pkt);
            }
            else {
                apply(send_to_curserver);
            }
        }
    }
    else if (valid(sq_reply)) {
        // QUERY_REPLY
        apply(sqreply_reqid_md);
        apply(get_counter_idx_reply);
        apply(update_qlen1);
        apply(update_qlen2);
        apply(update_qlen3);
        apply(update_qlen4);
        apply(update_qlen5);
        apply(update_qlen6);
        apply(update_qlen7);
        apply(update_qlen8);

        // reset the ht
        apply(reset_sq_ht1);
        // apply(reset_sq_ht2);
        // apply(reset_sq_ht3);
        apply(ipv4_route);
    }
    else {
        apply(ipv4_route);
    }
}

control egress {
    apply(set_mac);
}
