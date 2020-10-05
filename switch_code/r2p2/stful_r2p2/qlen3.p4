register server_qlen3 {
    width : 64;
    instance_count : CORE_NUM;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_update_qlen3 {
    reg : server_qlen3;

    condition_lo : register_lo <= sq_md.round_idx;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;

    output_predicate : condition_lo;
    output_value : combined_predicate;
    output_dst : sq_md.to_qlen3;
}

action act_update_qlen3() {
    salu_update_qlen3.execute_stateful_alu(sq_md.core_idx);
}

table update_qlen3 {
    actions {act_update_qlen3;}
    default_action : act_update_qlen3();
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen3 {
    reg : server_qlen3;

    condition_lo : ipv4.srcAddr == HOSTIP_3;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen3() {
    salu_dcr_qlen3.execute_stateful_alu(sq_reply.core_idx);
}

@pragma stage 3
table dcr_qlen3 {
    actions {act_dcr_qlen3;}
    default_action : act_dcr_qlen3();
}

action act_send_server3() {
    modify_field(sq_md.curserver,HOSTID_3);
}

table send_server3 {
    actions {act_send_server3;}
    default_action : act_send_server3();
}
