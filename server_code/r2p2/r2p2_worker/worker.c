#include <stdbool.h>
#include <rte_ethdev.h>

#include "networker.h"
#include "ethqueue.h"
#include "dispatcher.h"
#include "cfg.h"

__thread uint64_t worker_idx;

struct eth_queue worker_eth_queues[CFG_MAX_WORKERS];

__attribute__((noreturn)) int do_work(void *args) {
	printf("Worker %lu doing work\n", (size_t)args);
	worker_idx = (size_t)args;
	struct message *msg;
	struct recv_data_contents contents[32];
	struct dispatcher_request *req;
	struct rte_mbuf *recv_mbuf[32];
	struct rte_mbuf *pkt;

	while (true) {
                int num_recv = eth_process_recv(&worker_eth_queues[worker_idx],
                                &recv_mbuf, contents, 32);
                if (num_recv <= 0)
			continue;
		// printf("Worker %lu received requests\n", (size_t)args);
		for (int j = 0; j < num_recv; j++) {
			msg = (struct message *)contents[j].payload;
			// printf("Worker %lu doing work run_ns: %lu\n",worker_idx, msg->run_ns);
			uint64_t i = 0;
			do {
				asm volatile ("nop");
				i++;
			} while ( i / 0.58 < msg->run_ns);

			struct message resp;
			resp.gen_ns = msg->gen_ns;
			resp.run_ns = msg->run_ns;
			// resp.core_idx = worker_idx;
			resp.core_idx = 0;
			if (worker_idx > 0)
				resp.core_idx = worker_idx-1;

			struct ip_tuple new_id = {
				.src_ip = contents[j].tup.dst_ip,
				.dst_ip = contents[j].tup.src_ip,
				.src_port = contents[j].tup.dst_port,
				.dst_port = contents[j].tup.src_port
			};

			pkt = construct_worker_response(&resp, sizeof(resp));
			if (unlikely(!pkt)) rte_exit(1, "Could not create worker response");

			int ret = send_worker_response(&worker_eth_queues[worker_idx], pkt, &req->resp_mac, &new_id, worker_idx);
        		if (unlikely(ret)) rte_exit(1, "Could not send worker response");

			rte_pktmbuf_free(recv_mbuf[j]);
		}
	}
}

void start_workers() {
	size_t i;
	int ret;
	for (i = 1; i < CFG.num_workers; i++) {
		ret = rte_eal_remote_launch(do_work, (void *)i, i);
		if (ret) rte_exit(1, "Could not start worker %lu", i);
	}
	// TODO: Does the main thread always get pinned to 0?
	do_work((void *)0);
}

int init_workers() {
	return 0;
}
