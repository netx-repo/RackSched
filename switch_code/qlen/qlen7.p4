register server_qlen7 {
    width : QLEN_LEN_2;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen7 {
    reg : server_qlen7;
    output_value : register_lo;
    output_dst : sq_md.qlen7;
}

action act_read_qlen7() {
    salu_read_qlen7.execute_stateful_alu(sq_md.counter_idx);
}

table read_qlen7 {
    actions {act_read_qlen7;}
    default_action : act_read_qlen7();
}

// update the queue len upon reply
blackbox stateful_alu salu_update_qlen7 {
    reg : server_qlen7;

    condition_lo : ipv4.srcAddr == HOSTIP_7;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : sq_reply.qlen1;
}

action act_update_qlen7() {
    salu_update_qlen7.execute_stateful_alu(sq_md.counter_idx);
}

// @pragma stage 1
table update_qlen7 {
    actions {act_update_qlen7;}
    default_action : act_update_qlen7();
}
