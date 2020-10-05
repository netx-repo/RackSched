action act_random1_qlen1() {
    modify_field(sq_md.qlen_random1, sq_md.qlen1);
}

table random1_qlen1 {
    actions {act_random1_qlen1;}
    default_action : act_random1_qlen1();
}

action act_random1_qlen2() {
    modify_field(sq_md.qlen_random1, sq_md.qlen2);
}

table random1_qlen2 {
    actions {act_random1_qlen2;}
    default_action : act_random1_qlen2();
}

action act_random1_qlen3() {
    modify_field(sq_md.qlen_random1, sq_md.qlen3);
}

table random1_qlen3 {
    actions {act_random1_qlen3;}
    default_action : act_random1_qlen3();
}

action act_random1_qlen4() {
    modify_field(sq_md.qlen_random1, sq_md.qlen4);
}

table random1_qlen4 {
    actions {act_random1_qlen4;}
    default_action : act_random1_qlen4();
}

action act_random1_qlen5() {
    modify_field(sq_md.qlen_random1, sq_md.qlen5);
}

table random1_qlen5 {
    actions {act_random1_qlen5;}
    default_action : act_random1_qlen5();
}

action act_random1_qlen6() {
    modify_field(sq_md.qlen_random1, sq_md.qlen6);
}

table random1_qlen6 {
    actions {act_random1_qlen6;}
    default_action : act_random1_qlen6();
}

action act_random1_qlen7() {
    modify_field(sq_md.qlen_random1, sq_md.qlen7);
}

table random1_qlen7 {
    actions {act_random1_qlen7;}
    default_action : act_random1_qlen7();
}

action act_random1_qlen8() {
    modify_field(sq_md.qlen_random1, sq_md.qlen8);
}

table random1_qlen8 {
    actions {act_random1_qlen8;}
    default_action : act_random1_qlen8();
}

action _no_op() {
    no_op();
}

table assign_qlen_random1 {
    reads {
        sq_md.random_server1: exact;
    }
    actions {
        act_random1_qlen1;
        act_random1_qlen2;
        act_random1_qlen3;
        act_random1_qlen4;
        act_random1_qlen5;
        act_random1_qlen6;
        act_random1_qlen7;
        act_random1_qlen8;
        _no_op;
    }
    default_action : _no_op();
}


action act_random2_qlen1() {
    modify_field(sq_md.qlen_random2, sq_md.qlen1);
}

table random2_qlen1 {
    actions {act_random2_qlen1;}
    default_action : act_random2_qlen1();
}

action act_random2_qlen2() {
    modify_field(sq_md.qlen_random2, sq_md.qlen2);
}

table random2_qlen2 {
    actions {act_random2_qlen2;}
    default_action : act_random2_qlen2();
}

action act_random2_qlen3() {
    modify_field(sq_md.qlen_random2, sq_md.qlen3);
}

table random2_qlen3 {
    actions {act_random2_qlen3;}
    default_action : act_random2_qlen3();
}

action act_random2_qlen4() {
    modify_field(sq_md.qlen_random2, sq_md.qlen4);
}

table random2_qlen4 {
    actions {act_random2_qlen4;}
    default_action : act_random2_qlen4();
}

action act_random2_qlen5() {
    modify_field(sq_md.qlen_random2, sq_md.qlen5);
}

table random2_qlen5 {
    actions {act_random2_qlen5;}
    default_action : act_random2_qlen5();
}

action act_random2_qlen6() {
    modify_field(sq_md.qlen_random2, sq_md.qlen6);
}

table random2_qlen6 {
    actions {act_random2_qlen6;}
    default_action : act_random2_qlen6();
}

action act_random2_qlen7() {
    modify_field(sq_md.qlen_random2, sq_md.qlen7);
}

table random2_qlen7 {
    actions {act_random2_qlen7;}
    default_action : act_random2_qlen7();
}

action act_random2_qlen8() {
    modify_field(sq_md.qlen_random2, sq_md.qlen8);
}

table random2_qlen8 {
    actions {act_random2_qlen8;}
    default_action : act_random2_qlen8();
}

table assign_qlen_random2 {
    reads {
        sq_md.random_server2: exact;
    }
    actions {
        act_random2_qlen1;
        act_random2_qlen2;
        act_random2_qlen3;
        act_random2_qlen4;
        act_random2_qlen5;
        act_random2_qlen6;
        act_random2_qlen7;
        act_random2_qlen8;
        _no_op;
    }
    default_action : _no_op();
}

action act_cmp_random_qlen() {
    min(sq_md.min_random_qlen, sq_md.qlen_random1, sq_md.qlen_random2);
}

table cmp_random_qlen {
    actions {act_cmp_random_qlen;}
    default_action : act_cmp_random_qlen();
}

action act_assign_curserver_random1() {
    add(sq_md.sq_server, sq_md.random_server1, 1);
}

table assign_curserver_random1 {
    actions {act_assign_curserver_random1;}
    default_action : act_assign_curserver_random1();
}

action act_assign_curserver_random2() {
    add(sq_md.sq_server, sq_md.random_server2, 1);
}

table assign_curserver_random2 {
    actions {act_assign_curserver_random2;}
    default_action : act_assign_curserver_random2();
}
