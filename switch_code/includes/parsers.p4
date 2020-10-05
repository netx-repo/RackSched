parser start {
    return parse_ethernet;
}

#define ETHERTYPE_IPV4 0x0800
header ethernet_t ethernet;

parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4;
        default: ingress;
    }
}

header ipv4_t ipv4;

#define IP_PROTOCOLS_TCP 6
#define IP_PROTOCOLS_UDP 17
parser parse_ipv4 {
    extract(ipv4);
    return select(latest.protocol) {
        IP_PROTOCOLS_TCP : parse_tcp;
        IP_PROTOCOLS_UDP : parse_udp;
        default: ingress;
    }
}

field_list ipv4_field_list {
    ipv4.version;
    ipv4.ihl;
    ipv4.diffserv;
    ipv4.totalLen;
    ipv4.identification;
    ipv4.flags;
    ipv4.fragOffset;
    ipv4.ttl;
    ipv4.protocol;
    ipv4.srcAddr;
    ipv4.dstAddr;
}

field_list_calculation ipv4_chksum_calc {
    input {
        ipv4_field_list;
    }
    algorithm: csum16;
    output_width: 16;
}

calculated_field ipv4.hdrChecksum {
    update ipv4_chksum_calc;
}

header tcp_t tcp;
header udp_t udp;

#define SQ_PORT_1 1234
#define SQ_PORT_2 1235
#define SQ_PORT_3 1236

#define SQ_REPLY_PORT_1 11234
#define SQ_REPLY_PORT_2 11235
#define SQ_REPLY_PORT_3 11236

parser parse_tcp {
    extract(tcp);
    return select(latest.dstPort) {
         default : ingress;
    }
}

parser parse_udp {
    extract(udp);
    return select(latest.dstPort) {
        SQ_PORT_1 : parse_sq;
        SQ_PORT_2 : parse_sq;
        SQ_PORT_3 : parse_sq;
        SQ_REPLY_PORT_1 : parse_sq_reply;
        SQ_REPLY_PORT_2 : parse_sq_reply;
        SQ_REPLY_PORT_3 : parse_sq_reply;
        // SQ_REPLY_PORT_1 : parse_sq;
        // SQ_REPLY_PORT_2 : parse_sq;
        // SQ_REPLY_PORT_3 : parse_sq;
        default : ingress;
    }
}

header sq_t sq;
header sq_t sq_reply;

parser parse_sq {
    extract(sq);
    return ingress;
}

parser parse_sq_reply {
    extract(sq_reply);
    return ingress;
}
