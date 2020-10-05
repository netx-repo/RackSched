register server_qlen6 {
    width : 64;
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
    default_action : act_read_qlen6;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_inc_qlen6 {
    reg : server_qlen6;

    condition_lo : sq_md.sq_server == HOSTID_6;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;
}

action act_inc_qlen6() {
    salu_inc_qlen6.execute_stateful_alu(sq_md.counter_idx);
}

table inc_qlen6 {
    actions {act_inc_qlen6;}
    default_action : act_inc_qlen6;
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen6 {
    reg : server_qlen6;

    condition_lo : ipv4.srcAddr == HOSTIP_6;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen6() {
    salu_dcr_qlen6.execute_stateful_alu(sq_md.counter_idx);
}

table dcr_qlen6 {
    actions {act_dcr_qlen6;}
    default_action : act_dcr_qlen6;
}

action act_min6() {
    modify_field(sq_md.sq_server, HOSTID_6);
}

table set_min6 {
    actions {act_min6;}
    default_action : act_min6();
}
