#pragma once

#include <rte_mbuf.h>
#include <rte_ip.h>

#define IP_ADDR_STR_LEN 16

// forward declaration since this struct is defined in
// ethqueue.h, which includes this header file (so don't
// want a cyclic dependency)
struct recv_data_contents;

struct ip_addr {
        uint32_t addr;
} __rte_packed;

struct ip_tuple {
	struct ip_addr src_ip;
	struct ip_addr dst_ip;
	uint16_t src_port;
	uint16_t dst_port;
} __packed;

void set_ip_tuple(struct rte_mbuf *pkt, struct ip_tuple *tup);
void ip_addr_to_str(struct ip_addr *addr, char *str);
int ip_input(struct rte_mbuf *pkt, struct ipv4_hdr *hdr, struct recv_data_contents *);
size_t ip_output(struct rte_mbuf *, struct ip_tuple *, uint8_t, size_t);

#define	IP_RF 0x8000			/* reserved fragment flag */
#define	IP_DF 0x4000			/* dont fragment flag */
#define	IP_MF 0x2000			/* more fragments flag */
#define	IP_OFFMASK 0x1fff		/* mask for fragmenting bits */
