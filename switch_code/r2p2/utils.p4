register jbsq_n {
    width : 32;
    instance_count : 1;
}


blackbox stateful_alu salu_read_jbsqn {
    reg : jbsq_n;
    condition_lo : sq_md.round_idx < register_lo-1;

    output_predicate : condition_lo;
    output_value : combined_predicate;
    output_dst : sq_md.smaller_jbsqn;
}

action act_read_jbsqn() {
    salu_read_jbsqn.execute_stateful_alu(0);
}

table read_jbsqn {
    actions {act_read_jbsqn;}
    default_action : act_read_jbsqn();
}


register core_idx {
    width : 16;
    instance_count : 1;
}


blackbox stateful_alu salu_exe_core_idx {
    reg : core_idx;
    //WARN: sth may be wrong, it should be >=, but turned out > works well
    //alu_lo should be the value after modification, but
    condition_lo : register_lo >= CORE_NUM-1;
    update_lo_1_predicate : condition_lo;
    update_lo_1_value : 0;
    update_lo_2_predicate : not condition_lo;
    update_lo_2_value : register_lo + 1;
    output_value : alu_lo;
    output_dst : sq_md.core_idx;
}

action act_exe_core_idx() {
    salu_exe_core_idx.execute_stateful_alu(0);
}

table rr_select_core_idx {
    actions {act_exe_core_idx;}
    default_action : act_exe_core_idx();
}

action act_prepare_recir() {
    modify_field(sq.recir_flag, 1);
    add_header(recir);
    modify_field(recir.round_idx, sq_md.round_idx);
    modify_field(sq.core_idx, sq_md.core_idx);
}

table prepare_recir {
    actions {act_prepare_recir;}
    default_action : act_prepare_recir();
}

action act_mod_hdr_round_idx() {
    modify_field(recir.round_idx,sq_md.round_idx);
}

table mod_hdr_round_idx{
    actions {act_mod_hdr_round_idx;}
    default_action : act_mod_hdr_round_idx();
}

action act_recirculate() {
    recirculate(68);
}

table recir_pkt {
    actions {act_recirculate;}
    default_action : act_recirculate();
}

action act_prepare_md() {
    modify_field(sq_md.round_idx, recir.round_idx);
    modify_field(sq_md.core_idx, sq.core_idx);
}

table prepare_md {
    actions {act_prepare_md;}
    default_action : act_prepare_md();
}

action act_incr_round_idx() {
    add_to_field(sq_md.round_idx,1);
}

table incr_round_idx{
    actions {act_incr_round_idx;}
    default_action : act_incr_round_idx();
}

action act_assign_util() {
    modify_field(sq_md.used_for_shift, 1);
}

table assign_util {
    actions {act_assign_util;}
    default_action : act_assign_util();
}

action act_shift_core_idx() {
    subtract_from_field(sq.core_idx,sq_md.used_for_shift);
}

table shift_core_idx {
    actions {act_shift_core_idx;}
    default_action : act_shift_core_idx();
}

action act_remove_recir() {
    remove_header(recir);
}

table remove_recir {
    actions {act_remove_recir;}
    default_action : act_remove_recir();
}
