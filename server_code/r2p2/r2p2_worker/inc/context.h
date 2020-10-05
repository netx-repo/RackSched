/*
 * context.h - manages the context pointers
 */

#include <ucontext.h>
#include <inttypes.h>

#include "dispatcher.h"

int context_look_up(ucontext_t **cont, uint64_t context_idx);
int context_clear(uint64_t context_idx);
int context_contains_request(uint64_t context_idx, bool *contains);
int context_get_request(uint64_t context_idx, struct dispatcher_request **req);
int context_copy_dispatcher_request(uint64_t context_idx, struct dispatcher_request *req);
int init_context();

/* From context_fast.S */

extern int getcontext_fast(ucontext_t *ucp);
extern int swapcontext_fast(ucontext_t *ouctx, ucontext_t *uctx);
extern int swapcontext_very_fast(ucontext_t *ouctx, ucontext_t *uctx);
extern int swapcontext_fast_to_control(ucontext_t *, ucontext_t *);
