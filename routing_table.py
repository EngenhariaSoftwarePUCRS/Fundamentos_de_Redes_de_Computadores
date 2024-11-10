import re
from socket import socket

from config import TableRow, router_port

class RoutingTable:
    self_ip: str
    routes: list[TableRow]
    live_neighbours: dict[str, bool]

    def __init__(self, my_ip: str, initial_neighbours: list[str]):
        self.self_ip = my_ip
        self.routes = [(ip, 1, my_ip) for ip in initial_neighbours]
        self.live_neighbours = {}
    
    def register_route(self, ip: str, metric: int, output: str) -> None:
        self.routes.append((ip, metric, output))
    
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
    
    def alive_neighbour(self, ip: str) -> None:
        self.live_neighbours[ip] = True

    def _remove_neighbour(self, ip: str) -> None:
        for i, route in enumerate(self.routes):
            if route[0] == ip or route[2] == ip:
                self.routes.pop(i)

    def remove_dead_neighbours(self) -> None:
        for neighbour in self.live_neighbours:
            if not self.live_neighbours[neighbour]:
                self._remove_neighbour(neighbour)

    def broadcast_message(self, message: str, socket: socket) -> None:
        for neighbour in self.get_neighbours():
            self.live_neighbours[neighbour] = False
            socket.sendto(message.encode(), (neighbour, router_port))

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
