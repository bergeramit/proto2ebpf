import argparse
from protobuf_ebpf_generator import generate_ebpf_from_protobuf
from examples.search_pb2 import SearchRequest
from server_app import Server
from load_ebpf_filter import run_server_with_filter
from client_app import run_client_demo
from server_app import run_server_demo

def run_test_ebpf(role):
    if role == "client":
        run_client_demo()
        return

    search_query = SearchRequest(query=b'Dog', page_number=10)
    ebpf = generate_ebpf_from_protobuf(search_query, "search_query.query ~ A")
    print("\n<Instruction for protobu handles>\n")
    print(f"search_query.SerializeToString().hex() -> {search_query.SerializeToString().hex()}")
    print(f"Use bytes.fromhex('{search_query.SerializeToString().hex()}') in order to send it in the network")
    print(f"Parse with search_query.ParseFromString(bytes.fromhex('{search_query.SerializeToString().hex()}'))")
    print("\n</Instruction for protobu handles>\n")

    if role == "server_without_filter":
        server = Server(b'AAAAAAAAAAA', 1, use_ebpf_smart_filter=False)
    elif role == "server_with_filter":
        server = Server(b'AAAAAAAAAAA', 1, use_ebpf_smart_filter=True)
    
    run_server_with_filter(ebpf, interface="lo", server=server)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', help='Can be server or client')
    args = parser.parse_args()
    run_test_ebpf(args.env)