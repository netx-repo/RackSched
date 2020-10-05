#include <net/ether.h>
#include <rte_ethdev.h>
#include <rte_ip.h>
#include <rte_mbuf.h>
#include <net/ip.h>
#include <net/udp.h>
#include <ix/byteorder.h>

#include "ethqueue.h"
#include "networker.h"
#include "cfg.h"

int eth_fast_process(struct rte_mbuf *buf, struct recv_data_contents *recv_data) {
	size_t ip_offset = sizeof(struct ether_hdr);
	size_t udp_offset = ip_offset + sizeof(struct ipv4_hdr);
	size_t size_min = udp_offset + sizeof(struct udp_hdr);
	struct ipv4_hdr *ip;
	struct udp_hdr *udp;

	if (rte_pktmbuf_pkt_len(buf) < size_min ||
	    rte_pktmbuf_pkt_len(buf) != rte_pktmbuf_data_len(buf)) {
		return 1;
	}
	ip = rte_pktmbuf_mtod_offset(buf, struct ipv4_hdr *, ip_offset);
	udp = rte_pktmbuf_mtod_offset(buf, struct udp_hdr *, udp_offset);

	struct ip_addr src_ip = { .addr = ntoh32(ip->src_addr) };
        struct ip_addr dst_ip = { .addr = ntoh32(ip->dst_addr) };
        if (recv_data) {
                memcpy(&recv_data->tup.src_ip, &src_ip, sizeof(src_ip));
                memcpy(&recv_data->tup.dst_ip, &dst_ip, sizeof(dst_ip));
        }
	uint16_t src_port = ntoh16(udp->src_port);
        uint16_t dst_port = ntoh16(udp->dst_port);
        if (recv_data) {
                recv_data->tup.src_port = src_port;
                recv_data->tup.dst_port = dst_port;
                recv_data->payload = rte_pktmbuf_mtod_offset(buf, void *, size_min);
                recv_data->payload_len = rte_pktmbuf_pkt_len(buf) - sizeof(struct udp_hdr);
        }
	return 0;
}

/**
 * eth_process_recv - polls the specified queue for packets
 * sitting in the RX queue
 */
int eth_process_recv(struct eth_queue *queue, struct rte_mbuf **recv_mbufs,
		struct recv_data_contents *contents, size_t batch) {
	uint16_t nb_rx, nb_for_dispatcher = 0;
	size_t i, j;
	struct rte_mbuf *bufs[batch];
	/* Get burst of RX packets from the specified queue */
	nb_rx = rte_eth_rx_burst(queue->port, queue->queue, bufs, batch);

	j = 0;
	for (i = 0; i < nb_rx; i++) {
		//check that the packet is valid and that its destination
		//is one of the Shinjuku apps
		//if this is not the case, [eth_input] frees the mbuf
		if (eth_fast_process(bufs[i], &contents[j]) == 0) {
			//give to dispatcher
			recv_mbufs[j] = bufs[i];
			j++;
		} else {
			printf("Got invalid packet\n");
			rte_pktmbuf_free(bufs[i]);
		}
	}
	return j;
}

/**
 * send_to_dispatcher - sends a response to the dispatcher on the StingRay
 * queue - the queue to send out from (should be the queue for that worker)
 * buffer - an mbuf containing the data along with the various network
 * layers (UDP, IP, and Ethernet)... the src/dst MAC addresses will be 
 * overwritten, but nothing else (such as the port number, IP addresses, etc.),
 * so make sure the IP checksum, the UDP checksum, etc. is set properly
 * Note that you can only send one mbuf (rather than an array of mbufs), this
 * is done on purpose to emphasize that the worker should not be sending
 * multiple messages to the dispatcher (it should only send one until the
 * dispatcher responses)... I suppose you could call this function multiple
 * times before you receive a response but don't do that
 * worker_idx - the index of the worker that is sending data
 */
int send_to_dispatcher(struct eth_queue *queue, struct rte_mbuf *mbuf, size_t worker_idx) {
	struct ether_addr *worker_mac;
	uint16_t num_sent = 0;
	
	if (worker_idx >= CFG.num_workers) return -1;
	worker_mac = &CFG.workers[worker_idx];
	set_mac_addrs(mbuf, worker_mac, &CFG.dispatcher_addr);

	while (num_sent < 1) {
		num_sent += rte_eth_tx_burst(queue->port, queue->queue,
				&mbuf, 1);
	}
	return 0;
}

/**
 * send_worker_response - sends a response from the worker to the original
 * client
 * queue - the queue to send the response from
 * mbuf - the packet to send
 * to_mac - the MAC address of the machine that should receive the response
 * on the next hop
 * tup - the IP tuple
 */
int send_worker_response(struct eth_queue *queue, struct rte_mbuf *mbuf,
		struct ether_addr *to_mac, struct ip_tuple *tup, size_t worker_idx) {
	uint16_t num_sent = 0;

	//set_mac_addrs(mbuf, &CFG.workers[worker_idx], to_mac);

	set_ip_tuple(mbuf, tup);
	while (num_sent < 1) {
		num_sent += rte_eth_tx_burst(queue->port, queue->queue, &mbuf, 1);
	}
	return 0;
}

/**
 * construct_worker_response - creates an mbuf that contains the various
 * network headers (e.g. UDP, IP, and Ethernet) and contains the data
 * at [buffer] as the UDP payload
 * Note that this message is not constructed for a specific worker... the
 * actual IP address and MAC addresses are filled in by [send_to_dispatcher]
 * Returns a pointer to the mbuf (or NULL if an error occurred)
 */
struct rte_mbuf *construct_worker_response(void *buffer, size_t len) {
	struct ether_tuple ether_tup;
	struct ip_tuple ip_tup;

	// set the MAC addresses to zeroes because they are filled
	// in when the [send_to_worker] function is called
	memset(&ether_tup.src_addr, 0, sizeof(ether_tup.src_addr));
	memset(&ether_tup.dst_addr, 0, sizeof(ether_tup.dst_addr));

	// the IP addresses don't matter
	ip_tup.src_ip.addr = 0;
	ip_tup.dst_ip.addr = 0;
	// this message is a control message, so set the ports
	// accordingly
	ip_tup.src_port = CFG.worker_control_port;
	ip_tup.dst_port = CFG.worker_control_port;

	return generate_udp_packet(&ether_tup, &ip_tup, buffer, len);
}
