from examples.search_pb2 import SearchRequest

def parse_query_packet(packet):
    try:
        search_query = SearchRequest(query=b'Dog', page_number=10)
        search_query.ParseFromString(packet)
        print(f"Got packet at server: search_query.SerializeToString().hex() -> {search_query.SerializeToString().hex()}")
        print(f"Handled")
    except Exception:
        print("Error in parsing protobuf!")
