#!/bin/sh

# Remove kernel modules
rmmod pcidma
rmmod dune

# Set huge pages
sudo sh -c 'for i in /sys/devices/system/node/node*/hugepages/hugepages-2048kB/nr_hugepages; do echo 8192 > $i; done'

# Unbind NICs
sudo ./deps/dpdk/tools/dpdk_nic_bind.py --force -u 05:00.0

# Build required kernel modules.
sudo make -sj64 -C deps/dune
sudo make -sj64 -C deps/pcidma
sudo make -sj64 -C deps/dpdk config T=x86_64-native-linuxapp-gcc
sudo make -sj64 -C deps/dpdk

# Insert kernel modules
sudo insmod deps/dune/kern/dune.ko
sudo insmod deps/pcidma/pcidma.ko
