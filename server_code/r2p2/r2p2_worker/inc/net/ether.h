#pragma once

#include <rte_ether.h>
#include <rte_mbuf.h>

#include "ethqueue.h"

struct ether_tuple {
	struct ether_addr src_addr;
	struct ether_addr dst_addr;
};

int eth_input(struct rte_mbuf *pkt, struct recv_data_contents *);
size_t ethernet_output(struct rte_mbuf *, struct ether_tuple *, uint16_t, size_t);
void set_mac_addrs(struct rte_mbuf *pkt, struct ether_addr *src,
		   struct ether_addr *dst);
struct ether_addr *
ether_aton_r (const char *asc, struct ether_addr *addr);
