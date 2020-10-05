#include <rte_mbuf.h>
#include <rte_ip.h>
#include <rte_udp.h>
#include "ethqueue.h"

int udp_input(struct rte_mbuf *pkt, struct ipv4_hdr *iphdr, struct udp_hdr *udphdr, struct recv_data_contents *);
size_t udp_output(struct rte_mbuf *, uint16_t, uint16_t, void *, size_t);
void *get_udp_payload(struct rte_mbuf *pkt);
