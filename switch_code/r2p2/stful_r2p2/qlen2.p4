register server_qlen2 {
    width : 64;
    instance_count : CORE_NUM;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_update_qlen2 {
    reg : server_qlen2;

    condition_lo : register_lo <= sq_md.round_idx;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;

    output_predicate : condition_lo;
    output_value : combined_predicate;
    output_dst : sq_md.to_qlen2;
}

action act_update_qlen2() {
    salu_update_qlen2.execute_stateful_alu(sq_md.core_idx);
}

table update_qlen2 {
    actions {act_update_qlen2;}
    default_action : act_update_qlen2();
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen2 {
    reg : server_qlen2;

    condition_lo : ipv4.srcAddr == HOSTIP_2;
    // condition_lo : ig_intr_md.ingress_port == INGRESS_PORT_2;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen2() {
    salu_dcr_qlen2.execute_stateful_alu(sq_reply.core_idx);
}

@pragma stage 2
table dcr_qlen2 {
    actions {act_dcr_qlen2;}
    default_action : act_dcr_qlen2();
}

action act_send_server2() {
    modify_field(sq_md.curserver,HOSTID_2);
}

table send_server2 {
    actions {act_send_server2;}
    default_action : act_send_server2();
}
