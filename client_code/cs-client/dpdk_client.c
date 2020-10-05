#include <arpa/inet.h>
#include <assert.h>
#include <errno.h>
#include <getopt.h>
#include <inttypes.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/queue.h>
#include <time.h>

#include <rte_cycles.h>
#include <rte_debug.h>
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_launch.h>
#include <rte_lcore.h>
#include <rte_malloc.h>
#include <rte_mbuf.h>
#include <rte_memory.h>
#include <rte_memzone.h>
#include <rte_per_lcore.h>
#include <rte_udp.h>

#include "util.h"
#include "zipf.h"

/*
 * constants
 */

#define NUM_PKTS 1
#define MAX_RESULT_SIZE 16777216UL  // 2^24

/*
 * custom types
 */

/********* Configs *********/
char ip_client[][32] = {
    "10.1.0.1", "10.1.0.2", "10.1.0.3", "10.1.0.4",  "10.1.0.5",  "10.1.0.6",
    "10.1.0.7", "10.1.0.8", "10.1.0.9", "10.1.0.10", "10.1.0.11", "10.1.0.12",
};

char ip_server[][32] = {
    "10.1.0.1", "10.1.0.2", "10.1.0.3", "10.1.0.4",  "10.1.0.5",  "10.1.0.6",
    "10.1.0.7", "10.1.0.8", "10.1.0.9", "10.1.0.10", "10.1.0.11", "10.1.0.12",
};

uint16_t src_port = 11234;
uint16_t dst_port = 1234;

/********* Custom parameters *********/
int is_latency_client = 0;   // 0 means batch client, 1 means latency client
uint32_t client_index = 11;  // default client: netx12
uint32_t server_index = 0;   // default server: netx1
uint32_t qps = 100000;       // default qps: 100000
char *dist_type = "fixed";   // default dist: fixed
uint32_t scale_factor = 1;   // 1 means the mean is 1us; mean = 1 * scale_factor
uint32_t is_rocksdb = 0; // 1 means testing with rocksdb, 0 means testing with synthetic workload

/********* Packet related *********/
uint32_t req_id = 0;
int max_req_id = (1<<25)-1;
uint32_t req_id_core[8] = {0};

/********* Results *********/
uint64_t pkt_sent = 0;
uint64_t pkt_recv = 0;
LatencyResults latency_results = {NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0, 0};

/********* Debug the us *********/
uint64_t work_ns_sample[1048576] = {0};
uint32_t sample_idx = 0;
uint64_t local_type_count[2] = {0};

/********* Used for server-based selection *********/
uint64_t server_load[1000][8] = {0};
uint16_t client_num = 10;
uint32_t zipf_alpha = 90;
struct zipf_gen_state *zipf_state;

/*
 * functions called when program ends
 */

static void dump_stats_to_file() {
  size_t count = latency_results.count;

  FILE *output_ptr = fopen("./results/output", "wb");
  fwrite(latency_results.sjrn_times, sizeof(latency_results.sjrn_times),
         latency_results.count, output_ptr);
  FILE *output_reply_ns_ptr = fopen("./results/output.reply_ns", "wb");
  fwrite(latency_results.reply_run_ns, sizeof(latency_results.reply_run_ns),
         latency_results.count, output_reply_ns_ptr);
  FILE *output_ptr_short = fopen("./results/output.short", "wb");
  fwrite(latency_results.sjrn_times_short, sizeof(latency_results.sjrn_times_short),
         latency_results.count_short, output_ptr_short);
  FILE *output_ptr_long = fopen("./results/output.long", "wb");
  fwrite(latency_results.sjrn_times_long, sizeof(latency_results.sjrn_times_long),
        latency_results.count_long, output_ptr_long);
  FILE *ratio_ptr = fopen("./results/output.ratios", "wb");
  fwrite(latency_results.work_ratios, sizeof(latency_results.work_ratios),
         latency_results.count, ratio_ptr);
  FILE *ratio_ptr_short = fopen("./results/output.ratios.short", "wb");
  fwrite(latency_results.work_ratios_short, sizeof(latency_results.work_ratios_short),
         latency_results.count_short, ratio_ptr_short);
  FILE *ratio_ptr_long = fopen("./results/output.ratios.long", "wb");
  fwrite(latency_results.work_ratios_long, sizeof(latency_results.work_ratios_long),
        latency_results.count_long, ratio_ptr_long);

  FILE *queue_length_ptr = fopen("./results/output.queue_lengths", "w");
  for (int i = 0; i < latency_results.count; i++) {
    fprintf(queue_length_ptr, "Queue0: %u, Queue1: %u, Queue2: %u\n",
            latency_results.queue_lengths[i][0],
            latency_results.queue_lengths[i][1],
            latency_results.queue_lengths[i][2]);
  }

  fclose(output_ptr);
  fclose(ratio_ptr);
}

