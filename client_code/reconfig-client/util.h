#ifndef UTIL_H_
#define UTIL_H_

#include <gsl/gsl_randist.h>
#include <gsl/gsl_rng.h>
#include <time.h>

/*
 * constants
 */

#define TYPE_REQ 1
#define TYPE_REQ_FOLLOW 2
#define TYPE_RES 0

#define NB_MBUF 8191
#define MBUF_SIZE (2048 + sizeof(struct rte_mbuf) + RTE_PKTMBUF_HEADROOM)
#define MBUF_CACHE_SIZE 32
#define MAX_BURST_SIZE 32
#define MAX_LCORES 32
#define NB_RXD 128  // RX descriptors
#define NB_TXD 512  // TX descriptors
#define RX_QUEUE_PER_LCORE 4

#define IP_SRC "10.1.0.12"
#define IP_DST "10.1.0.1"
#define CLIENT_PORT 11234
#define SERVICE_PORT 1234

static const struct rte_eth_conf port_conf = {
    .rxmode =
        {
            .max_rx_pkt_len = ETHER_MAX_LEN,
            .split_hdr_size = 0,
            .header_split = 0,    // Header Split disabled
            .hw_ip_checksum = 0,  // IP checksum offload disabled
            .hw_vlan_filter = 0,  // VLAN filtering disabled
            .jumbo_frame = 0,     // Jumbo Frame Support disabled
            .hw_strip_crc = 0,    // CRC stripped by hardware
        },
    .txmode =
        {
            .mq_mode = ETH_MQ_TX_NONE,
        },
};

/*
 * custom types
 */

/********* Misc *********/

// Get current time in ns
uint64_t get_cur_ns() {
  struct timespec ts;
  clock_gettime(CLOCK_REALTIME, &ts);
  uint64_t t = ts.tv_sec * 1000 * 1000 * 1000 + ts.tv_nsec;
  return t;
}

// For storing results
typedef struct LatencyResults_ {
  uint64_t *sjrn_times;
  uint64_t *sjrn_times_short;
  uint64_t *sjrn_times_long;
  uint64_t *work_ratios;
  uint64_t *work_ratios_short;
  uint64_t *work_ratios_long;
  uint32_t (*queue_lengths)[3];
  uint64_t *reply_run_ns;
  size_t count;
  size_t count_short;
  size_t count_long;
} LatencyResults;

/********* Distributions *********/

// Exponential Distribution
typedef struct ExpDist_ {
  gsl_rng *r;
  double mu;
  uint64_t cur_ns;
} ExpDist;

void init_exp_dist(ExpDist *exp_dist, double mu) {
  gsl_rng_env_setup();
  const gsl_rng_type *T = gsl_rng_default;
  gsl_rng *r = gsl_rng_alloc(T);
  uint64_t cur_ns = get_cur_ns();
  ExpDist temp_exp_dist = {r, mu, cur_ns};
  memcpy(exp_dist, &temp_exp_dist, sizeof(ExpDist));
}

uint64_t exp_dist_next_arrival_ns(ExpDist *exp_dist) {
  exp_dist->cur_ns += gsl_ran_exponential(exp_dist->r, exp_dist->mu);
  return exp_dist->cur_ns;
}

uint64_t exp_dist_work_ns(ExpDist *exp_dist) {
  return gsl_ran_exponential(exp_dist->r, exp_dist->mu);
}

void free_exp_dist(const ExpDist *exp_dist) {
  gsl_rng_free(exp_dist->r);
  free((void *)exp_dist);
}

// Lognormal Distribution
typedef struct LognormalDist_ {
  gsl_rng *r;
  double mu;
  double sigma;
} LognormalDist;

void init_lognormal_dist(LognormalDist *lognormal_dist, double mu,
                         double sigma) {
  gsl_rng_env_setup();
  const gsl_rng_type *T = gsl_rng_default;
  gsl_rng *r = gsl_rng_alloc(T);
  LognormalDist temp_lognormal_dist = {r, mu, sigma};
  memcpy(lognormal_dist, &temp_lognormal_dist, sizeof(LognormalDist));
}

