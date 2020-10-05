#include <rte_ether.h>
#include <rte_udp.h>
#include <net/ip.h>
#include <net/udp.h>
#include <ix/byteorder.h>
#include "cfg.h"

int udp_input(struct rte_mbuf *pkt, struct ipv4_hdr *iphdr, struct udp_hdr *udphdr,
		struct recv_data_contents *recv_data) {
        int i;
	size_t data_offset = sizeof(struct ether_hdr) +
			     sizeof(struct ipv4_hdr) +
			     sizeof(struct udp_hdr);
        void *data = rte_pktmbuf_mtod_offset(pkt, void *, data_offset);
        uint16_t len = ntoh16(udphdr->dgram_len);
        struct ip_tuple *id;

	//TODO: Implement if needed
/*
        if (unlikely(!mbuf_enough_space(pkt, udphdr, len))) {
                mbuf_free(pkt);
                return -1; 
        }   
*/

	uint16_t src_port = ntoh16(udphdr->src_port);
        uint16_t dst_port = ntoh16(udphdr->dst_port);
	if (recv_data) {
		recv_data->tup.src_port = src_port;
		recv_data->tup.dst_port = dst_port;
		recv_data->payload = data;
		recv_data->payload_len = len - sizeof(struct udp_hdr);
	}
/*	printf("UDP Source Port: %u\n", src_port);
	printf("UDP Destination Port: %u\n", dst_port);
	printf("UDP Datagram Length: %u\n", len); */

        if (dst_port == 6666) {
            exit(0);
	}
        return 0; 
}

/**
 * udp_output - generate a UDP packet
 * pkt - the mbuf to fill in (must be zeroed out initially!)
 * tuple - contains the src/dst IP addresses and ports
 * buffer - the UDP payload (i.e. the data you want to send)
 * len - the length of [buffer]
 */
size_t udp_output(struct rte_mbuf *pkt, uint16_t src_port,
		uint16_t dst_port, void *buffer, size_t len) {
	size_t offset = sizeof(struct ether_hdr) +
			sizeof(struct ipv4_hdr);
	struct udp_hdr *udphdr = rte_pktmbuf_mtod_offset(pkt, 
			struct udp_hdr *, offset);
	// the length of the UDP header and payload
	// must be at least 8 (because this is the size of
	// the header)
	uint16_t dgram_len = sizeof(*udphdr) + len;

	udphdr->src_port = hton16(src_port);
	udphdr->dst_port = hton16(dst_port);
	udphdr->dgram_len = hton16(dgram_len);
	// the UDP checksum is optional in IPv4, so
	// I'm not going to deal with it
	udphdr->dgram_cksum = 0;

	void *buffer_dst = rte_pktmbuf_mtod_offset(pkt, void *, 
			offset + sizeof(*udphdr));
	memcpy(buffer_dst, buffer, len);
	return dgram_len;
}

void *get_udp_payload(struct rte_mbuf *pkt) {
	size_t offset = sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr) +
			sizeof(struct udp_hdr);
	return rte_pktmbuf_mtod_offset(pkt, void *, offset);
}