static void sigint_handler(int sig) {
  double req_recv_ratio = (double)pkt_recv / (double)req_id;
  double recv_ratio = (double)pkt_recv / (double)pkt_sent;
  printf("\nRequests sent: %u\n", req_id);
  printf("Packets sent: %lu\n", pkt_sent);
  printf("Responses/Packets received: %lu\n", pkt_recv);
  printf("Ratio of responses recv/requests sent: %lf\n", req_recv_ratio);
  printf("Ratio of packets recv/packets sent: %lf\n", recv_ratio);
  printf("local_type_1-4: %lu\n", local_type_count[0]);
  printf("local_type_5-8: %lu\n", local_type_count[1]);
  fflush(stdout);
  if (is_latency_client > 0) {
    dump_stats_to_file();
  }
  rte_free(latency_results.sjrn_times);
  rte_free(latency_results.work_ratios);
  rte_free(latency_results.queue_lengths);
  rte_free(latency_results.sjrn_times_short);
  rte_free(latency_results.sjrn_times_long);
  rte_free(latency_results.work_ratios_short);
  rte_free(latency_results.work_ratios_long);
  rte_free(latency_results.reply_run_ns);

  rte_exit(EXIT_SUCCESS, "\nStopped DPDK client\n");
}

/*
 * functions
 */

static void generate_packet(uint32_t lcore_id, struct rte_mbuf *mbuf,
                            uint16_t seq_num, uint32_t pkts_length,
                            uint64_t gen_ns, uint64_t run_ns, int port_offset) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  assert(mbuf != NULL);

  mbuf->next = NULL;
  mbuf->nb_segs = 1;
  mbuf->ol_flags = 0;
  mbuf->data_len = 0;
  mbuf->pkt_len = 0;

  // init packet header
  struct ether_hdr *eth = rte_pktmbuf_mtod(mbuf, struct ether_hdr *);
  struct ipv4_hdr *ip =
      (struct ipv4_hdr *)((uint8_t *)eth + sizeof(struct ether_hdr));
  struct udp_hdr *udp =
      (struct udp_hdr *)((uint8_t *)ip + sizeof(struct ipv4_hdr));
  rte_memcpy(eth, header_template, sizeof(header_template));
  mbuf->data_len += sizeof(header_template);
  mbuf->pkt_len += sizeof(header_template);

  // init req msg
  Message *req = (Message *)((uint8_t *)eth + sizeof(header_template));

  inet_pton(AF_INET, ip_client[client_index], &(ip->src_addr));
  inet_pton(AF_INET, ip_server[server_index], &(ip->dst_addr));
  udp->src_port = htons(src_port + port_offset);
  udp->dst_port = htons(dst_port + port_offset);
  if (seq_num == 0) {
    req->type = TYPE_REQ;
  } else {
    req->type = TYPE_REQ_FOLLOW;
  }

  req->seq_num = seq_num;
  req->queue_length[0] = 0;
  req->queue_length[1] = htonl(0);
  req->queue_length[2] = 0;
  uint32_t req_client_id = (client_index + 1 << 3) + lcore_id;

  // used for simulate clients
  uint16_t sim_client_id, random_int;
  sim_client_id = lcore_id;

  // if (zipf_alpha > 0)
  //   sim_client_id = (zipf_next(zipf_state) % client_num);
  // else
  //   sim_client_id = (rte_rand()%client_num);

  // random_int = (rte_rand()%91);
  // if (random_int == 0)
  //   random_int = 9;
  // else
  //   random_int = random_int%9;
  // sim_client_id = random_int;

  req->client_id = sim_client_id;
  // req->req_id = req_id;
  req->req_id = (req_client_id << 25) + req_id_core[lcore_id];
  req->pkts_length = pkts_length;
  req->gen_ns = gen_ns;
  req->run_ns = run_ns;
  // printf("request client_id: %u, req_id: %u\n",req->client_id,req->req_id);
  mbuf->data_len += sizeof(Message);
  mbuf->pkt_len += sizeof(Message);

  // do JSQ on client side
  // uint8_t lst_server_idx = 0;
  // for(int i = 1; i < 7; i++) {
  //   if (server_load[lcore_id][i] < server_load[lcore_id][lst_server_idx])
  //     lst_server_idx = i;
  // }

  // do POK on client side
  uint8_t random1 = rte_rand()%8;
  uint8_t random2 = rte_rand()%8;
  uint8_t lst_server_idx;
  if (server_load[sim_client_id][random1] < server_load[sim_client_id][random2])
    lst_server_idx = random1;
  else
    lst_server_idx = random2;
  inet_pton(AF_INET, ip_server[lst_server_idx], &(ip->dst_addr));
  pkt_sent++;
}

