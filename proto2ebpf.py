from protobuf_rule import ProtobufBasicRule
from protobuf_ebpf_generator import generate_ebpf_from_rule

def generate_ebpf_from_protobuf(proto_class, rule):
    '''
    currently only support one level of protobuf class (cannot provide a protobuf-of-protobufs

    @proto_class
        the relavant protobuf class for the rule
    @rule
        Example rules:
            ProtobufBasicRule: "person.email == 'joe@gmail.com'"
            "search.query ~ '*dog' and search.page_number > 3"
    '''
    proto_rule = ProtobufBasicRule(proto_class, rule)
    ebpf = generate_ebpf_from_rule(proto_rule)
    return ebpf

def run_test_ebpf():
    from examples.search_pb2 import SearchRequest
    from load_ebpf_filter import run_filter_demo

    search_query = SearchRequest(query=b'Dog', page_number=10)
    ebpf = generate_ebpf_from_protobuf(search_query, "search_query.page_number > 5")
    run_filter_demo(ebpf, interface="lo")


if __name__ == "__main__":
    run_test_ebpf()