#define HOSTID_1 0
#define HOSTID_2 1
#define HOSTID_3 2
#define HOSTID_4 3
#define HOSTID_5 4
#define HOSTID_6 5
#define HOSTID_7 6
#define HOSTID_8 7

action act_min1() {
    modify_field(sq_md.sq_server, HOSTID_1);
}

table set_min1 {
    actions {act_min1;}
    default_action : act_min1();
}

action act_min2() {
    modify_field(sq_md.sq_server, HOSTID_2);
}

table set_min2 {
    actions {act_min2;}
    default_action : act_min2();
}

action act_min3() {
    modify_field(sq_md.sq_server, HOSTID_3);
}

table set_min3 {
    actions {act_min3;}
    default_action : act_min3();
}

action act_min4() {
    modify_field(sq_md.sq_server, HOSTID_4);
}

table set_min4 {
    actions {act_min4;}
    default_action : act_min4();
}

action act_min5() {
    modify_field(sq_md.sq_server, HOSTID_5);
}

table set_min5 {
    actions {act_min5;}
    default_action : act_min5();
}

action act_min6() {
    modify_field(sq_md.sq_server, HOSTID_6);
}

table set_min6 {
    actions {act_min6;}
    default_action : act_min6();
}

action act_min7() {
    modify_field(sq_md.sq_server, HOSTID_7);
}

table set_min7 {
    actions {act_min7;}
    default_action : act_min7();
}

action act_min8() {
    modify_field(sq_md.sq_server, HOSTID_8);
}

table set_min8 {
    actions {act_min8;}
    default_action : act_min8();
}