static void process_packet(uint32_t lcore_id, struct rte_mbuf *mbuf) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];

  // parse packet header
  struct ether_hdr *eth = rte_pktmbuf_mtod(mbuf, struct ether_hdr *);
  struct ipv4_hdr *ip =
      (struct ipv4_hdr *)((uint8_t *)eth + sizeof(struct ether_hdr));
  struct udp_hdr *udp =
      (struct udp_hdr *)((uint8_t *)ip + sizeof(struct ipv4_hdr));

  // parse header
  Message *res = (Message *)((uint8_t *)eth + sizeof(header_template));

  uint8_t server_idx = ntohl(ip->src_addr) - 167837696;
  if (server_idx <= 4) {
      local_type_count[0]++;
  }
  else {
      local_type_count[1]++;
  }
  // debug
  // printf("client_id:%u, req_id:%u\n",res->client_id, res->req_id);
  uint64_t cur_ns = get_cur_ns();
  uint16_t reply_port = ntohs(udp->src_port);
  // printf("reply_port:%u\n",reply_port);
  uint64_t reply_run_ns = rte_le_to_cpu_64(res->run_ns);
  assert(cur_ns > res->gen_ns);
  uint64_t sjrn = cur_ns - res->gen_ns;  // diff in time

  // update server load on client side
  uint32_t reply_qlen = ntohs(res->queue_length[0]);
  // uint32_t reply_lcore_id = (res->client_id - (client_index + 1 << 3));
  // assert(reply_lcore_id<8);
  // server_load[reply_lcore_id][server_idx] = reply_qlen;
  uint16_t sim_client_id = res->client_id;
  assert(sim_client_id<client_num);
  server_load[sim_client_id][server_idx] = reply_qlen;
  pkt_recv++;
  // sample
  uint64_t sample_count;
  if (qps > 100000)
   sample_count = qps/100000;
  else
   sample_count = qps/10000;
  if ((pkt_recv%sample_count)!=0)
    return;
  latency_results.sjrn_times[latency_results.count] = sjrn;
  // latency_results.reply_run_ns[latency_results.count] = reply_run_ns;
  latency_results.reply_run_ns[latency_results.count] = sim_client_id;
  if (is_rocksdb == 1) {
      if (res->run_ns == 0)
        res->run_ns = 780000;
      else
        res->run_ns = 50000;
  }
  else {
      if (res->run_ns == 0)
        res->run_ns = 1;
  }
  latency_results.work_ratios[latency_results.count] = sjrn / res->run_ns;
  latency_results.queue_lengths[latency_results.count][0] =
      res->queue_length[0];
  latency_results.queue_lengths[latency_results.count][1] =
      res->queue_length[1];
  latency_results.queue_lengths[latency_results.count][2] =
      res->queue_length[2];
  latency_results.count++;
  if (reply_run_ns == 0) {
      // long request
      latency_results.sjrn_times_long[latency_results.count_long] = sjrn;
      latency_results.work_ratios_long[latency_results.count_long] = sjrn / res->run_ns;
      latency_results.count_long++;
  }
  else {
      // short request
      latency_results.sjrn_times_short[latency_results.count_short] = sjrn;
      latency_results.work_ratios_short[latency_results.count_short] = sjrn / res->run_ns;
      latency_results.count_short++;
  }

  if (unlikely(latency_results.count >= MAX_RESULT_SIZE)) {
    printf("Latency result limit reached. Automatically stopped.\n");
    sigint_handler(SIGINT);
  }
}

