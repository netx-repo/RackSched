#define ONE_THIRD 21845
#define TWO_THIRD 43691
#define MAX 65536

header_type rand_sample_md_t{
    fields {
        random_int1 : 15;
        random_int2 : 15;
        min_1_int1 : 16;
        min_1_int2 : 16;
    }
}

metadata rand_sample_md_t rand_sample_md;

action act_gen_random_int() {
    modify_field_rng_uniform(rand_sample_md.random_int1, 0, 32767);
    modify_field_rng_uniform(rand_sample_md.random_int2, 0, 32767);
    // modify_field_rng_uniform(rand_sample_md.random_int1, 0, 7);
    // modify_field_rng_uniform(rand_sample_md.random_int2, 0, 7);
}

table gen_random_int {
    actions {act_gen_random_int;}
    default_action : act_gen_random_int();
}

// using RANGE match-action table instead of comparing in data plane

action act_assign_int1_to_random_7(random_num) {
    modify_field(sq_md.random_server1, random_num);
}

action drop_packet() {
   drop();
}

table int1_to_random_7 {
    reads {
        rand_sample_md.random_int1: range;
    }
    actions {
        act_assign_int1_to_random_7;
        // drop_packet;
    }
    default_action: act_assign_int1_to_random_7(0);
}

action act_assign_int2_to_random_7(random_num) {
    modify_field(sq_md.random_server2, random_num);
}

// @pragma stage 3
table int2_to_random_7 {
    reads {
        rand_sample_md.random_int2: range;
    }
    actions {
        act_assign_int2_to_random_7;
        // drop_packet;
    }
    default_action: act_assign_int2_to_random_7(0);
}
