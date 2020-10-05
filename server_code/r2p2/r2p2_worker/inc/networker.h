#pragma once

#include <stdio.h>

#include <net/ip.h>
#include "ethqueue.h"

struct rte_mbuf *generate_udp_packet(struct ether_tuple *,
		struct ip_tuple *, void *, size_t);
