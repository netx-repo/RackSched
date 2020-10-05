register server_qlen1 {
    width : 64;
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

table read_qlen1 {
    actions {act_read_qlen1;}
    default_action : act_read_qlen1;
}

// increase the counter after finding the shortest_queue
blackbox stateful_alu salu_inc_qlen1 {
    reg : server_qlen1;

    condition_lo : sq_md.sq_server == HOSTID_1;
    // condition_lo : sq_md.random_server == HOSTID_1;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : register_lo + 1;
}

action act_inc_qlen1() {
    salu_inc_qlen1.execute_stateful_alu(sq_md.counter_idx);
}

table inc_qlen1 {
    actions {act_inc_qlen1;}
    default_action : act_inc_qlen1;
}

// decrease the reply upon reply
blackbox stateful_alu salu_dcr_qlen1 {
    reg : server_qlen1;

    condition_lo : ipv4.srcAddr == HOSTIP_1;
    condition_hi : register_lo > 0;

    update_lo_1_predicate : condition_lo and condition_hi;
    update_lo_1_value : register_lo - 1;
}

action act_dcr_qlen1() {
    salu_dcr_qlen1.execute_stateful_alu(sq_md.counter_idx);
}

table dcr_qlen1 {
    actions {act_dcr_qlen1;}
    default_action : act_dcr_qlen1;
}

action act_min1() {
    modify_field(sq_md.sq_server, HOSTID_1);
}

table set_min1 {
    actions {act_min1;}
    default_action : act_min1();
}
