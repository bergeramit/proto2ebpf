import socket
import datetime
from examples.search_pb2 import SearchRequest

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

class Server:
    def __init__(self, template_query, template_page_number, use_ebpf_smart_filter) -> None:
        self.search_query = SearchRequest(query=template_query, page_number=template_page_number)
        self.sock = socket.socket()
        self.sock.bind((SERVER_HOST, SERVER_PORT))
        self.sock.listen(1)
        self.use_ebpf_smart_filter = use_ebpf_smart_filter
        print('Listening on port %s ...' % SERVER_PORT)

    def is_valid_protobuf(self, search_query):
        if not search_query.query:
            return False

        # print(f"Protbuf from server: {search_query.query}")
        for i in range(len(search_query.query)):
            if search_query.query[i] == 'A':
                return False
        return True

    def _process_with_container_filter(self, packet, total_valid_amount):
        try:
            search_query = SearchRequest(query=b'AAAAAAAA', page_number=10)
            search_query.ParseFromString(packet)
            should_keep = self.is_valid_protobuf(search_query)
        except Exception:
            # print(f"Parse error on: {packet}")
            # print(f"{datetime.datetime.now()}: Manually Dropped")
            return total_valid_amount

        if should_keep:
            print(f"{datetime.datetime.now()}: Handled!{total_valid_amount}")
            return total_valid_amount + 1
        else:
            # print(f"{datetime.datetime.now()}: Manually Dropped")
            return total_valid_amount

    def process(self, packet, total_valid_amount):
        if self.use_ebpf_smart_filter:
            print(f"{datetime.datetime.now()}: Handled!{total_valid_amount}")
            return total_valid_amount + 1
        return self._process_with_container_filter(packet, total_valid_amount)

def run_server_demo():

    # Wait for client connections
    server = Server(b'template', 1)
    total_valid_amount = 1
    client_connection, _ = server.sock.accept()
    print(f"{datetime.datetime.now()}: Started Session")
    while True:    

        # Get the client request
        # search_query.ParseFromString()
        request = client_connection.recv(1024)
        if not request:
            break

        server.process(request, total_valid_amount)
        total_valid_amount += 1

    # Close socket
    print('Closing Server...')
    server.sock.close()