uint64_t lognormal_dist_work_ns(LognormalDist *lognormal_dist) {
  return gsl_ran_lognormal(lognormal_dist->r, lognormal_dist->mu,
                           lognormal_dist->sigma);
}

void free_lognormal_dist(LognormalDist *lognormal_dist) {
  gsl_rng_free(lognormal_dist->r);
  free((void *)lognormal_dist);
}

// Bimodal Distribution
typedef struct BimodalDist_ {
  gsl_rng *r;
  uint64_t work_1;
  uint64_t work_2;
  double ratio;
} BimodalDist;

void init_bimodal_dist(BimodalDist *bimodal_dist, uint64_t work_1_ns,
                       uint64_t work_2_ns, double ratio) {
  gsl_rng_env_setup();
  const gsl_rng_type *T = gsl_rng_default;
  gsl_rng *r = gsl_rng_alloc(T);
  BimodalDist temp_bimodal_dist = {r, work_1_ns, work_2_ns, ratio};
  memcpy(bimodal_dist, &temp_bimodal_dist, sizeof(BimodalDist));
}

uint64_t bimodal_dist_work_ns(BimodalDist *bimodal_dist) {
  double num = gsl_ran_flat(bimodal_dist->r, 0.0, 1.0);
  if (num < bimodal_dist->ratio) {
    return bimodal_dist->work_1;
  } else {
    return bimodal_dist->work_2;
  }
}

void free_bimodal_dist(BimodalDist *bimodal_dist) {
  gsl_rng_free(bimodal_dist->r);
  free((void *)bimodal_dist);
}

// Trimodal Distribution
typedef struct TrimodalDist_ {
  gsl_rng *r;
  uint64_t work_1;
  uint64_t work_2;
  uint64_t work_3;
  double ratio1;
  double ratio2;
} TrimodalDist;

void init_trimodal_dist(TrimodalDist *trimodal_dist, uint64_t work_1_ns,
                        uint64_t work_2_ns, uint64_t work_3_ns, double ratio1,
                        double ratio2) {
  gsl_rng_env_setup();
  const gsl_rng_type *T = gsl_rng_default;
  gsl_rng *r = gsl_rng_alloc(T);
  TrimodalDist temp_trimodal_dist = {
      r, work_1_ns, work_2_ns, work_3_ns, ratio1, ratio2,
  };
  memcpy(trimodal_dist, &temp_trimodal_dist, sizeof(TrimodalDist));
}

uint64_t trimodal_dist_work_ns(TrimodalDist *trimodal_dist) {
  double num = gsl_ran_flat(trimodal_dist->r, 0.0, 1.0);
  if (num < trimodal_dist->ratio1) {
    return trimodal_dist->work_1;
  } else if (num < trimodal_dist->ratio1 + trimodal_dist->ratio2) {
    return trimodal_dist->work_2;
  } else {
    return trimodal_dist->work_3;
  }
}

void free_trimodal_dist(TrimodalDist *trimodal_dist) {
  gsl_rng_free(trimodal_dist->r);
  free((void *)trimodal_dist);
}

typedef struct Message_ {
  uint8_t type;
  uint16_t seq_num;
  uint32_t queue_length[3];
  uint16_t client_id;
  uint32_t req_id;
  uint32_t pkts_length;
  uint64_t run_ns;
  uint64_t gen_ns;
} __attribute__((__packed__)) Message;

struct mbuf_table {
  uint32_t len;
  struct rte_mbuf *m_table[MAX_BURST_SIZE];
};

struct lcore_configuration {
  uint32_t vid;                                // virtual core id
  uint32_t port;                               // one port
  uint32_t tx_queue_id;                        // one TX queue
  uint32_t n_rx_queue;                         // number of RX queues
  uint32_t rx_queue_list[RX_QUEUE_PER_LCORE];  // list of RX queues
  struct mbuf_table tx_mbufs;                  // mbufs to hold TX queue
} __rte_cache_aligned;

