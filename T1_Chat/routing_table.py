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
