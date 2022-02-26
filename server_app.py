import socket
import datetime
from examples.search_pb2 import SearchRequest

# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

class Server:
    def __init__(self, template_query, template_page_number) -> None:
        self.search_query = SearchRequest(query=template_query, page_number=template_page_number)
        self.sock = socket.socket()
        self.sock.bind((SERVER_HOST, SERVER_PORT))
        self.sock.listen(1)
        print('Listening on port %s ...' % SERVER_PORT)

    def is_valid_protobuf(self, search_query):
        return True

    def process(self, packet):
        print(f"Got to server: {packet}")
        search_query = SearchRequest(query=b'Dog', page_number=10)
        search_query.ParseFromString(packet)

        should_keep = self.is_valid_protobuf(search_query)
        if should_keep:
            print(f"{datetime.datetime.now()}: Handled!")
        else:
            print(f"{datetime.datetime.now()}: Manually Dropped")


def run_server_demo():

    # Wait for client connections
    server = Server(b'template', 1)
    client_connection, _ = server.sock.accept()
    print(f"{datetime.datetime.now()}: Started Session")
    while True:    

        # Get the client request
        # search_query.ParseFromString()
        request = client_connection.recv(1024)
        if not request:
            break

        server.process(request)

    # Close socket
    print('Closing Server...')
    server.sock.close()
