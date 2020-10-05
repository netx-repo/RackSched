#include <stdio.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <net/ip.h>
#include <net/udp.h>
#include <ix/byteorder.h>

uint16_t ip_id = 0;

void set_ip_tuple(struct rte_mbuf *pkt, struct ip_tuple *tup) {
	struct ipv4_hdr *iphdr;
	struct udp_hdr *udphdr;
	size_t offset = 0;

        if (!pkt || !tup) return;

	offset = sizeof(struct ether_hdr);
        iphdr = rte_pktmbuf_mtod_offset(pkt, struct ipv4_hdr *, offset);
	offset += sizeof(struct ipv4_hdr);
        udphdr = rte_pktmbuf_mtod_offset(pkt, struct udp_hdr *, offset);

	iphdr->src_addr = hton32(tup->src_ip.addr);
	iphdr->dst_addr = hton32(tup->dst_ip.addr);
	iphdr->hdr_checksum = 0;
	iphdr->hdr_checksum = rte_ipv4_cksum(iphdr);

	udphdr->src_port = hton16(tup->src_port);
	udphdr->dst_port = hton16(tup->dst_port);
}

/**
 * ip_addr_to_str - prints an IP address as a human-readable string
 * @addr: the ip address
 * @str: a buffer to store the string
 *
 * The buffer must be IP_ADDR_STR_LEN in size.
 */
void ip_addr_to_str(struct ip_addr *addr, char *str)
{
        snprintf(str, IP_ADDR_STR_LEN, "%d.%d.%d.%d",
                 ((addr->addr >> 24) & 0xff),
                 ((addr->addr >> 16) & 0xff),
                 ((addr->addr >> 8) & 0xff),
                 (addr->addr & 0xff));
}

int ip_input(struct rte_mbuf *pkt, struct ipv4_hdr *hdr,
		struct recv_data_contents *recv_data)
{       
        int version, hdrlen, pktlen, ret;
	size_t offset;

	hdrlen = hdr->version_ihl & 0x0F;
	version = (hdr->version_ihl & 0xF0) >> 4;
	hdrlen *= sizeof(uint32_t);
        /* check that the packet is long enough */
        if (rte_pktmbuf_pkt_len(pkt) < sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr)) {
                goto out;
	}
        /* check for IP version 4 */
        if (version != 4) {
                goto out;
	}
        /* the minimum legal IPv4 header length is 20 bytes (5 words) */
        if (hdrlen < 20) {
                goto out;
	}
        /* drop all IP fragment packets (unsupported) */
        if (ntoh16(hdr->fragment_offset) & (IP_OFFMASK | IP_MF)) {
                goto out;
	}
        
        pktlen = ntoh16(hdr->total_length);
        
        /* the ip total length must be large enough to hold the header */
        if (pktlen < hdrlen) {
                goto out;
	}
        //TODO: Make sure entire IP packet fits in the one mbuf (can it
	//ever extend across multiple mbufs?)
	//if (!mbuf_enough_space(pkt, hdr, pktlen))
        //        goto out;
        
        pktlen -= hdrlen;

	struct ip_addr src_ip = { .addr = ntoh32(hdr->src_addr) };
	struct ip_addr dst_ip = { .addr = ntoh32(hdr->dst_addr) };
	if (recv_data) {
		memcpy(&recv_data->tup.src_ip, &src_ip, sizeof(src_ip));
		memcpy(&recv_data->tup.dst_ip, &dst_ip, sizeof(dst_ip));
	}
/*
	char type[100];
	switch (hdr->next_proto_id) {
	case IPPROTO_TCP:
		strcpy(type, "TCP");
		break;
	case IPPROTO_UDP:
		strcpy(type, "UDP");
		break;
	case IPPROTO_ICMP:
		strcpy(type, "ICMP");
		break;
	default:
		strcpy(type, "Other");
		break;
	}
	printf("IP Protocol Type: %s\n", type);
	char src[100];
	char dst[100];

	ip_addr_to_str(&src_ip, src);
	ip_addr_to_str(&dst_ip, dst);
	printf("IP Source Address: %s\n", src);
	printf("IP Destination Address: %s\n", dst);
 */


        switch (hdr->next_proto_id) {
        case IPPROTO_TCP:
                printf("ip: dropping TCP packet\n");
                goto out;
        case IPPROTO_UDP:
		offset = sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr);
                ret = udp_input(pkt, hdr, rte_pktmbuf_mtod_offset(pkt, struct udp_hdr *, offset), recv_data);
                if (ret < 0) 
                        goto out;
                return ret;
        case IPPROTO_ICMP:
                printf("ip: dropping ICMP packet\n");
                goto out;
        default:
                goto out;
        }

out:    
        rte_pktmbuf_free(pkt);
        return -1;
}

size_t ip_output(struct rte_mbuf *pkt, struct ip_tuple *tuple, uint8_t proto_id,
		size_t dgram_len) {
	size_t offset = sizeof(struct ether_hdr);
	struct ipv4_hdr *iphdr = rte_pktmbuf_mtod_offset(pkt, 
		struct ipv4_hdr *, offset);
	size_t version = 4;
	// no additional options are included in the IP header,
	// so the length of the header is the minimum length
	// possible, which is 5 words
	size_t header_len = 5;
	size_t total_length = header_len * 4 + dgram_len;
	iphdr->version_ihl = ((version & 0xF) << 4) | (header_len & 0xF);
	iphdr->total_length = hton16(total_length);
	iphdr->packet_id = hton16(__sync_fetch_and_add(&ip_id, 1));
	iphdr->fragment_offset = hton16(0);
	// I just chose 20... doesn't really matter as long as it's
	// large enough for the number of hops the packet goes
	// through
	iphdr->time_to_live = 20;
	// generally is only going to be IPPROTO_UDP in this
	// application
	iphdr->next_proto_id = proto_id;
	iphdr->src_addr = hton32(tuple->src_ip.addr);
	iphdr->dst_addr = hton32(tuple->dst_ip.addr);

	iphdr->hdr_checksum = 0;
	iphdr->hdr_checksum = rte_ipv4_cksum(iphdr);

	// now pass this off to the Ethernet layer
	return total_length;
}