static void fixed_tx_loop(uint32_t lcore_id, double work_ns) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering fixed TX loop on lcore %u\n", (long long)time(NULL),
         lcore_id);

  struct rte_mbuf *mbuf;

  ExpDist *dist = malloc(sizeof(ExpDist));
  double lambda = qps * 1e-9;
  double mu = 1.0 / lambda;
  init_exp_dist(dist, mu);

  printf("lcore %u start sending fixed packets in %" PRIu32 " qps\n", lcore_id,
         qps);

  signal(SIGINT, sigint_handler);
  while (1) {
    uint64_t gen_ns = exp_dist_next_arrival_ns(dist);
    uint32_t pkts_length = NUM_PKTS * sizeof(Message);
    for (uint8_t i = 0; i < NUM_PKTS; i++) {
      mbuf = rte_pktmbuf_alloc(pktmbuf_pool);
      generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 0);
      enqueue_pkt(lcore_id, mbuf);
    }
    req_id++;
    if (req_id_core[lcore_id] >= max_req_id) {
      req_id_core[lcore_id] = 0;
    } else {
      req_id_core[lcore_id]++;
    }
    while (get_cur_ns() < gen_ns)
      ;
    send_pkt_burst(lcore_id);
  }
  free_exp_dist(dist);
}

static void exp_tx_loop(uint32_t lcore_id, double work_mu) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering exp TX loop on lcore %u\n", (long long)time(NULL),
         lcore_id);

  struct rte_mbuf *mbuf;

  ExpDist *dist = malloc(sizeof(ExpDist));
  ExpDist *work_dist = malloc(sizeof(ExpDist));
  double lambda = qps * 1e-9;
  double mu = 1.0 / lambda;
  uint64_t work_ns;
  init_exp_dist(dist, mu);
  init_exp_dist(work_dist, work_mu);

  printf("lcore %u start sending exp packets in %" PRIu32 " qps\n", lcore_id,
         qps);

  signal(SIGINT, sigint_handler);
  while (1) {
    // while (work_ns == 0) {
    //     work_ns = exp_dist_work_ns(work_dist);
    // }
    work_ns = exp_dist_work_ns(work_dist);
    uint64_t gen_ns = exp_dist_next_arrival_ns(dist);
    uint32_t pkts_length = NUM_PKTS * sizeof(Message);
    for (uint8_t i = 0; i < NUM_PKTS; i++) {
      mbuf = rte_pktmbuf_alloc(pktmbuf_pool);
      generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 0);
      enqueue_pkt(lcore_id, mbuf);
    }
    req_id++;
    if (req_id_core[lcore_id] >= max_req_id) {
      req_id_core[lcore_id] = 0;
    } else {
      req_id_core[lcore_id]++;
    }
    while (get_cur_ns() < gen_ns)
      ;
    send_pkt_burst(lcore_id);
  }
  free_exp_dist(dist);
  free_exp_dist(work_dist);
}

static void lognormal_tx_loop(uint32_t lcore_id, double work_mu, double sigma) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering lognormal TX loop on lcore %u\n", (long long)time(NULL),
         lcore_id);

  struct rte_mbuf *mbuf;

  ExpDist *dist = malloc(sizeof(ExpDist));
  LognormalDist *work_dist = malloc(sizeof(LognormalDist));
  double lambda = qps * 1e-9;
  double mu = 1.0 / lambda;
  uint64_t work_ns;
  init_exp_dist(dist, mu);
  init_lognormal_dist(work_dist, work_mu, sigma);

  printf("lcore %u start sending lognormal packets in %" PRIu32 " qps\n",
         lcore_id, qps);

  signal(SIGINT, sigint_handler);
  while (1) {
    work_ns = lognormal_dist_work_ns(work_dist);
    uint64_t gen_ns = exp_dist_next_arrival_ns(dist);
    uint32_t pkts_length = NUM_PKTS * sizeof(Message);
    for (uint8_t i = 0; i < NUM_PKTS; i++) {
      mbuf = rte_pktmbuf_alloc(pktmbuf_pool);
      generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 0);
      enqueue_pkt(lcore_id, mbuf);
    }
    req_id++;
    if (req_id_core[lcore_id] >= max_req_id) {
      req_id_core[lcore_id] = 0;
    } else {
      req_id_core[lcore_id]++;
    }
    while (get_cur_ns() < gen_ns)
      ;
    send_pkt_burst(lcore_id);
  }
  free_exp_dist(dist);
  free_lognormal_dist(work_dist);
}

