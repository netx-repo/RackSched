register server_qlen1 {
    width : QLEN_LEN_2;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen1 {
    reg : server_qlen1;
    output_value : register_lo;
    output_dst : sq_md.qlen1;
}

action act_read_qlen1() {
    salu_read_qlen1.execute_stateful_alu(sq_md.counter_idx);
}

#ifdef FAILURE
@pragma stage 1
#else
@pragma stage 2
#endif
// @pragma stage 1
table read_qlen1 {
    actions {act_read_qlen1;}
    default_action : act_read_qlen1();
}

// update the queue len upon reply
blackbox stateful_alu salu_update_qlen1 {
    reg : server_qlen1;
    condition_lo : ipv4.srcAddr == HOSTIP_1;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : sq_reply.qlen1;
}

action act_update_qlen1() {
    salu_update_qlen1.execute_stateful_alu(sq_md.counter_idx);
}

#ifdef FAILURE
@pragma stage 1
#else
@pragma stage 2
#endif
// @pragma stage 1
table update_qlen1 {
    actions {act_update_qlen1;}
    default_action : act_update_qlen1();
}
