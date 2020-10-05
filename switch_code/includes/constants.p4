#define QUERY 0
#define REPLY 1

/*** used for random scheduling ***/

// RNDSERVER_SIZE should be n, RND_SIZE should be (1<<n)-1,
#define RANDOM_RNDSERVER_SIZE 1
#define RANDOM_RND_SIZE 1
#define RANDOM_SERVER_NUM 2

#define RNDSERVER_SIZE 3
#define RND_SIZE 7

// for scalability results: shinjuku_server_num=4
// #define RNDSERVER_SIZE 2
// #define RND_SIZE 3

// for scalability results: shinjuku_server_num=2
// #define RNDSERVER_SIZE 1
// #define RND_SIZE 1

#define RNDSERVER_SIZE8 5
#define RND_SIZE8 31


/*** INT2, only tracks the minimum number of outstanding requests and updates on reply packets ***/
// the ratio for random is 1/(RANDOM_BASE_MAX+1), RANDOM_BASE_MAX = (1<<RANDOM_BASE)-1
#define RANDOM_BASE 2

/*** used for PROACTIVE, maintain counters on the switch ***/
#define RANDOM_BASE_MAX 3

/*** used for round-robin scheduling ***/
#define SERVER_NUM8 8

// #define SERVER_NUM 2
#define PORT_OFFSET 1236
#define TYPE_REQ 1
#define TYPE_REQ_FOLLOW 2

/*** used for shortest-queue scheduling ***/
#define HOSTIP_1 0x0a010001
#define HOSTIP_2 0x0a010002
#define HOSTIP_3 0x0a010003
#define HOSTIP_4 0x0a010004
#define HOSTIP_5 0x0a010005
#define HOSTIP_6 0x0a010006
#define HOSTIP_7 0x0a010007
#define HOSTIP_8 0x0a010008

#define PREEMTIVE_SLICE 5000

/*** used for multi-pkt support ***/
#define QLEN_LEN 32
#define QLEN_LEN_2 64

#define HASH_NUM_BASE 16
// HASH_NUM = (1<<HASH_NUM_BASE)
#define HASH_NUM 65536 // 65536:1<<16, 1048576:1<<20
#define SERVER_NUM_POW 1 // #of servers = (1<<SERVER_NUM_POW)
#define HASH_SIZE 4294967296 //1<<32
