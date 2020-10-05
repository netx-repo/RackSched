register ht2 {
    width : 64;
    instance_count : HASH_NUM;
}

field_list_calculation sq_md_hash_2 {
    input {sq_hash_field;}
    algorithm : crc_16_en_13757;
    output_width : HASH_NUM_BASE;
}

blackbox stateful_alu salu_wrt_ht2 {
    reg : ht2;

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

action act_wrt_ht2() {
    salu_wrt_ht2.execute_stateful_alu_from_hash(sq_md_hash_2);
}

// @pragma stage 8
table write_sq_ht2 {
    actions {act_wrt_ht2;}
    default_action : act_wrt_ht2();
}

blackbox stateful_alu salu_read_ht2 {
    reg : ht2;

    condition_lo : register_hi == sq_md.req_id;
    output_predicate : condition_lo;

    output_value : register_lo;
    // output_dst : sq_md.stored_server;
    output_dst : sq_md.sq_server;
}

action act_read_ht2() {
    salu_read_ht2.execute_stateful_alu_from_hash(sq_md_hash_2);
}

// @pragma stage 8
table read_sq_ht2 {
    actions {act_read_ht2;}
    default_action : act_read_ht2();
}

blackbox stateful_alu salu_reset_ht2 {
    reg : ht2;
    condition_lo : register_hi == sq_md.req_id;

    update_lo_1_predicate : condition_lo;
    update_lo_1_value : 0;

    update_hi_1_predicate : condition_lo;
    update_hi_1_value : 0;
}

action act_reset_ht2() {
    salu_reset_ht2.execute_stateful_alu_from_hash(sq_md_hash_2);
}

// @pragma stage 8
table reset_sq_ht2 {
    actions {act_reset_ht2;}
    default_action : act_reset_ht2();
}
