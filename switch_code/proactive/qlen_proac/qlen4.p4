register server_qlen4 {
    width : 64;
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
    default_action : act_read_qlen4;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_inc_qlen4 {
    reg : server_qlen4;

    condition_lo : sq_md.sq_server == HOSTID_4;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;
}

action act_inc_qlen4() {
    salu_inc_qlen4.execute_stateful_alu(sq_md.counter_idx);
}

table inc_qlen4 {
    actions {act_inc_qlen4;}
    default_action : act_inc_qlen4;
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen4 {
    reg : server_qlen4;

    condition_lo : ipv4.srcAddr == HOSTIP_4;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen4() {
    salu_dcr_qlen4.execute_stateful_alu(sq_md.counter_idx);
}

table dcr_qlen4 {
    actions {act_dcr_qlen4;}
    default_action : act_dcr_qlen4;
}

action act_min4() {
    modify_field(sq_md.sq_server, HOSTID_4);
}

table set_min4 {
    actions {act_min4;}
    default_action : act_min4();
}