/*
 * global variables
 */

uint32_t enabled_port_mask = 1;
uint32_t enabled_ports[RTE_MAX_ETHPORTS];
uint32_t n_enabled_ports = 0;
uint32_t n_rx_queues = 0;
uint32_t n_lcores = 0;

struct rte_mempool *pktmbuf_pool = NULL;
struct ether_addr port_eth_addrs[RTE_MAX_ETHPORTS];
struct lcore_configuration lcore_conf[MAX_LCORES];

uint8_t header_template[sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr) +
                        sizeof(struct udp_hdr)];

/*
 * functions for generation
 */

// send packets, drain TX queue
static void send_pkt_burst(uint32_t lcore_id) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  struct rte_mbuf **m_table = (struct rte_mbuf **)lconf->tx_mbufs.m_table;

  uint32_t n = lconf->tx_mbufs.len;
  uint32_t ret = rte_eth_tx_burst(lconf->port, lconf->tx_queue_id, m_table,
                                  lconf->tx_mbufs.len);
  if (unlikely(ret < n)) {
    do {
      rte_pktmbuf_free(m_table[ret]);
    } while (++ret < n);
  }
  lconf->tx_mbufs.len = 0;
}

// put packet into TX queue
static void enqueue_pkt(uint32_t lcore_id, struct rte_mbuf *mbuf) {
  struct lcore_configuration *lconf = &lcore_conf[lcore_id];
  lconf->tx_mbufs.m_table[lconf->tx_mbufs.len++] = mbuf;

  // enough packets in TX queue
  if (unlikely(lconf->tx_mbufs.len == MAX_BURST_SIZE)) {
    send_pkt_burst(lcore_id);
  }
}

/*
 * functions for initialization
 */

// init header template
static void init_header_template(void) {
  memset(header_template, 0, sizeof(header_template));
  struct ether_hdr *eth = (struct ether_hdr *)header_template;
  struct ipv4_hdr *ip =
      (struct ipv4_hdr *)((uint8_t *)eth + sizeof(struct ether_hdr));
  struct udp_hdr *udp =
      (struct udp_hdr *)((uint8_t *)ip + sizeof(struct ipv4_hdr));
  uint32_t pkt_len = sizeof(header_template) + sizeof(Message);

  // eth header
  eth->ether_type = rte_cpu_to_be_16(ETHER_TYPE_IPv4);
  struct ether_addr src_addr = {
      .addr_bytes = {0xaa, 0xbb, 0xcc, 0xdd, 0xee, 0xff}};
  struct ether_addr dst_addr = {
      .addr_bytes = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}};
  ether_addr_copy(&src_addr, &eth->s_addr);
  ether_addr_copy(&dst_addr, &eth->d_addr);

  // ip header
  char src_ip[] = IP_SRC;
  char dst_ip[] = IP_DST;
  int st1 = inet_pton(AF_INET, src_ip, &(ip->src_addr));
  int st2 = inet_pton(AF_INET, dst_ip, &(ip->dst_addr));
  if (st1 != 1 || st2 != 1) {
    fprintf(stderr, "inet_pton() failed.Error message: %s %s", strerror(st1),
            strerror(st2));
    exit(EXIT_FAILURE);
  }
  ip->total_length = rte_cpu_to_be_16(pkt_len - sizeof(struct ether_hdr));
  ip->version_ihl = 0x45;
  ip->type_of_service = 0;
  ip->packet_id = 0;
  ip->fragment_offset = 0;
  ip->time_to_live = 64;
  ip->next_proto_id = IPPROTO_UDP;
  uint32_t ip_cksum;
  uint16_t *ptr16 = (uint16_t *)ip;
  ip_cksum = 0;
  ip_cksum += ptr16[0];
  ip_cksum += ptr16[1];
  ip_cksum += ptr16[2];
  ip_cksum += ptr16[3];
  ip_cksum += ptr16[4];
  ip_cksum += ptr16[6];
  ip_cksum += ptr16[7];
  ip_cksum += ptr16[8];
  ip_cksum += ptr16[9];
  ip_cksum = ((ip_cksum & 0xffff0000) >> 16) + (ip_cksum & 0x0000ffff);
  if (ip_cksum > 65535) {
    ip_cksum -= 65535;
  }
  ip_cksum = (~ip_cksum) & 0x0000ffff;
  if (ip_cksum == 0) {
    ip_cksum = 0xffff;
  }
  ip->hdr_checksum = (uint16_t)ip_cksum;

  // udp header
  udp->src_port = htons(CLIENT_PORT);
  udp->dst_port = htons(SERVICE_PORT);
  udp->dgram_len = rte_cpu_to_be_16(pkt_len - sizeof(struct ether_hdr) -
                                    sizeof(struct ipv4_hdr));
  udp->dgram_cksum = 0;
}

