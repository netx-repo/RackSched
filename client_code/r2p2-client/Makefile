ifeq ($(RTE_SDK),)
$(error "Please define RTE_SDK environment variable")
endif

# Default target, can be overriden by command line or environment
RTE_TARGET ?= x86_64-native-linuxapp-gcc

include $(RTE_SDK)/mk/rte.vars.mk

# binary name
APP = dpdk_client

# all source are stored in SRCS-y
SRCS-y := dpdk_client.c

CFLAGS += -O3 # -g for gdb debugging
#CFLAGS += $(WERROR_FLAGS)

# GSL
CFLAGS += -I/usr/local/include
LDFLAGS += -L/usr/local/lib
LDLIBS += -lgsl -lgslcblas -lm

include $(RTE_SDK)/mk/rte.extapp.mk
