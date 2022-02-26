import socket
import time
from examples.search_pb2 import SearchRequest

def generate_query_packet(query, page_number):
    search_query = SearchRequest(query=query, page_number=page_number)
    return search_query.SerializeToString()

def run_client_demo():
    client = socket.socket()
    client.connect(("0.0.0.0", 8000))
    should_filter_protbuf_packet = generate_query_packet(b'ShouldNotDogOnServer', 3)
    should_process = generate_query_packet(b'ShouldProcesses', 5)
    for _ in range(1):
        print(f"Sending {should_filter_protbuf_packet.hex()}")
        client.send(should_filter_protbuf_packet)
        time.sleep(0.01)
        print(f"Sending {should_process.hex()}")
        client.send(should_process)
        time.sleep(0.01)