// check link status
static void check_link_status(void) {
  const uint32_t check_interval_ms = 100;
  const uint32_t check_iterations = 90;
  uint32_t i, j;
  struct rte_eth_link link;
  for (i = 0; i < check_iterations; i++) {
    uint8_t all_ports_up = 1;
    for (j = 0; j < n_enabled_ports; j++) {
      uint32_t portid = enabled_ports[j];
      memset(&link, 0, sizeof(link));
      rte_eth_link_get_nowait(portid, &link);
      if (link.link_status) {
        printf("\tport %u link up - speed %u Mbps - %s\n", portid,
               link.link_speed,
               (link.link_duplex == ETH_LINK_FULL_DUPLEX) ? "full-duplex"
                                                          : "half-duplex");
      } else {
        all_ports_up = 0;
      }
    }

    if (all_ports_up == 1) {
      printf("check link status finish: all ports are up\n");
      break;
    } else if (i == check_iterations - 1) {
      printf("check link status finish: not all ports are up\n");
    } else {
      rte_delay_ms(check_interval_ms);
    }
  }
}

// initialize all status
static void init(void) {
  uint32_t i, j;

  // create mbuf pool
  printf("create mbuf pool\n");
  pktmbuf_pool = rte_mempool_create(
      "mbuf_pool", NB_MBUF, MBUF_SIZE, MBUF_CACHE_SIZE,
      sizeof(struct rte_pktmbuf_pool_private), rte_pktmbuf_pool_init, NULL,
      rte_pktmbuf_init, NULL, rte_socket_id(), 0);
  if (pktmbuf_pool == NULL) {
    rte_exit(EXIT_FAILURE, "cannot init mbuf pool\n");
  }

  // determine available ports
  printf("create enabled ports\n");
  uint32_t n_total_ports = 0;
  n_total_ports = rte_eth_dev_count();

  if (n_total_ports == 0) {
    rte_exit(EXIT_FAILURE, "cannot detect ethernet ports\n");
  }
  if (n_total_ports > RTE_MAX_ETHPORTS) {
    n_total_ports = RTE_MAX_ETHPORTS;
  }

  // get info for each enabled port
  struct rte_eth_dev_info dev_info;
  n_enabled_ports = 0;
  printf("\tports: ");
  for (i = 0; i < n_total_ports; i++) {
    if ((enabled_port_mask & (1 << i)) == 0) {
      continue;
    }
    enabled_ports[n_enabled_ports++] = i;
    rte_eth_dev_info_get(i, &dev_info);
    printf("%u ", i);
  }
  printf("\n");

  // find number of active lcores
  printf("create enabled cores\n\tcores: ");
  n_lcores = 0;
  for (i = 0; i < MAX_LCORES; i++) {
    if (rte_lcore_is_enabled(i)) {
      n_lcores++;
      printf("%u ", i);
    }
  }

  // ensure numbers are correct
  if (n_lcores % n_enabled_ports != 0) {
    rte_exit(EXIT_FAILURE,
             "number of cores (%u) must be multiple of ports (%u)\n", n_lcores,
             n_enabled_ports);
  }

  uint32_t rx_queues_per_lcore = RX_QUEUE_PER_LCORE;
  uint32_t rx_queues_per_port =
      rx_queues_per_lcore * n_lcores / n_enabled_ports;
  uint32_t tx_queues_per_port = n_lcores / n_enabled_ports;

  if (rx_queues_per_port < rx_queues_per_lcore) {
    rte_exit(EXIT_FAILURE,
             "rx_queues_per_port (%u) must be >= rx_queues_per_lcore (%u)\n",
             rx_queues_per_port, rx_queues_per_lcore);
  }

  // assign each lcore some RX queues and a port
  printf("set up %d RX queues per port and %d TX queues per port\n",
         rx_queues_per_port, tx_queues_per_port);
  uint32_t portid_offset = 0;
  uint32_t rx_queue_id = 0;
  uint32_t tx_queue_id = 0;
  uint32_t vid = 0;
  for (i = 0; i < MAX_LCORES; i++) {
    if (rte_lcore_is_enabled(i)) {
      lcore_conf[i].vid = vid++;
      lcore_conf[i].n_rx_queue = rx_queues_per_lcore;
      for (j = 0; j < rx_queues_per_lcore; j++) {
        lcore_conf[i].rx_queue_list[j] = rx_queue_id++;
      }
      lcore_conf[i].port = enabled_ports[portid_offset];
      lcore_conf[i].tx_queue_id = tx_queue_id++;
      if (rx_queue_id % rx_queues_per_port == 0) {
        portid_offset++;
        rx_queue_id = 0;
        tx_queue_id = 0;
      }
    }
  }

  // initialize each port
  for (portid_offset = 0; portid_offset < n_enabled_ports; portid_offset++) {
    uint32_t portid = enabled_ports[portid_offset];

    int32_t ret = rte_eth_dev_configure(portid, rx_queues_per_port,
                                        tx_queues_per_port, &port_conf);
    if (ret < 0) {
      rte_exit(EXIT_FAILURE, "cannot configure device: err=%d, port=%u\n", ret,
               portid);
    }
    rte_eth_macaddr_get(portid, &port_eth_addrs[portid]);

    // initialize RX queues
    for (i = 0; i < rx_queues_per_port; i++) {
      ret = rte_eth_rx_queue_setup(
          portid, i, NB_RXD, rte_eth_dev_socket_id(portid), NULL, pktmbuf_pool);
      if (ret < 0) {
        rte_exit(EXIT_FAILURE, "rte_eth_rx_queue_setup: err=%d, port=%u\n", ret,
                 portid);
      }
    }

    // initialize TX queues
    for (i = 0; i < tx_queues_per_port; i++) {
      ret = rte_eth_tx_queue_setup(portid, i, NB_TXD,
                                   rte_eth_dev_socket_id(portid), NULL);
      if (ret < 0) {
        rte_exit(EXIT_FAILURE, "rte_eth_tx_queue_setup: err=%d, port=%u\n", ret,
                 portid);
      }
    }

    // start device
    ret = rte_eth_dev_start(portid);
    if (ret < 0) {
      rte_exit(EXIT_FAILURE, "rte_eth_dev_start: err=%d, port=%u\n", ret,
               portid);
    }

    rte_eth_promiscuous_enable(portid);

    char mac_buf[ETHER_ADDR_FMT_SIZE];
    ether_format_addr(mac_buf, ETHER_ADDR_FMT_SIZE, &port_eth_addrs[portid]);
    printf("initiaze queues and start port %u, MAC address:%s\n", portid,
           mac_buf);
  }

  if (!n_enabled_ports) {
    rte_exit(EXIT_FAILURE,
             "all available ports are disabled. Please set portmask.\n");
  }
  check_link_status();
  init_header_template();
}

/*
 * misc
 */

static uint64_t timediff_in_us(uint64_t new_t, uint64_t old_t) {
  return (new_t - old_t) * 1000000UL / rte_get_tsc_hz();
}

#endif  // UTIL_H_