static void bimodal_tx_loop(uint32_t lcore_id, uint64_t work_1_ns,
                            uint64_t work_2_ns, double ratio) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering bimodal TX loop on lcore %u\n", (long long)time(NULL),
         lcore_id);

  struct rte_mbuf *mbuf;

  ExpDist *dist = malloc(sizeof(ExpDist));
  BimodalDist *work_dist = malloc(sizeof(BimodalDist));
  double lambda;
  // if (lcore_id == 7)
  //   lambda = 10000 * 1e-9;
  // else
  //   lambda = qps * 1e-9;
  lambda = qps * 1e-9;
  double mu = 1.0 / lambda;
  uint64_t work_ns;
  init_exp_dist(dist, mu);
  init_bimodal_dist(work_dist, work_1_ns, work_2_ns, ratio);

  printf("lcore %u start sending bimodal packets in %" PRIu32 " qps\n",
         lcore_id, qps);

  signal(SIGINT, sigint_handler);
  while (1) {
    work_ns = bimodal_dist_work_ns(work_dist);
    uint64_t gen_ns = exp_dist_next_arrival_ns(dist);
    uint32_t pkts_length = NUM_PKTS * sizeof(Message);
    for (uint8_t i = 0; i < NUM_PKTS; i++) {
      mbuf = rte_pktmbuf_alloc(pktmbuf_pool);
      generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 0);
      enqueue_pkt(lcore_id, mbuf);
    }
    req_id++;
    if (req_id_core[lcore_id] >= max_req_id) {
      req_id_core[lcore_id] = 0;
    } else {
      req_id_core[lcore_id]++;
    }
    while (get_cur_ns() < gen_ns)
      ;
    send_pkt_burst(lcore_id);
  }
  free_exp_dist(dist);
  free_bimodal_dist(work_dist);
}

static void port_bimodal_tx_loop(uint32_t lcore_id, uint64_t work_1_ns,
                                 uint64_t work_2_ns, double ratio) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering port bimodal TX loop on lcore %u\n",
         (long long)time(NULL), lcore_id);

  struct rte_mbuf *mbuf;

  ExpDist *dist = malloc(sizeof(ExpDist));
  BimodalDist *work_dist = malloc(sizeof(BimodalDist));
  double lambda = qps * 1e-9;
  double mu = 1.0 / lambda;
  uint64_t work_ns;
  init_exp_dist(dist, mu);
  init_bimodal_dist(work_dist, work_1_ns, work_2_ns, ratio);

  printf("lcore %u start sending port bimodal packets in %" PRIu32 " qps\n",
         lcore_id, qps);

  signal(SIGINT, sigint_handler);
  while (1) {
    work_ns = bimodal_dist_work_ns(work_dist);
    uint64_t gen_ns = exp_dist_next_arrival_ns(dist);
    uint32_t pkts_length = NUM_PKTS * sizeof(Message);
    for (uint8_t i = 0; i < NUM_PKTS; i++) {
      mbuf = rte_pktmbuf_alloc(pktmbuf_pool);
      if (work_ns == work_1_ns) {
        generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 0);
      } else if (work_ns == work_2_ns) {
        generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 1);
      }
      enqueue_pkt(lcore_id, mbuf);
    }
    req_id++;
    if (req_id_core[lcore_id] >= max_req_id) {
      req_id_core[lcore_id] = 0;
    } else {
      req_id_core[lcore_id]++;
    }
    while (get_cur_ns() < gen_ns)
      ;
    send_pkt_burst(lcore_id);
  }
  free_exp_dist(dist);
  free_bimodal_dist(work_dist);
}

