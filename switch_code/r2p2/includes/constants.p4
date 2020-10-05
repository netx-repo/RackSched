/*** used for recirculate ***/
#define IS_RECIR 1

// #define CORE_NUM 8
#define CORE_NUM 8
/*** used for random scheduling ***/

// RNDSERVER_SIZE should be n, RND_SIZE should be (1<<n)-1,
#define RANDOM_RNDSERVER_SIZE 1
#define RANDOM_RND_SIZE 1
#define RANDOM_SERVER_NUM 2

#define RNDSERVER_SIZE 3
#define RND_SIZE 7


// the ratio for random is 1/(RANDOM_BASE_MAX+1), RANDOM_BASE_MAX = (1<<RANDOM_BASE)-1
#define RANDOM_BASE 2
#define RANDOM_BASE_MAX 3

/*** used for round-robin scheduling ***/
#define SERVER_NUM 2
// #define SERVER_NUM 2
#define PORT_OFFSET 1236
#define REQ0 1
#define TYPE_REQ_FOLLOW 2
#define REPLY 3

/*** used for shortest-queue scheduling ***/
#define HOSTIP_1 0x0a010001
#define HOSTIP_2 0x0a010002
#define HOSTIP_3 0x0a010003
#define HOSTIP_4 0x0a010004
#define HOSTIP_5 0x0a010005
#define HOSTIP_6 0x0a010006
#define HOSTIP_7 0x0a010007
#define HOSTIP_8 0x0a010008

#define HOSTID_1 0
#define HOSTID_2 1
#define HOSTID_3 2
#define HOSTID_4 3
#define HOSTID_5 4
#define HOSTID_6 5
#define HOSTID_7 6
#define HOSTID_8 7

/*** used for multi-pkt support ***/
#define QLEN_LEN 32
#define QLEN_LEN_2 64
#define TYPE_REQ 1
#define TYPE_REQ_FOLLOW 2

#define HASH_NUM_BASE 19
// HASH_NUM = (1<<HASH_NUM_BASE)
#define HASH_NUM 524228 // 65536:1<<16, 1048576:1<<20

#define HASH_SIZE 4294967296 //1<<32
// #define HOSTID_1 1
// #define HOSTID_2 2
// #define HOSTID_3 3
// #define HOSTID_4 4
// #define HOSTID_5 5
// #define HOSTID_6 6
// #define HOSTID_7 7
// #define HOSTID_8 8
#define INGRESS_PORT_1 188
#define INGRESS_PORT_2 184
