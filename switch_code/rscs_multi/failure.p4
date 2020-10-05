#define SIM_WORK 0
#define SIM_FAIL 1

action act_set_status(status) {
    modify_field(sq_md.status, status);
}

table sim_fail {
    actions {act_set_status;}
}