static void port_trimodal_tx_loop(uint32_t lcore_id, uint64_t work_1_ns,
                                  uint64_t work_2_ns, uint64_t work_3_ns,
                                  double ratio1, double ratio2) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering port trimodal TX loop on lcore %u\n",
         (long long)time(NULL), lcore_id);

  struct rte_mbuf *mbuf;

  ExpDist *dist = malloc(sizeof(ExpDist));
  TrimodalDist *work_dist = malloc(sizeof(TrimodalDist));
  double lambda = qps * 1e-9;
  double mu = 1.0 / lambda;
  uint64_t work_ns;
  init_exp_dist(dist, mu);
  init_trimodal_dist(work_dist, work_1_ns, work_2_ns, work_3_ns, ratio1,
                     ratio2);

  printf("lcore %u start sending port trimodal packets in %" PRIu32 " qps\n",
         lcore_id, qps);

  signal(SIGINT, sigint_handler);
  while (1) {
    work_ns = trimodal_dist_work_ns(work_dist);
    uint64_t gen_ns = exp_dist_next_arrival_ns(dist);
    uint32_t pkts_length = NUM_PKTS * sizeof(Message);
    for (uint8_t i = 0; i < NUM_PKTS; i++) {
      mbuf = rte_pktmbuf_alloc(pktmbuf_pool);
      if (work_ns == work_1_ns) {
        generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 0);
      } else if (work_ns == work_2_ns) {
        generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 1);
      } else if (work_ns == work_3_ns) {
        generate_packet(lcore_id, mbuf, i, pkts_length, gen_ns, work_ns, 2);
      }
      enqueue_pkt(lcore_id, mbuf);
    }
    req_id++;
    if (req_id_core[lcore_id] >= max_req_id) {
      req_id_core[lcore_id] = 0;
    } else {
      req_id_core[lcore_id]++;
    }
    while (get_cur_ns() < gen_ns)
      ;
    send_pkt_burst(lcore_id);
  }
  free_exp_dist(dist);
  free_trimodal_dist(work_dist);
}

static void tx_loop(uint32_t lcore_id) {
  if (strcmp(dist_type, "fixed") == 0) {
    fixed_tx_loop(lcore_id, 1000 * scale_factor);  // 1us
  } else if (strcmp(dist_type, "exp") == 0) {
    exp_tx_loop(lcore_id, 1000 * scale_factor);  // mu = 1us
  } else if (strcmp(dist_type, "lognormal") == 0) {
    lognormal_tx_loop(lcore_id, 1000 * scale_factor,
                      10000);  // mu = 1us, sigma = 10us
  } else if (strcmp(dist_type, "bimodal") == 0) {
    bimodal_tx_loop(lcore_id, 1000 * scale_factor, 10000 * scale_factor,
                    0.9);  // 99.5%: 10us, 0.5%: 1000us
  } else if (strcmp(dist_type, "port_bimodal") == 0) {
    port_bimodal_tx_loop(lcore_id, 1000 * scale_factor, 10000 * scale_factor,
                         0.5);  // 50%: 1us, 50%: 100us
  } else if (strcmp(dist_type, "port_trimodal") == 0) {
    port_trimodal_tx_loop(lcore_id, 1000 * scale_factor, 10000 * scale_factor,
                          100000 * scale_factor, 0.333,
                          0.333);  // 33.3%: 1us, 33.3%: 10us, 33.3%: 100us
  } else if (strcmp(dist_type, "db_bimodal") == 0) {
    // run_ns=0, SCAN;
    // 90%: GET, 10%: SCAN
    bimodal_tx_loop(lcore_id, 500 * scale_factor, 0 * scale_factor, 0.9);
  } else if (strcmp(dist_type, "db_port_bimodal") == 0) {
    port_bimodal_tx_loop(lcore_id, 1000 * scale_factor, 0 * scale_factor, 0.5);
  } else {
    rte_exit(EXIT_FAILURE, "Error: No matching distribution type found\n");
  }
}

static void rx_loop(uint32_t lcore_id) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  printf("%lld entering RX loop (master loop) on lcore %u\n",
         (long long)time(NULL), lcore_id);

  struct rte_mbuf *mbuf;
  struct rte_mbuf *mbuf_burst[MAX_BURST_SIZE];
  uint32_t i, j, nb_rx;

  while (1) {
    for (i = 0; i < lconf->n_rx_queue; i++) {
      nb_rx = rte_eth_rx_burst(lconf->port, lconf->rx_queue_list[i], mbuf_burst,
                               MAX_BURST_SIZE);
      for (j = 0; j < nb_rx; j++) {
        mbuf = mbuf_burst[j];
        rte_prefetch0(rte_pktmbuf_mtod(mbuf, void *));
        process_packet(lcore_id, mbuf);
        rte_pktmbuf_free(mbuf);
      }
    }
  }
}

