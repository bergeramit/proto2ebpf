#!/usr/bin/python
#
#Bertrone Matteo - Polytechnic of Turin
#November 2015
#
#eBPF application that parses HTTP packets
#and extracts (and prints on screen) the URL contained in the GET/POST request.
#
#eBPF program protobuf_filter is used as SOCKET_FILTER attached to eth0 interface.
#only packet of type ip and tcp containing HTTP GET/POST are returned to userspace, others dropped
#
#python script uses bcc BPF Compiler Collection by iovisor (https://github.com/iovisor/bcc)
#and prints on stdout the first line of the HTTP GET/POST request containing the url
from bcc import BPF
from protobuf_rule import ProtobufBasicRule

template_bcc_code = '''
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <linux/string.h>
#include <bcc/proto.h>

#define IP_TCP 	6
#define ETH_HLEN 14

/*eBPF program.
  Filter IP and TCP packets, having payload not empty
  and containing "HTTP", "GET", "POST"  as first bytes of payload.
  AND ALL the other packets having same (src_ip,dst_ip,src_port,dst_port)
  this means belonging to the same "session"
  this additional check avoids url truncation, if url is too long
  userspace script, if necessary, reassembles urls split in 2 or more packets.
  if the program is loaded as PROG_TYPE_SOCKET_FILTER
  and attached to a socket
  return  0 -> DROP the packet
  return -1 -> KEEP the packet and return it to user space (userspace can read it from the socket_fd )
*/
int protobuf_filter(struct __sk_buff *skb) {{

	u8 *cursor = 0;

	struct ethernet_t *ethernet = cursor_advance(cursor, sizeof(*ethernet));
	//filter IP packets (ethernet type = 0x0800)
	if (!(ethernet->type == 0x0800)) {{
		goto DROP;
	}}

	struct ip_t *ip = cursor_advance(cursor, sizeof(*ip));
	//filter TCP packets (ip next protocol = 0x06)
	if (ip->nextp != IP_TCP) {{
		goto DROP;
	}}

	u32  tcp_header_length = 0;
	u32  ip_header_length = 0;
	u32  payload_offset = 0;
	u32  payload_length = 0;

	//calculate ip header length
	//value to multiply * 4
	//e.g. ip->hlen = 5 ; IP Header Length = 5 x 4 byte = 20 byte
	ip_header_length = ip->hlen << 2;    //SHL 2 -> *4 multiply

	//check ip header length against minimum
	if (ip_header_length < sizeof(*ip)) {{
			goto DROP;
	}}

	//shift cursor forward for dynamic ip header size
	void *_ = cursor_advance(cursor, (ip_header_length-sizeof(*ip)));

	struct tcp_t *tcp = cursor_advance(cursor, sizeof(*tcp));

	//calculate tcp header length
	//value to multiply *4
	//e.g. tcp->offset = 5 ; TCP Header Length = 5 x 4 byte = 20 byte
	tcp_header_length = tcp->offset << 2; //SHL 2 -> *4 multiply

	//calculate payload offset and length
	payload_offset = ETH_HLEN + ip_header_length + tcp_header_length;
	payload_length = ip->tlen - ip_header_length - tcp_header_length;

	//load first 100 byte of payload into p (payload_array)
	//direct access to skb not allowed
	unsigned long p[100];
	int i = 0;
	for (i = 0; i < payload_length; i++) {{
		p[i] = load_byte(skb , payload_offset + i);
	}}

	// p[0] holds the first protobuf key
	// which is 3 last bits wire type and first 5 bits the field number
	if (p[0] >> 3 != {first_field_number}) {{
		goto DROP;
	}}

	{handle_first_field_rule}

	// SEARCH PROTBUF SHOULD_DROP PATTERN
	if ((p[0] == 0xa) && (p[1] == 0x14) && (p[2] == 0x53) && (p[3] == 0x68)) {{
		goto KEEP;
	}}

	// SEARCH PROTBUF SHOULD KEEP PATTERN
	if ((p[0] == 0x0a) && (p[1] == 0x0f) && (p[2] == 0x53) && (p[3] == 0x68)) {{
		goto KEEP;
	}}
	goto DROP;

	//send packet to userspace returning -1
KEEP:
	return -1;

	//drop the packet returning 0
DROP:
	return 0;
}}
'''

def generate_ebpf_from_rule(rule):
	validate_rule = rule.generate_c_code_rule(pointer='p')
	print(f"Rule: {validate_rule}")
	_dict = {
		"first_field_number": rule.field_number,
		"handle_first_field_rule": validate_rule
	}
	# import ipdb; ipdb.set_trace()
	# print(f"template_bcc_code: {template_bcc_code}")
	return BPF(text=template_bcc_code.format(**_dict), debug=0)

def generate_ebpf_from_protobuf(proto_class, rule):
    '''
    currently only support one level of protobuf class (cannot provide a protobuf-of-protobufs

    @proto_class
        the relavant protobuf class for the rule
    @rule
        Example rules:
            ProtobufBasicRule: "person.email == 'joe@gmail.com'"
            "search.query ~ dog"
			"search.page_number > 3"
    '''
    proto_rule = ProtobufBasicRule(proto_class, rule)
    ebpf = generate_ebpf_from_rule(proto_rule)
    return ebpf