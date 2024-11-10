import re
import time

from config import TableRow

class RoutingTable:
    self_ip: str
    routes: list[TableRow]

    def __init__(self, my_ip: str, initial_neighbours: list[str]):
        self.self_ip = my_ip
        self.routes = [(ip, 1, my_ip) for ip in initial_neighbours]
    
    def register_route(self, ips: str, metric: int, output: str) -> None:
        self.routes.append((ips, metric, output))
    
    def get_route(self, ip: str) -> tuple[str, int] | None:
        """
        Returns the output and metric of the route to the given IP."""
        for route in self.routes:
            if route[0] == ip:
                return route[2], route[1]
        return None
    
    def get_neighbours(self) -> list[str]:
        neighbours = [route[0] for route in self.routes]
        return set(neighbours) - {self.self_ip}
    
    def get_ips_from_routes(self, routes: list[TableRow] | None = None) -> list[str]:
        if routes is None:
            routes = self.routes
        return [route[0] for route in routes]

    def update_route(self, ip: str, metric: int, output: str) -> None:
        for i, route in enumerate(self.routes):
            if route[0] == ip:
                self.routes[i] = (ip, metric, output)
                break

    def remove_route(self, ip: str) -> None:
        self.routes = [route for route in self.routes if route[0] != ip]

    def order_ips(ips: list[str]) -> list[str]:
        return sorted(ips)

    def serialize_routing_table_to_string(self) -> str:
        return "".join([f"@{route[0]}-{route[1]}" for route in self.routes])

    def parse_string_to_routing_table(self, table_string: str) -> list[TableRow]:
        table_rows = re.split(r'@', table_string)
        table: list[TableRow] = []
        for row in table_rows[1:]:
            ip, metric = row.split('-')
            table.append((ip, int(metric), None))
        return table

    def __str__(self) -> str:
        as_str: str = "Destination\tMetric\tOutput"
        for route in self.routes:
            as_str += f"\n{route[0]}\t{route[1]}\t{route[2]}"
        return as_str