// main processing loop for client
static int32_t client_loop(__attribute__((unused)) void *arg) {
  uint32_t lcore_id = rte_lcore_id();

  if (is_latency_client > 0) {
    if (lcore_id == 0) {
      rx_loop(lcore_id);
    } else {
      tx_loop(lcore_id);
    }
  } else {
    tx_loop(lcore_id);
  }

  return 0;
}

// initialization
static void custom_init(void) {
  if (is_latency_client > 0) {
    // init huge arrays to store results
    latency_results.sjrn_times =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
    latency_results.sjrn_times_long =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
    latency_results.sjrn_times_short =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
    latency_results.work_ratios =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
    latency_results.work_ratios_short =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
    latency_results.work_ratios_long =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
    latency_results.queue_lengths = (uint32_t(*)[3])rte_malloc(
        NULL, sizeof(uint32_t[3]) * MAX_RESULT_SIZE, 0);
    latency_results.reply_run_ns =
        (uint64_t *)rte_malloc(NULL, sizeof(uint64_t) * MAX_RESULT_SIZE, 0);
  }
  // initialize zipf
  zipf_state = malloc(sizeof(struct zipf_gen_state));
  zipf_init(zipf_state, client_num, zipf_alpha * 0.01, 2011);
  printf("\n=============== Finish initialization ===============\n\n");
}

/*
 * functions for parsing arguments
 */

static void parse_client_args_help(char *program_name) {
  fprintf(stderr,
          "Usage: %s -l <WORKING_CORES> -- -l <IS_LATENCY_CLIENT> -c "
          "<CLIENT_ID> -s <SERVER_ID> -d "
          "<DIST_TYPE> -q "
          "<QPS_PER_CORE>\n",
          program_name);
}

static int parse_client_args(int argc, char **argv) {
  int opt, num;
  while ((opt = getopt(argc, argv, "l:c:s:d:q:x:r:n:z:")) != -1) {
    switch (opt) {
      case 'l':
        num = atoi(optarg);
        is_latency_client = num;
        break;
      case 'c':
        num = atoi(optarg);
        client_index = num - 1;
        break;
      case 's':
        num = atoi(optarg);
        server_index = num - 1;
        break;
      case 'd':
        dist_type = optarg;
        break;
      case 'q':
        num = atoi(optarg);
        qps = num;
        break;
      case 'x':
        num = atoi(optarg);
        scale_factor = num;
        break;
      case 'r':
        num = atoi(optarg);
        is_rocksdb = num;
      case 'n':
        num = atoi(optarg);
        client_num = num;
      case 'z':
        num = atoi(optarg);
        zipf_alpha = num;
        break;
      default:
        parse_client_args_help(argv[0]);
        return -1;
    }
  }

  printf("\nType of client: %s\n",
         is_latency_client > 0 ? "Latency client" : "Batch client");
  printf("Client (src): %s\n", ip_client[client_index]);
  printf("Server (dst): %s\n", ip_server[server_index]);
  printf("Type of distribution: %s\n", dist_type);
  printf("QPS per core: %" PRIu32 "\n\n", qps);

  return 0;
}

/*
 * main function
 */

int main(int argc, char **argv) {
  int ret;
  uint32_t lcore_id;

  // parse eal arguments
  ret = rte_eal_init(argc, argv);
  if (ret < 0) {
    rte_exit(EXIT_FAILURE, "invalid EAL arguments\n");
  }
  argc -= ret;
  argv += ret;

  // parse client arguments
  ret = parse_client_args(argc, argv);
  if (ret < 0) {
    rte_exit(EXIT_FAILURE, "invalid client arguments\n");
  }

  // init
  init();
  custom_init();

  // launch main loop in every lcore
  rte_eal_mp_remote_launch(client_loop, NULL, CALL_MASTER);
  RTE_LCORE_FOREACH_SLAVE(lcore_id) {
    if (rte_eal_wait_lcore(lcore_id) < 0) {
      ret = -1;
      break;
    }
  }

  return 0;
}
