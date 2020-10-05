#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "../includes/constants.p4"
#include "../includes/headers.p4"
#include "../includes/parsers.p4"
#include "../includes/ipv4_route.p4"

#define HOSTID_1 0
#define HOSTID_2 1
#define HOSTID_3 2
#define HOSTID_4 3
#define HOSTID_5 4
#define HOSTID_6 5
#define HOSTID_7 6
#define HOSTID_8 7

#include "qlen_proac/qlen1.p4"
#include "qlen_proac/qlen2.p4"
#include "qlen_proac/qlen3.p4"
#include "qlen_proac/qlen4.p4"
#include "qlen_proac/qlen5.p4"
#include "qlen_proac/qlen6.p4"
#include "qlen_proac/qlen7.p4"
#include "qlen_proac/qlen8.p4"

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
        min12 : 32;
        min34 : 32;
        min56 : 32;
        min78 : 32;
        min1234: 32;
        min5678 : 32;
        minall : 32;
        min12_idx : 1;
        min34_idx : 1;
        min56_idx : 1;
        min78_idx : 1;
        min1234_idx: 1;
        min5678_idx : 1;
        minall_idx : 1;
        counter_idx : 8;
        sq_server : 3;
        resubmit_flag : 1;
        is_min1 : 1;
        is_min2 : 1;
        is_min3 : 1;
        is_min4 : 1;
        is_min5 : 1;
        is_min6 : 1;
        is_min7 : 1;
        is_min8 : 1;
        is_random : RANDOM_BASE;
    }
}

metadata sq_metadata_t sq_md;

action act_calc_minpair() {
    min(sq_md.min12, sq_md.qlen1, sq_md.qlen2);
    min(sq_md.min34, sq_md.qlen3, sq_md.qlen4);
    min(sq_md.min56, sq_md.qlen5, sq_md.qlen6);
    min(sq_md.min78, sq_md.qlen7, sq_md.qlen8);
}

table calc_minpair {
    actions {act_calc_minpair;}
    default_action : act_calc_minpair();
}

action act_calc_minquarter() {
    min(sq_md.min1234, sq_md.min12, sq_md.min34);
    min(sq_md.min5678, sq_md.min56, sq_md.min78);
}

table calc_minquarter {
    actions {act_calc_minquarter;}
    default_action : act_calc_minquarter();
}

action act_calc_minall() {
    min(sq_md.minall, sq_md.min1234, sq_md.min5678);
}

table calc_minall {
    actions {act_calc_minall;}
    default_action : act_calc_minall();
}

table send_to_curserver {
    reads {
        sq_md.sq_server: exact;
    }
    actions {
        act_rewrite_iface;
    }
}

action act_modify_resubmit_flag() {
    modify_field(sq_md.resubmit_flag, 1);
}

table modify_resubmit_flag {
    actions {act_modify_resubmit_flag;}
    default_action : act_modify_resubmit_flag();
}

field_list e2e_mirror_info {
    sq_md.sq_server;
    sq_md.resubmit_flag;
}

action act_resubmit() {
    resubmit(e2e_mirror_info);
}

