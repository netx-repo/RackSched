#include <rte_mbuf.h>
#include <rte_ether.h>
#include <net/ether.h>
#include <net/ip.h>
#include <ix/byteorder.h>

/**
 * eth_input - process an ethernet packet
 * @pkt: the mbuf containing the packet
 */
int eth_input(struct rte_mbuf *pkt, struct recv_data_contents *content) {
        struct ether_hdr *ethhdr;
	size_t offset;

	ethhdr = rte_pktmbuf_mtod(pkt, struct ether_hdr *); 
	offset = sizeof(struct ether_hdr);

        if (ethhdr->ether_type == hton16(ETHER_TYPE_IPv4)) {
                return ip_input(pkt, rte_pktmbuf_mtod_offset(pkt, struct ipv4_hdr *, offset), content);
        } else {
                rte_pktmbuf_free(pkt);
                return -1; 
        }   
}

size_t ethernet_output(struct rte_mbuf *pkt, struct ether_tuple *tuple,
		uint16_t ether_type, size_t ip_len) {
	struct ether_hdr *ethhdr = rte_pktmbuf_mtod(pkt, 
		struct ether_hdr *);
	ethhdr->ether_type = hton16(ether_type);
	memcpy(&ethhdr->s_addr, &tuple->src_addr, sizeof(ethhdr->s_addr));
	memcpy(&ethhdr->d_addr, &tuple->dst_addr, sizeof(ethhdr->d_addr));

	return sizeof(*ethhdr) + ip_len;
}

/**
 * set_mac_addrs - set the src and dst MAC addresses in the packet
 * Assumes that the outermost layer of the [pkt] mbuf is an Ethernet
 * header
 */
void set_mac_addrs(struct rte_mbuf *pkt, struct ether_addr *src,
		   struct ether_addr *dst) {
        struct ether_hdr *ethhdr;
	if (!pkt || !src || !dst) return;

	ethhdr = rte_pktmbuf_mtod(pkt, struct ether_hdr *); 
	memcpy(&ethhdr->s_addr, src, sizeof(*src));
	memcpy(&ethhdr->d_addr, dst, sizeof(*dst));
}

struct ether_addr *
ether_aton_r (const char *asc, struct ether_addr *addr) {
  size_t cnt;
  for (cnt = 0; cnt < 6; ++cnt)
    {   
      unsigned int number;
      char ch; 
      ch = _tolower (*asc++);
      if ((ch < '0' || ch > '9') && (ch < 'a' || ch > 'f'))
        return NULL;
      number = isdigit (ch) ? (ch - '0') : (ch - 'a' + 10);
      ch = _tolower (*asc);
      if ((cnt < 5 && ch != ':') || (cnt == 5 && ch != '\0' && !isspace (ch)))
        {   
          ++asc;
          if ((ch < '0' || ch > '9') && (ch < 'a' || ch > 'f'))
            return NULL;
          number <<= 4;
          number += isdigit (ch) ? (ch - '0') : (ch - 'a' + 10);
          ch = *asc;
          if (cnt < 5 && ch != ':')
            return NULL;
        }   
      /* Store result.  */
      addr->addr_bytes[cnt] = (unsigned char) number;
      /* Skip ':'.  */
      ++asc;
    }   
  return addr;
}
