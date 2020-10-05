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
 * cfg.h - configuration parameters
 */

#pragma once

#include <rte_ether.h>

#include <net/ether.h>
#include <net/ip.h>

#define CFG_APP_NAME     "shinjuku"

#define CFG_MAX_CPU		128
#define CFG_MAX_ETHDEV		16
#define CFG_MAX_WORKERS		1000
#define CFG_MAX_PACKET_SIZE	1500

#define TASK_CAPACITY (768 * 1024)

struct cfg_parameters {
	struct ether_addr dispatcher_addr;

	/* control messages sent between the dispatcher and the workers
	 * use this port
	 */
	uint16_t worker_control_port;

	uint64_t num_contexts;
	size_t num_workers;
	struct ether_addr workers[CFG_MAX_WORKERS];

	// the virtual vector that is delivered when the timer fires (the
	// physical posted interrupt vector is set in the Dune module)
	int preempt_vector;
	// the time set in the local APIC timer (this value is the number
	// of cycles that the timer must count before it fires, as this is
	// the unit specified in the Intel manual... on goliath-1, the timer
	// runs with a frequency of 100 MHz, so you can get the timer to fire
	// after 1 second if you set this to 100,000,000)
	uint64_t preempt_time_slice;
};

struct cfg_parameters CFG;

int init_config();
