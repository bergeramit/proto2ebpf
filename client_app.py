import socket
import time
from examples.search_pb2 import SearchRequest

def generate_query_packet(query, page_number):
    search_query = SearchRequest(query=query, page_number=page_number)
    return search_query.SerializeToString()

def run_client_demo():
    client = socket.socket()
    client.connect(("0.0.0.0", 8000))
    should_filter_protbuf_packet = generate_query_packet(b'AAAAAAAAA', 3)
    should_process = generate_query_packet(b'BBBBBBBBBBBBB', 5)
    for _ in range(1000):
        print(f"Sending AAAAAAAAA (should drop)...")
        client.send(should_process)
        time.sleep(0.02)
        print(f"Sending BBBBBBBBBBBBB (should process)...")
        # print(f"Sending {should_process.query}: {should_filter_protbuf_packet.hex()}")
        client.send(should_filter_protbuf_packet)
        time.sleep(0.02)
