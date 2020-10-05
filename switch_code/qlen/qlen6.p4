register server_qlen6 {
    width : QLEN_LEN_2;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen6 {
    reg : server_qlen6;
    output_value : register_lo;
    output_dst : sq_md.qlen6;
}

action act_read_qlen6() {
    salu_read_qlen6.execute_stateful_alu(sq_md.counter_idx);
}

table read_qlen6 {
    actions {act_read_qlen6;}
    default_action : act_read_qlen6();
}

// update the queue len upon reply
blackbox stateful_alu salu_update_qlen6 {
    reg : server_qlen6;

    condition_lo : ipv4.srcAddr == HOSTIP_6;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : sq_reply.qlen1;
}

action act_update_qlen6() {
    salu_update_qlen6.execute_stateful_alu(sq_md.counter_idx);
}

table update_qlen6 {
    actions {act_update_qlen6;}
    default_action : act_update_qlen6();
}
