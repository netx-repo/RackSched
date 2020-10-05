#include <tofino/constants.p4>
#include <tofino/intrinsic_metadata.p4>
#include <tofino/primitives.p4>
#include <tofino/stateful_alu_blackbox.p4>

#include "includes/constants.p4"
#include "includes/headers.p4"
#include "includes/parsers.p4"
#include "includes/ipv4_route.p4"

#include "stful_r2p2/qlen1.p4"
#include "stful_r2p2/qlen2.p4"
#include "stful_r2p2/qlen3.p4"
#include "stful_r2p2/qlen4.p4"
#include "stful_r2p2/qlen5.p4"
#include "stful_r2p2/qlen6.p4"
#include "stful_r2p2/qlen7.p4"
#include "stful_r2p2/qlen8.p4"

#include "utils.p4"

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
        sq_server : 3;
        is_random : RANDOM_BASE;
        serverid : 3;
        jbsqn : 8;
        round_idx : 8;
        core_idx : 8;
        to_qlen1 : 1;
        to_qlen2 : 1;
        to_qlen3 : 1;
        to_qlen4 : 1;
        to_qlen5 : 1;
        to_qlen6 : 1;
        to_qlen7 : 1;
        to_qlen8 : 1;
        smaller_jbsqn : 1;
        curserver : 3;
        used_for_shift: 8;
    }
}

metadata sq_metadata_t sq_md;

action act_set_vfip(iface, dip, dmac) {
    modify_field(ig_intr_md_for_tm.ucast_egress_port,iface);
    modify_field(ipv4.dstAddr, dip);
    modify_field(ethernet.dstAddr, dmac);
}

table send_to_curserver {
    reads {
        sq_md.curserver: exact;
        sq_md.core_idx: exact;
    }
    actions {
        act_set_vfip;
        // _drop;
    }
    // default_action : _drop;
}

// for debugging
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
    default_action : act_drop_counter;
}

control ingress {
    if (valid(sq)) {
        if (valid(recir)) {
            // recirculated pkt
            apply(prepare_md);
        }
        else {
            // the first pass for a request
            apply(rr_select_core_idx);

        }
        apply(read_jbsqn);

        apply(update_qlen1);
        if (sq_md.to_qlen1 == 0) {
            apply(update_qlen2);
            if (sq_md.to_qlen2 == 0) {
                apply(update_qlen3);
                if (sq_md.to_qlen3 == 0) {
                    apply(update_qlen4);
                    if (sq_md.to_qlen4 == 0) {
                        apply(update_qlen5);
                        if (sq_md.to_qlen5 == 0) {
                            apply(update_qlen6);
                            if (sq_md.to_qlen6 == 0) {
                                apply(update_qlen7);
                                if (sq_md.to_qlen7 == 0) {
                                    apply(update_qlen8);
                                }
                            }
                        }
                    }
                }
            }
        }
        if (sq_md.to_qlen1 == 1) {
            apply(send_server1);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen2 == 1) {
            apply(send_server2);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen3 == 1) {
            apply(send_server3);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen4 == 1) {
            apply(send_server4);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen5 == 1) {
            apply(send_server5);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen6 == 1) {
            apply(send_server6);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen7 == 1) {
            apply(send_server7);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else if (sq_md.to_qlen8 == 1) {
            apply(send_server8);
            if (valid(recir)) {
                apply(remove_recir);
            }
            apply(send_to_curserver);
        }
        else {
            // no valid servers, recirculate
            if (sq_md.smaller_jbsqn == 1) {
                apply(incr_round_idx);
            }
            if (valid(recir)) {
                apply(mod_hdr_round_idx);
            }
            else {
                apply(prepare_recir);
            }
            apply(recir_pkt);
        }

    }
    else if (valid(sq_reply)) {
        // QUERY_REPLY
        // apply(count_drop);
        // apply(assign_util);
        // apply(shift_core_idx);
        apply(dcr_qlen1);
        apply(dcr_qlen2);
        apply(dcr_qlen3);
        apply(dcr_qlen4);
        apply(dcr_qlen5);
        apply(dcr_qlen6);
        apply(dcr_qlen7);
        apply(dcr_qlen8);

        apply(ipv4_route);
        apply(set_mac);

    }

    else {
        apply(ipv4_route);
        apply(set_mac);
    }
}

control egress {
    // apply(set_mac);
}
