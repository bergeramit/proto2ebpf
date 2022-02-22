import argparse
from protobuf_ebpf_generator import generate_ebpf_from_protobuf
from examples.search_pb2 import SearchRequest
from server_app import parse_query_packet
from load_ebpf_filter import run_server_with_filter

def run_client_demo(interface):
    pass

def run_test_ebpf(role):
    search_query = SearchRequest(query=b'Dog', page_number=10)
    ebpf = generate_ebpf_from_protobuf(search_query, "search_query.page_number > 5")
    print("\n<Instruction for protobu handles>\n")
    print(f"search_query.SerializeToString().hex() -> {search_query.SerializeToString().hex()}")
    print(f"Use bytes.fromhex('{search_query.SerializeToString().hex()}') in order to send it in the network")
    print(f"Parse with search_query.ParseFromString(bytes.fromhex('{search_query.SerializeToString().hex()}'))")
    print("\n</Instruction for protobu handles>\n")

    if role == "client":
        run_client_demo(interface="lo")
    elif role == "server":
        run_server_with_filter(ebpf, interface="lo", server_processing=parse_query_packet)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', help='Can be server or client')
    args = parser.parse_args()
    run_test_ebpf(args.env)