register lowest_load_server {
    width : 64;
    instance_count : 3;
}

blackbox stateful_alu salu_update_llserver {
    reg : lowest_load_server;
    initial_register_lo_value : 1;
    initial_register_hi_value : 9999;
    condition_lo : sq_md.curserver == register_lo;
    condition_hi : sq_reply.qlen1 - register_hi <= 0;

    update_lo_1_predicate : condition_hi;
    update_lo_1_value : sq_md.curserver;

    update_hi_1_predicate : condition_lo or condition_hi;
    update_hi_1_value : sq_reply.qlen1;
}

action act_update_llserver() {
    salu_update_llserver.execute_stateful_alu(sq_md.counter_idx);
}

table update_llserver {
    actions {act_update_llserver;}
    default_action : act_update_llserver;
}

blackbox stateful_alu salu_read_llserver {
    reg : lowest_load_server;
    initial_register_lo_value : 1;
    initial_register_hi_value : 9999;
    output_value : register_lo;
    output_dst : sq_md.sq_server;
}

action act_read_llserver() {
    salu_read_llserver.execute_stateful_alu(sq_md.counter_idx);
}

table read_llserver {
    actions {act_read_llserver;}
    default_action : act_read_llserver;
}
