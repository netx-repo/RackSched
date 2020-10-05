#include <stdbool.h>
#include <rte_mbuf.h>
#include <rte_cycles.h>
#include <net/ether.h>
#include <net/ip.h>
#include <net/udp.h>

#include "networker.h"
#include "cfg.h"
#include "dpdk.h"

/**
 * generate_udp_packet - generate a UDP packet and return a pointer
 * to the mbuf
 * Some of the initialization code is borrowed from:
 * https://github.com/ceph/dpdk/blob/master/app/test/test_mbuf.c
 */
struct rte_mbuf *generate_udp_packet(struct ether_tuple *ether_tup,
		struct ip_tuple *ip_tup,
		void *payload, size_t payload_len) {
	struct rte_mbuf *pkt = NULL;
	void *start = NULL;
	size_t dgram_len = 0;
	size_t ip_len = 0;
	size_t eth_len = 0;
	size_t max_payload_len = CFG_MAX_PACKET_SIZE -
			sizeof(struct ether_hdr) - sizeof(struct ipv4_hdr) -
			sizeof(struct udp_hdr);

	if (payload_len > max_payload_len) return NULL;

	pkt = rte_pktmbuf_alloc(mbuf_main_pool);
	if (!pkt) return NULL;
	if (rte_pktmbuf_pkt_len(pkt) != 0) return NULL;

	start = rte_pktmbuf_append(pkt, CFG_MAX_PACKET_SIZE);
	if (!start) return NULL;

	if (rte_pktmbuf_pkt_len(pkt) != CFG_MAX_PACKET_SIZE) return NULL;
	if (rte_pktmbuf_data_len(pkt) != CFG_MAX_PACKET_SIZE) return NULL;
	if (!rte_pktmbuf_is_contiguous(pkt)) return NULL;

	memset(start, 0, rte_pktmbuf_pkt_len(pkt));
	dgram_len = udp_output(pkt, ip_tup->src_port, ip_tup->dst_port,
		payload, payload_len);
	ip_len = ip_output(pkt, ip_tup, IPPROTO_UDP, dgram_len);
	eth_len = ethernet_output(pkt, ether_tup, ETHER_TYPE_IPv4, ip_len);

	pkt->pkt_len = eth_len;
	pkt->data_len = eth_len;

	return pkt;
}
