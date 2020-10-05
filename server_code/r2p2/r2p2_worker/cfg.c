#include <rte_debug.h>
#include <rte_ether.h>

#include "cfg.h"

int init_config()
{
	// ----- MAC address initialization -----
	//ether_aton_r("00:10:18:ad:05:04", &CFG.dispatcher_addr);

	// ----- Port initialization -----
	CFG.worker_control_port = 10000;

	// ----- Worker information -----
	CFG.num_contexts = 200000;
	CFG.num_workers = 9;
	RTE_ASSERT(CFG.num_workers <= CFG_MAX_WORKERS);
	ether_aton_r("3c:fd:fe:c3:e9:b0", &CFG.workers[0]);
	ether_aton_r("00:00:00:00:00:01", &CFG.workers[1]);
	ether_aton_r("00:00:00:00:00:02", &CFG.workers[2]);
	ether_aton_r("00:00:00:00:00:03", &CFG.workers[3]);
	ether_aton_r("00:00:00:00:00:04", &CFG.workers[4]);
	ether_aton_r("00:00:00:00:00:05", &CFG.workers[5]);
	ether_aton_r("00:00:00:00:00:06", &CFG.workers[6]);
	ether_aton_r("00:00:00:00:00:07", &CFG.workers[7]);
	ether_aton_r("00:00:00:00:00:08", &CFG.workers[8]);

	// ether_aton_r("00:00:00:00:00:01", &CFG.workers[0]);
	// ether_aton_r("00:00:00:00:00:02", &CFG.workers[1]);
	// ether_aton_r("00:00:00:00:00:03", &CFG.workers[2]);
	// ether_aton_r("00:00:00:00:00:04", &CFG.workers[3]);
	// ether_aton_r("00:00:00:00:00:05", &CFG.workers[4]);
	// ether_aton_r("00:00:00:00:00:06", &CFG.workers[5]);
	// ether_aton_r("00:00:00:00:00:07", &CFG.workers[6]);
	// ether_aton_r("00:00:00:00:00:08", &CFG.workers[7]);
	/*
	ether_aton_r("82:42:54:28:41:29", &CFG.workers[1]);
	ether_aton_r("9a:a4:6e:19:9f:9f", &CFG.workers[2]);
	ether_aton_r("36:e3:b4:76:bb:26", &CFG.workers[3]);
	ether_aton_r("5e:36:75:5b:fb:d6", &CFG.workers[4]);
	ether_aton_r("0e:61:33:0f:b3:fc", &CFG.workers[5]);
	ether_aton_r("52:a8:e7:0c:dc:4c", &CFG.workers[6]);
	ether_aton_r("c6:92:c6:2f:8d:8b", &CFG.workers[7]);
	*/
	/*
	ether_aton_r("c2:f1:5c:07:cc:ff", &CFG.workers[8]);
	ether_aton_r("42:b5:6d:23:78:39", &CFG.workers[9]);
	ether_aton_r("72:93:bc:1e:e0:dd", &CFG.workers[10]);
	ether_aton_r("0e:29:0d:c9:57:88", &CFG.workers[11]);
	ether_aton_r("2e:71:01:45:2a:a0", &CFG.workers[12]);
	ether_aton_r("a6:a6:64:c0:a7:0b", &CFG.workers[13]);
	ether_aton_r("a6:ac:b4:b3:77:fe", &CFG.workers[14]);
	ether_aton_r("3a:7c:b6:6b:73:11", &CFG.workers[15]);
	*/
	CFG.preempt_vector = 0xF2;
	// the clock has a frequency of 100 MHz
	// 5 microseconds = 500 cycles = 0x1F4
	CFG.preempt_time_slice = 0x1F4;

	return 0;
}
