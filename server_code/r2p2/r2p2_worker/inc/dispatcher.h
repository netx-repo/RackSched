#pragma once

#include <rte_mempool.h>

#include "cfg.h"

#define WAITING     0x00
#define ACTIVE      0x01

#define RUNNING     0x00
#define FINISHED    0x01
#define PREEMPTED   0x02
#define UNASSIGNED  0x03

#define NOCONTENT   0x00
#define PACKET      0x01
#define CONTEXT     0x02

#define MAX_UINT64  0xFFFFFFFFFFFFFFFF

//TODO: Optimize mempools to use cache (shouldn't be too hard)

struct message {
   uint8_t recir_flag;
   uint8_t core_idx;
   uint8_t type;
   uint16_t seq_num;
   uint32_t queue_length[3];
   uint16_t client_id;
   uint32_t req_id;
   uint32_t pkts_length;
   uint64_t run_ns;
   uint64_t gen_ns;
 } __attribute__((__packed__));


struct worker_response {
	uint64_t flag;
	// the worker id
	uint64_t worker;
	struct dispatcher_request *req;
} __rte_packed;

struct dispatcher_request {
	// this contains the address of the struct on
	// the ARM cores
	// this is needed because the dispatcher_request
	// struct is sent to workers and workers need to
	// know the address of the struct in StingRay
	// memory since they return the address to the
	// dispatcher in their worker_response struct (as
	// the [req] member) so that the dispatcher knows
	// where to go to get the original request details
	struct dispatcher_request *req;
	// the application that this request is for
	uint8_t type;
	// specifies whether this is a new packet
	// that the worker has never seen before
	// (PACKET) or if a worker has already
	// done some work on this request and thus
	// a context already exists (CONTEXT)
	uint8_t category;
	// the index of the context to use if [category]
	// is set to CONTEXT
	uint64_t context_idx;
	// the IP addresses and ports in the
	// request received from the client
	struct ip_tuple tup;
	// the MAC address that a response to the request
	// should be sent to (so that the workers do not
	// have to maintain their own ARP table)
	struct ether_addr resp_mac;
	// the cycle count when the networker
	// received the request
	uint64_t timestamp;
	size_t data_len;
	// the request data
	char data[CFG_MAX_PACKET_SIZE];
} __rte_packed;
