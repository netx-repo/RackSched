/*
 * Copyright 2013-16 Board of Trustees of Stanford University
 * Copyright 2013-16 Ecole Polytechnique Federale Lausanne (EPFL)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

/*
 * ethqueue.h - ethernet queue support
 */

#pragma once

#include <stddef.h>
#include <rte_mbuf.h>
#include <net/ether.h>
#include <net/ip.h>

#define ETH_DEV_RX_QUEUE_SZ     512
#define ETH_DEV_TX_QUEUE_SZ     4096
#define ETH_RX_MAX_DEPTH	32768

struct recv_data_contents {
	struct ip_tuple tup;
	void *payload;
	size_t payload_len;
};

struct eth_queue {
	size_t port;
	size_t queue;
} __attribute((packed, aligned));

int eth_process_recv(struct eth_queue *, struct rte_mbuf **, struct recv_data_contents *, size_t);
int send_to_dispatcher(struct eth_queue *, struct rte_mbuf *, size_t);
int send_worker_response(struct eth_queue *queue, struct rte_mbuf *mbuf,
		struct ether_addr *to_mac, struct ip_tuple *tup, size_t worker_idx);
struct rte_mbuf *construct_worker_response(void *, size_t);
