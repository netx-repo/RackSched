#include <stddef.h>
#include <stdbool.h>
#include <ucontext.h>
#include <rte_mempool.h>
#include <sys/mman.h>

#include "cfg.h"
#include "context.h"

// TODO: Check that everything is aligned on cache lines properly

#define STACK_SIZE (4096*10 - sizeof(bool) - sizeof(struct dispatcher_request) - sizeof(ucontext_t))

struct context {
	// align the end of this struct to the end
	// of a cache line
	uint8_t stack[STACK_SIZE];
	bool contains_dispatcher_req;
	struct dispatcher_request req;
	ucontext_t ctx;
} __attribute__((packed, aligned(64)));

struct context *context_ptrs = NULL;

extern int getcontext_fast(ucontext_t *ucp);

inline int context_look_up(ucontext_t **cont, uint64_t context_idx) {
	if (context_idx >= CFG.num_contexts) {
		return -1;
	}
	*cont = &(context_ptrs[context_idx].ctx);

	return 0;
}

int context_clear(uint64_t context_idx) {
	if (context_idx >= CFG.num_contexts) {
		return -1;
	}
	
	struct context *c = &context_ptrs[context_idx];
	c->contains_dispatcher_req = false;
	return 0;
}

int context_contains_request(uint64_t context_idx, bool *contains) {
	if (context_idx >= CFG.num_contexts || !contains) {
		return -1;
	}
	struct context *c = &context_ptrs[context_idx];
	*contains = c->contains_dispatcher_req;
	return 0;
}

int context_get_request(uint64_t context_idx, struct dispatcher_request **req) {
	if (context_idx >= CFG.num_contexts || !req) {
		return -1;
	}
	struct context *c = &context_ptrs[context_idx];
	*req = &c->req;
	return 0;
}

int context_copy_dispatcher_request(uint64_t context_idx, struct dispatcher_request *req) {
	if (context_idx >= CFG.num_contexts || !req) {
		return -1;
	}
	struct context *c = &context_ptrs[context_idx];
	struct dispatcher_request *to = &c->req;
	memcpy(to, req, sizeof(*to));
	c->contains_dispatcher_req = true;
	return 0;
}

int init_context() {
	size_t i;
	size_t mmap_len = sizeof(struct context) * CFG.num_contexts;
	// according to the mmap documentation, when the first argument
	// is NULL, the mapping is created on a page boundary
	// therefore, the beginning of the array is aligned to the
	// beginning of a cache line
	// furthermore, since the [MAP_ANONYMOUS] flag is specified,
	// the memory is initialized to zeroes
	context_ptrs = mmap(NULL, mmap_len, PROT_READ | PROT_WRITE | PROT_EXEC,
			MAP_ANONYMOUS | MAP_HUGETLB | MAP_PRIVATE, -1, 0);
	if (context_ptrs == MAP_FAILED) return -1;
	for (size_t i = 0; i < CFG.num_contexts; i++) {
		struct context *cont = &context_ptrs[i];
		cont->ctx.uc_stack.ss_sp = cont->stack;
		cont->ctx.uc_stack.ss_size = STACK_SIZE;
	}

	// TODO: Need to worry about allocating the stacks (and part of the
	// context_ptrs array) on memory quickly accessible to processor
	// in each socket
	return 0;
}