table resubmit_pkt {
    actions {act_resubmit;}
    default_action : act_resubmit();
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

action act_random_12() {
    modify_field_rng_uniform(sq_md.min12_idx, 0, 1);
}

table random_12{
    actions {act_random_12;}
    default_action: act_random_12();
}

action act_min12_1() {
    modify_field(sq_md.min12_idx, 0);
}

table min12_1{
    actions {act_min12_1;}
    default_action: act_min12_1();
}

action act_min12_2() {
    modify_field(sq_md.min12_idx, 1);
}

table min12_2{
    actions {act_min12_2;}
    default_action: act_min12_2();
}

action act_random_34() {
    modify_field_rng_uniform(sq_md.min34_idx, 0, 1);
}

table random_34{
    actions {act_random_34;}
    default_action: act_random_34();
}

action act_min34_3() {
    modify_field(sq_md.min34_idx, 0);
}

table min34_3{
    actions {act_min34_3;}
    default_action: act_min34_3();
}

action act_min34_4() {
    modify_field(sq_md.min34_idx, 1);
}

table min34_4{
    actions {act_min34_4;}
    default_action: act_min34_4();
}

action act_random_56() {
    modify_field_rng_uniform(sq_md.min56_idx, 0, 1);
}

table random_56{
    actions {act_random_56;}
    default_action: act_random_56();
}

action act_min56_5() {
    modify_field(sq_md.min56_idx, 0);
}

table min56_5{
    actions {act_min56_5;}
    default_action: act_min56_5();
}

action act_min56_6() {
    modify_field(sq_md.min56_idx, 1);
}

table min56_6{
    actions {act_min56_6;}
    default_action: act_min56_6();
}

action act_random_78() {
    modify_field_rng_uniform(sq_md.min78_idx, 0, 1);
}

table random_78{
    actions {act_random_78;}
    default_action: act_random_78();
}

action act_min78_7() {
    modify_field(sq_md.min78_idx, 0);
}

table min78_7{
    actions {act_min78_7;}
    default_action: act_min78_7();
}

action act_min78_8() {
    modify_field(sq_md.min78_idx, 1);
}

table min78_8{
    actions {act_min78_8;}
    default_action: act_min78_8();
}

action act_random_1234_5678() {
    modify_field_rng_uniform(sq_md.minall_idx, 0, 1);
}

table random_1234_5678{
    actions {act_random_1234_5678;}
    default_action: act_random_1234_5678();
}

action act_random_1234() {
    modify_field_rng_uniform(sq_md.min1234_idx, 0, 1);
}

table random_1234{
    actions {act_random_1234;}
    default_action: act_random_1234();
}

action act_random_5678() {
    modify_field_rng_uniform(sq_md.min5678_idx, 0, 1);
}

table random_5678{
    actions {act_random_5678;}
    default_action: act_random_5678();
}

action act_min1234_12() {
    modify_field(sq_md.min1234_idx,0);
}

table min1234_12 {
    actions {act_min1234_12;}
    default_action: act_min1234_12();
}

action act_min1234_34() {
    modify_field(sq_md.min1234_idx,1);
}

table min1234_34 {
    actions {act_min1234_34;}
    default_action: act_min1234_34();
}

action act_min5678_56() {
    modify_field(sq_md.min5678_idx,0);
}

table min5678_56 {
    actions {act_min5678_56;}
    default_action: act_min5678_56();
}

action act_min5678_78() {
    modify_field(sq_md.min5678_idx,1);
}

table min5678_78 {
    actions {act_min5678_78;}
    default_action: act_min5678_78();
}

action act_minall_1234() {
    modify_field(sq_md.minall_idx,0);
}

table minall_1234 {
    actions {act_minall_1234;}
    default_action: act_minall_1234();
}

action act_minall_5678() {
    modify_field(sq_md.minall_idx,1);
}

table minall_5678 {
    actions {act_minall_5678;}
    default_action: act_minall_5678();
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

control ingress {
    if (valid(sq)) {
        if (sq.op_type == TYPE_REQ) {
            apply(get_counter_idx);
            apply(gen_is_random);
            if (sq_md.is_random == 1) {
                apply(gen_random_server);
                apply(send_to_curserver);
            }
            else {
                // QUERY,first time, find the server with the shortest-queue
                if (sq_md.resubmit_flag==0) {
                    apply(read_qlen1);
                    apply(read_qlen2);
                    apply(read_qlen3);
                    apply(read_qlen4);
                    apply(read_qlen5);
                    apply(read_qlen6);
                    apply(read_qlen7);
                    apply(read_qlen8);

                    apply(calc_minpair);
                    apply(calc_minquarter);
                    apply(calc_minall);

                    if (sq_md.min1234 == sq_md.min5678) {
                        apply(random_1234_5678);
                    }
                    else if (sq_md.min1234 == sq_md.minall) {
                        apply(minall_1234);
                    }
                    else {
                        apply(minall_5678);
                    }
                    if (sq_md.minall_idx == 0) {
                        // go to 1234
                        if (sq_md.min12 == sq_md.min34) {
                            apply(random_1234);
                        }
                        else if (sq_md.min12 == sq_md.min1234) {
                            apply(min1234_12);
                        }
                        else{
                            apply(min1234_34);
                        }
                        if (sq_md.min1234_idx == 0) {
                            // go to 12
                            if (sq_md.qlen1==sq_md.qlen2) {
                                apply(random_12);
                            }
                            else if (sq_md.qlen1 == sq_md.min12) {
                                apply(min12_1);
                            }
                            else {
                                apply(min12_2);
                            }
                            if (sq_md.min12_idx == 0) {
                                apply(set_min1);
                            }
                            else {
                                apply(set_min2);
                            }

                        }
                        else{
                            // go to 34
                            if (sq_md.qlen3==sq_md.qlen4) {
                                apply(random_34);
                            }
                            else if (sq_md.qlen3 == sq_md.min34) {
                                apply(min34_3);
                            }
                            else {
                                apply(min34_4);
                            }
                            if (sq_md.min34_idx == 0) {
                                apply(set_min3);
                            }
                            else {
                                apply(set_min4);
                            }
                        }
                    }
                    else {
                        // go to 5678
                        if (sq_md.min56 == sq_md.min78) {
                            apply(random_5678);
                        }
                        else if (sq_md.min56 == sq_md.min5678) {
                            apply(min5678_56);
                        }
                        else{
                            apply(min5678_78);
                        }
                        if (sq_md.min5678_idx == 0) {
                            // go to 56
                            if (sq_md.qlen5==sq_md.qlen6) {
                                apply(random_56);
                            }
                            else if (sq_md.qlen5 == sq_md.min56) {
                                apply(min56_5);
                            }
                            else {
                                apply(min56_6);
                            }
                            if (sq_md.min56_idx == 0) {
                                apply(set_min5);
                            }
                            else {
                                apply(set_min6);
                            }
                        }
                        else{
                            // go to 78
                            if (sq_md.qlen7==sq_md.qlen8) {
                                apply(random_78);
                            }
                            else if (sq_md.qlen7 == sq_md.min78) {
                                apply(min78_7);
                            }
                            else {
                                apply(min78_8);
                            }
                            if (sq_md.min78_idx == 0) {
                                apply(set_min7);
                            }
                            else {
                                apply(set_min8);
                            }
                        }
                    }
                    //resubmit this packet
                    apply(modify_resubmit_flag);
                    apply(resubmit_pkt);
                }
                // QUERY, second time, increase the shortest-queue counter by 1
                else {
                    apply(inc_qlen1);
                    apply(inc_qlen2);
                    apply(inc_qlen3);
                    apply(inc_qlen4);
                    apply(inc_qlen5);
                    apply(inc_qlen6);
                    apply(inc_qlen7);
                    apply(inc_qlen8);
                    apply(send_to_curserver);
                }
            }

        }
        // QUERY_REPLY
        else {
            apply(get_counter_idx_reply);
            apply(dcr_qlen1);
            apply(dcr_qlen2);
            apply(dcr_qlen3);
            apply(dcr_qlen4);
            apply(dcr_qlen5);
            apply(dcr_qlen6);
            apply(dcr_qlen7);
            apply(dcr_qlen8);
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
