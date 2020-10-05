#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#include "../includes/parsers.p4"
#include "../includes/ipv4_route.p4"

#define SERVER_NUM 8
#define SERVER_NUM_POW 3

#include "../qlen/qlen1.p4"
#include "../qlen/qlen2.p4"
#include "../qlen/qlen3.p4"
#include "../qlen/qlen4.p4"
#include "../qlen/qlen5.p4"
#include "../qlen/qlen6.p4"
#include "../qlen/qlen7.p4"
#include "../qlen/qlen8.p4"

#include "../po2.p4"

#include "../ht/ht1.p4"
#include "../ht/ht2.p4"
#include "../ht/ht3.p4"
#include "failure.p4"

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
        random_server1 : RNDSERVER_SIZE;
        random_server2 : RNDSERVER_SIZE;
        qlen_random1 : 32;
        qlen_random2 : 32;
        min_random_qlen : 32;
        is_random : RANDOM_BASE;
        stored_server : 1;
        req_id : 32;
        status : 1;
    }
}

metadata sq_metadata_t sq_md;

field_list sq_hash_field {
    sq.req_id;
}

field_list sq_reply_hash_field {
    sq_reply.req_id;
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

field_list_calculation hash_select {
    input {sq_hash_field;}
    algorithm : crc_16_dect;
    output_width : SERVER_NUM_POW;
}

action act_hash_select_server() {
    modify_field_with_hash_based_offset(sq_md.sq_server, 0, hash_select, SERVER_NUM);
}

table hash_select_server {
    actions {act_hash_select_server;}
    default_action : act_hash_select_server();
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
    apply(sim_fail);
    if (sq_md.status == SIM_WORK) {
        if (valid(sq)) {
            apply(sq_reqid_md);
            if (sq.op_type == TYPE_REQ) {
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

                    apply(cmp_random_qlen);

                    if (sq_md.min_random_qlen == sq_md.qlen_random1) {
                        apply(assign_curserver_random1);
                    }
                    else {
                        apply(assign_curserver_random2);
                    }
                }
                // ReqTable
                apply(write_sq_ht1);
                if (sq_md.stored_server == 0) {
                    apply(write_sq_ht2);
                    if (sq_md.stored_server == 0) {
                        apply(write_sq_ht3);
                    }
                }
                if (sq_md.stored_server == 0) {
                    // hash-based
                    apply(count_drop);
                    apply(hash_select_server);
                    // apply(hash_server_rectify);
                    apply(send_to_curserver_from0);
                    // apply(drop_pkt);
                }
                else {
                    apply(send_to_curserver);
                }
            }
            else if (sq.op_type == TYPE_REQ_FOLLOW) {
                // the following pkt in a request
                apply(read_sq_ht1);
                if (sq_md.sq_server == 0) {
                    apply(read_sq_ht2);
                    if (sq_md.sq_server == 0) {
                        apply(read_sq_ht3);
                    }
                }
                if (sq_md.sq_server == 0) {
                    // hash-based
                    apply(count_drop);
                    apply(hash_select_server);
                    // apply(hash_server_rectify);
                    apply(send_to_curserver_from0);
                    // apply(drop_pkt);
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

            // reset the ReqTable
            apply(reset_sq_ht1);
            apply(reset_sq_ht2);
            apply(reset_sq_ht3);
            apply(ipv4_route);
        }
        else {
            apply(ipv4_route);
        }
    }

}

control egress {
    if (sq_md.status == SIM_WORK) {
        apply(set_mac);
    }
}
