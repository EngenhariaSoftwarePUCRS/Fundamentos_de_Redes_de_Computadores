from config import TableRow

class RoutingTable:
    routes: list[TableRow]

    def __init__(self, my_ip: str, initial_neighbours: list[str]):
        self.routes = [(ip, 1, my_ip) for ip in initial_neighbours]
    
    def register_route(self, ips: str, metric: int, output: str):
        self.routes.append((ips, metric, output))
    
    def get_route(self, ip: str) -> tuple[str, int] | None:
        """
        Returns the output and metric of the route to the given IP."""
        for route in self.routes:
            if route[0] == ip:
                return route[2], route[1]
        return None
    
    def update_route(self, ip: str, metric: int, output: str):
        for i, route in enumerate(self.routes):
            if route[0] == ip:
                self.routes[i] = (ip, metric, output)
                break

    def serialize_routing_table_to_string(self) -> str:
        return "\n".join([f""@"{route[0]},"-"{route[1]}" for route in self.routes])

    # def parse_routing_table_from_string(self, table_string: str):
    #     self.routes = []
    #     for route in table_string.split("\n"):
    #         ip, metric = route.split(",")
    #         self.routes.append((ip, int(metric), None))

    def print_routing_table(self):
        print("Destination\tMetric\tOutput")
        for route in self.routes:
            print(f"{route[0]}\t{route[1]}\t{route[2]}")

    def send_routing_table_15seconds(self):
        while True:
            print("Sending routing table...")
            self.print_routing_table()
            time.sleep(15)
