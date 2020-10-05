#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>

#include "cfg.h"
#include "dpdk.h"
#include "context.h"
#include "worker.h"

// this is a list of all of the initialization functions
// the main function loops through this array and calls
// each function
int (*init_functions[])() = { 
				init_config, 
				init_dpdk,
				init_workers
			    };


int main(int argc, char *argv[]) {
	int ret;
	size_t i, num_init_functions;

	num_init_functions = sizeof(init_functions) / sizeof(int (*)());
	for (size_t i = 0; i < num_init_functions; i++) {
		ret = init_functions[i]();
		if (ret) {
			printf("Initialization function %lu returned error %d\n", i, ret);
			return ret;
		}
	}
	printf("Initialization functions ran successfully.\n");

        start_workers();
	return 0;
}
