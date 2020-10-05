register server_qlen1 {
    width : 64;
    instance_count : CORE_NUM;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_update_qlen1 {
    reg : server_qlen1;

    condition_lo : register_lo <= sq_md.round_idx;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;

    output_predicate : condition_lo;
    output_value : combined_predicate;
    output_dst : sq_md.to_qlen1;
}

action act_update_qlen1() {
    salu_update_qlen1.execute_stateful_alu(sq_md.core_idx);
}

@pragma stage 1
table update_qlen1 {
    actions {act_update_qlen1;}
    default_action : act_update_qlen1();
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen1 {
    reg : server_qlen1;

    condition_lo : ipv4.srcAddr == HOSTIP_1;
    // condition_lo : ig_intr_md.ingress_port == INGRESS_PORT_1;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen1() {
    salu_dcr_qlen1.execute_stateful_alu(sq_reply.core_idx);
}


@pragma stage 1
table dcr_qlen1 {
    actions {act_dcr_qlen1;}
    default_action : act_dcr_qlen1();
}

action act_send_server1() {
    modify_field(sq_md.curserver,HOSTID_1);
}

table send_server1 {
    actions {act_send_server1;}
    default_action : act_send_server1();
}
