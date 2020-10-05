register server_qlen8 {
    width : QLEN_LEN_2;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen8 {
    reg : server_qlen8;
    output_value : register_lo;
    output_dst : sq_md.qlen8;
}

action act_read_qlen8() {
    salu_read_qlen8.execute_stateful_alu(sq_md.counter_idx);
}

// @pragma stage 2
table read_qlen8 {
    actions {act_read_qlen8;}
    default_action : act_read_qlen8();
}

// update the queue len upon reply
blackbox stateful_alu salu_update_qlen8 {
    reg : server_qlen8;

    condition_lo : ipv4.srcAddr == HOSTIP_8;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : sq_reply.qlen1;
}

action act_update_qlen8() {
    salu_update_qlen8.execute_stateful_alu(sq_md.counter_idx);
}

table update_qlen8 {
    actions {act_update_qlen8;}
    default_action : act_update_qlen8();
}
