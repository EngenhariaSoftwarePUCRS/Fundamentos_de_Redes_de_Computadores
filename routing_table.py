import re
from socket import socket

from config import TableRow, router_port


class RoutingTable:
    self_ip: str
    routes: list[TableRow]
    acquantainces_last_interaction: dict[str, int]

    def __init__(self, my_ip: str, initial_neighbours: list[str]):
        """Initializes the routing table with the given IP and neighbours."""
        self.self_ip = my_ip
        self.routes = [(ip, 1, ip) for ip in initial_neighbours]
        self.acquantainces_last_interaction = {ip: 0 for ip in initial_neighbours}
    
    def register_route(self, ip: str, metric: int, output: str) -> None:
        """Inserts a new line in the routing table."""
        self.routes.append((ip, metric, output))
    
    def get_route(self, ip: str) -> tuple[str, int] | None:
        """Returns the output and metric of the route to the given IP."""
        for route in self.routes:
            if route[0] == ip:
                return route[2], route[1]
        return None
    
    def get_neighbours(self, routes: list[TableRow] | None = None) -> list[str]:
        """Returns the IPs of the router's neighbours (only directly connected)."""
        if not routes:
            routes = self.routes
        neighbours = [route[0] for route in self.routes if route[1] == 1]
        return neighbours
    
    def get_acquantainces(self, routes: list[TableRow] | None = None) -> list[str]:
        """Returns the IPs of the router's neighbours (all, including indirectly connected)."""
        if not routes:
            routes = self.routes
        acquantainces = [route[0] for route in self.routes]
        return acquantainces

    def update_route(self, ip: str, metric: int, output: str) -> None:
        """Updates the metric and output of the route to the given IP."""
        for i, route in enumerate(self.routes):
            if route[0] == ip:
                self.routes[i] = (ip, metric, output)
                break

    def remove_route(self, ip: str) -> None:
        """Removes the route to the given IP."""
        self.routes = [route for route in self.routes if route[0] != ip]
    
    def alive_acquantaince(self, ip: str, last_interaction_timestamp: int) -> None:
        """Marks the given acquantaince as alive, updating its last interaction timestamp."""
        self.acquantainces_last_interaction[ip] = last_interaction_timestamp

    def _remove_acquantaince(self, ip: str) -> None:
        """Removes the given acquantaince from the routing table, as destination or origin."""
        for i, route in enumerate(self.routes):
            if route[0] == ip or route[2] == ip:
                self.routes.pop(i)

    def remove_dead_acquantainces(self, current_timestamp: int, threshhold: int) -> None:
        """Removes all acquantainces that have not interacted in the last threshhold seconds."""
        for acquantaince, last_interaction in self.acquantainces_last_interaction.items():
            if current_timestamp - last_interaction >= threshhold:
                self._remove_acquantaince(acquantaince)

    def broadcast_message_neighbours(self, message: str, socket: socket) -> None:
        """Sends the given message to all neighbours (only directly connected)."""
        for neighbour in self.get_neighbours():
            socket.sendto(message.encode(), (neighbour, router_port))

    def broadcast_message_acquantainces(self, message: str, socket: socket) -> None:
        """Sends the given message to all acquantainces (including indirectly connected)."""
        for acquantaince in self.get_acquantainces():
            socket.sendto(message.encode(), (acquantaince, router_port))

    def serialize_routing_table_to_string(self) -> str:
        """Returns a string representation of the routing table for broadcasting."""
        return "".join([f"@{route[0]}-{route[1]}" for route in self.routes])

    def parse_string_to_routing_table(self, table_string: str) -> list[TableRow]:
        """Returns a list of routes from the given string representation of a routing table."""
        table_rows = re.split(r'@', table_string)
        table: list[TableRow] = []
        for row in table_rows[1:]:
            ip, metric = row.split('-')
            table.append((ip, int(metric), None))
        return table

    def __str__(self) -> str:
        """Returns a string representation of the routing table for printing."""
        if not self.routes:
            return "No routes"
        as_str: str = "Destination\tMetric\tOutput"
        for route in self.routes:
            as_str += f"\n{route[0]}\t{route[1]}\t{route[2]}"
        return as_str
