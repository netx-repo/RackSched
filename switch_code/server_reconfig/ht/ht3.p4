register ht3 {
    width : 64;
    instance_count : HASH_NUM;
}

field_list_calculation sq_md_hash_3 {
    input {sq_hash_field;}
    algorithm : crc_16_genibus;
    output_width : HASH_NUM_BASE;
}

blackbox stateful_alu salu_wrt_ht3 {
    reg : ht3;

    condition_lo : register_hi == 0;
    condition_hi : register_hi == sq_md.req_id;

    update_lo_1_predicate : condition_lo or condition_hi;
    update_lo_1_value : sq_md.sq_server;

    update_hi_1_predicate : condition_lo or condition_hi;
    update_hi_1_value : sq_md.req_id;

    output_predicate : condition_lo or condition_hi;
    output_value : combined_predicate;
    output_dst : sq_md.stored_server;
}

action act_wrt_ht3() {
    salu_wrt_ht3.execute_stateful_alu_from_hash(sq_md_hash_3);
}

table write_sq_ht3 {
    actions {act_wrt_ht3;}
    default_action : act_wrt_ht3();
}

blackbox stateful_alu salu_read_ht3 {
    reg : ht3;

    condition_lo : register_hi == sq_md.req_id;
    output_predicate : condition_lo;

    output_value : register_lo;
    // output_dst : sq_md.stored_server;
    output_dst : sq_md.sq_server;
}

action act_read_ht3() {
    salu_read_ht3.execute_stateful_alu_from_hash(sq_md_hash_3);
}

table read_sq_ht3 {
    actions {act_read_ht3;}
    default_action : act_read_ht3();
}

blackbox stateful_alu salu_reset_ht3 {
    reg : ht3;
    condition_lo : register_hi == sq_md.req_id;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : 0;

    update_hi_1_predicate : condition_lo;
    update_hi_1_value : 0;
}

action act_reset_ht3() {
    salu_reset_ht3.execute_stateful_alu_from_hash(sq_md_hash_3);
}

table reset_sq_ht3 {
    actions {act_reset_ht3;}
    default_action : act_reset_ht3();
}
