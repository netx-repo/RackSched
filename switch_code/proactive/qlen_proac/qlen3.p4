register server_qlen3 {
    width : 64;
    instance_count : 3;
}

// read the value from register
blackbox stateful_alu salu_read_qlen3 {
    reg : server_qlen3;
    output_value : register_lo;
    output_dst : sq_md.qlen3;
}

action act_read_qlen3() {
    salu_read_qlen3.execute_stateful_alu(sq_md.counter_idx);
}

table read_qlen3 {
    actions {act_read_qlen3;}
    default_action : act_read_qlen3;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_inc_qlen3 {
    reg : server_qlen3;

    condition_lo : sq_md.sq_server == HOSTID_3;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;
}

action act_inc_qlen3() {
    salu_inc_qlen3.execute_stateful_alu(sq_md.counter_idx);
}

table inc_qlen3 {
    actions {act_inc_qlen3;}
    default_action : act_inc_qlen3;
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
    salu_dcr_qlen3.execute_stateful_alu(sq_md.counter_idx);
}

table dcr_qlen3 {
    actions {act_dcr_qlen3;}
    default_action : act_dcr_qlen3;
}

action act_min3() {
    modify_field(sq_md.sq_server, HOSTID_3);
}

table set_min3 {
    actions {act_min3;}
    default_action : act_min3();
}
