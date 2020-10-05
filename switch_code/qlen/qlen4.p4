register server_qlen4 {
    width : QLEN_LEN_2;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen4 {
    reg : server_qlen4;
    output_value : register_lo;
    output_dst : sq_md.qlen4;
}

action act_read_qlen4() {
    salu_read_qlen4.execute_stateful_alu(sq_md.counter_idx);
}

table read_qlen4 {
    actions {act_read_qlen4;}
    default_action : act_read_qlen4();
}

// update the queue len upon reply
blackbox stateful_alu salu_update_qlen4 {
    reg : server_qlen4;

    condition_lo : ipv4.srcAddr == HOSTIP_4;

    update_lo_1_predicate : condition_lo;
    // update_lo_1_value : sq_reply.queue_len1;
    update_lo_1_value : sq_reply.qlen1;
}

action act_update_qlen4() {
    salu_update_qlen4.execute_stateful_alu(sq_md.counter_idx);
}

// @pragma stage 1
table update_qlen4 {
    actions {act_update_qlen4;}
    default_action : act_update_qlen4();
}
