register server_qlen5 {
    width : 64;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen5 {
    reg : server_qlen5;
    output_value : register_lo;
    output_dst : sq_md.qlen5;
}

action act_read_qlen5() {
    salu_read_qlen5.execute_stateful_alu(sq_md.counter_idx);
}

table read_qlen5 {
    actions {act_read_qlen5;}
    default_action : act_read_qlen5;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_inc_qlen5 {
    reg : server_qlen5;

    condition_lo : sq_md.sq_server == HOSTID_5;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;
}

action act_inc_qlen5() {
    salu_inc_qlen5.execute_stateful_alu(sq_md.counter_idx);
}

table inc_qlen5 {
    actions {act_inc_qlen5;}
    default_action : act_inc_qlen5;
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen5 {
    reg : server_qlen5;

    condition_lo : ipv4.srcAddr == HOSTIP_5;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen5() {
    salu_dcr_qlen5.execute_stateful_alu(sq_md.counter_idx);
}

table dcr_qlen5 {
    actions {act_dcr_qlen5;}
    default_action : act_dcr_qlen5;
}

action act_min5() {
    modify_field(sq_md.sq_server, HOSTID_5);
}

table set_min5 {
    actions {act_min5;}
    default_action : act_min5();
}
