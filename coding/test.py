import random
import matplotlib.pyplot as plt
import numpy as np  # Import numpy for Poisson and Exponential distributions

# Define the Router class
class Router:
    def __init__(self, name, bandwidth, transmission_rate, total_capacity, node_type='router', packet_loss_prob=0.0):
        self.name = name
        self.bandwidth = bandwidth
        self.transmission_rate = transmission_rate
        self.total_capacity = total_capacity
        self.memory_space = 0
        self.processing_rate = 20
        self.neighbors = []
        self.routing_table = {}
        self.node_type = node_type
        self.received_data = []
        self.packet_loss_prob = packet_loss_prob
        self.packet_loss_deterioration = 0.005  # Adjusted if needed
        if self.name == 'Smart Router':
            self.routing_probabilities = {}
        self.packet_loss_prob_history = []
        self.memory_usage_history = []

    # Rest of the Router class remains the same
    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def update_routing_table(self, destination, next_hop):
        self.routing_table[destination.name] = next_hop

    def send_data(self, destination, data_size, path=[]):
        path = path + [self.name]
        if destination in self.neighbors:
            destination.receive_data(data_size, path)
        else:
            if destination.name in self.routing_table:
                next_hop = self.routing_table[destination.name]
                next_hop.receive_data(data_size, path)
            else:
                print(f"No route from {self.name} to {destination.name}")

    def simulate_packet_loss(self):
        if self.name == "Router 1":
            # Gradually increase packet loss probability for Router 1
            self.packet_loss_prob = min(1.0, self.packet_loss_prob + self.packet_loss_deterioration)
        return random.random() < self.packet_loss_prob

    def receive_data(self, data_size, path):
        if self.node_type == 'router':
            packet_loss = self.simulate_packet_loss()
            self.packet_loss_prob_history.append(self.packet_loss_prob)
        else:
            packet_loss = False
        if packet_loss:
            print(f"Packet lost at {self.name}")
            # Even when a packet is lost, append to received_data to avoid IndexError
            self.received_data.append({'data_size': data_size, 'packet_loss': True})
        else:
            self.memory_space += data_size
            print(f"{self.name} received data. Memory usage: {self.memory_space}/{self.total_capacity}")
            if self.node_type == 'server' and self.name == 'Server B':
                send_metrics_back(path + [self.name])
            else:
                if 'Server B' in self.routing_table:
                    next_hop = self.routing_table['Server B']
                    next_hop.receive_data(data_size, path + [self.name])
            # Update metrics
            self.received_data.append({'data_size': data_size, 'packet_loss': False})
        self.memory_usage_history.append(self.memory_space)

    def process_data(self):
        if self.memory_space > 0:
            processed_data = min(self.processing_rate, self.memory_space)
            self.memory_space -= processed_data
            print(f"{self.name} processed {processed_data} MB. Remaining memory: {self.memory_space}/{self.total_capacity}")
        else:
            self.memory_usage_history.append(self.memory_space)
            self.packet_loss_prob_history.append(self.packet_loss_prob)

# Function to send metrics back to Smart Router
def send_metrics_back(path):
    print(f"Server B is sending metrics to Smart Router")
    smart_router = next((node for node in nodes if node.name == 'Smart Router'), None)
    if smart_router:
        if 'Smart Router' in path:
            smart_router_index = path.index('Smart Router')
            if smart_router_index + 1 < len(path):
                next_hop_name = path[smart_router_index + 1]
                next_hop = next((node for node in nodes if node.name == next_hop_name), None)
                if next_hop_name in smart_router.routing_probabilities and next_hop:
                    # Check if received_data is not empty
                    if next_hop.received_data:
                        # Get the last packet's information
                        packet_info = next_hop.received_data[-1]
                        packet_loss = packet_info['packet_loss']
                        p = 1 if packet_loss else 0
                        # Use packet_loss as the metric
                        # 0.99999 or 1
                        combined_metric = 1 / (p + 1e-6)
                        print(f"Combined metric for {next_hop_name}: {combined_metric}")
                        threshold = 1
                        if combined_metric < threshold:
                            smart_router.routing_probabilities[next_hop_name] = max(
                                0.1, smart_router.routing_probabilities[next_hop_name] * 0.9
                            )
                            print(f"Punishing {next_hop_name} due to packet loss.")
                        else:
                            smart_router.routing_probabilities[next_hop_name] = min(
                                0.9, smart_router.routing_probabilities[next_hop_name] * 1.1
                            )
                            print(f"Rewarding {next_hop_name} due to successful delivery.")
                        # Normalize probabilities
                        total_prob = sum(smart_router.routing_probabilities.values())
                        for key in smart_router.routing_probabilities:
                            smart_router.routing_probabilities[key] /= total_prob
                        # Record metrics for this iteration
                        probabilities_over_time.append((
                            smart_router.routing_probabilities.get('Router 1', 0),
                            smart_router.routing_probabilities.get('Router 2', 0)
                        ))
                        # Record which router was chosen
                        chosen_routers.append(next_hop_name)
                    else:
                        print(f"No packet information available for {next_hop_name}.")
                else:
                    print(f"Next hop {next_hop_name} not in routing probabilities.")
            else:
                print("No next hop after Smart Router in path.")
        else:
            print("Smart Router not in path.")
    else:
        print("Smart Router not found.")

# Create the network infrastructure
smart_router = Router(
    name='Smart Router',
    bandwidth=100,
    transmission_rate=1000,
    total_capacity=500
)
router1 = Router(
    name='Router 1',
    bandwidth=80,
    transmission_rate=800,
    total_capacity=420,
    packet_loss_prob=0.15
)
router2 = Router(
    name='Router 2',
    bandwidth=90,
    transmission_rate=900,
    total_capacity=450,
    packet_loss_prob=0.05
)
server_A = Router(
    name='Server A',
    bandwidth=1000,
    transmission_rate=2000,
    total_capacity=1000,
    node_type='server'
)
server_B = Router(
    name='Server B',
    bandwidth=1000,
    transmission_rate=2000,
    total_capacity=1000,
    node_type='server'
)

# Define neighbors
server_A.add_neighbor(smart_router)
smart_router.add_neighbor(server_A)
smart_router.add_neighbor(router1)
smart_router.add_neighbor(router2)
router1.add_neighbor(smart_router)
router1.add_neighbor(server_B)
router2.add_neighbor(smart_router)
router2.add_neighbor(server_B)
server_B.add_neighbor(router1)
server_B.add_neighbor(router2)

# Update Routing tables
smart_router.update_routing_table(destination=server_B, next_hop=None)
router1.update_routing_table(destination=server_B, next_hop=server_B)
router2.update_routing_table(destination=server_B, next_hop=server_B)

# Initialize routing probabilities in Smart Router
smart_router.routing_probabilities = {'Router 1': 0.5, 'Router 2': 0.5}

# List of all nodes
nodes = [smart_router, router1, router2, server_A, server_B]

# Metrics
probabilities_over_time = []
packet_losses = []
packet_loss_probs_router1 = []
packet_loss_probs_router2 = []
memory_usage_router1 = []
memory_usage_router2 = []
chosen_routers = []

# Function to simulate network traffic and Smart Router's learning
def simulate_traffic(num_iterations=30):
    """
    Simulate the network traffic using both Poisson and Exponential distributions.

    Parameters:
    - num_iterations: Number of iterations for the simulation.
    """
    for i in range(num_iterations):
        print(f"\nIteration {i+1}")
        path = []

        # Generate number of packets using Poisson distribution
        lam = 5  # Average number of packets per iteration from Poisson
        num_packets_poisson = np.random.poisson(lam)

        # Generate number of packets using Exponential distribution
        scale = 1  # Mean inter-arrival time
        total_time = 10  # Total simulation time per iteration
        arrival_times = []
        current_time = 0
        while current_time < total_time:
            inter_arrival_time = np.random.exponential(scale)
            current_time += inter_arrival_time
            if current_time < total_time:
                arrival_times.append(current_time)
        num_packets_exponential = len(arrival_times)

        # Debug line
        print(str(arrival_times) + " Arrival times\n")

        # Combine the numbers
        num_packets = num_packets_poisson + num_packets_exponential

        print(f"Number of packets to send: {num_packets}")

        # Simulate sending the packets
        for _ in range(num_packets):
            data_size = 50  # MB per packet
            # Smart Router chooses next hop based on probabilities
            next_hop_name = random.choices(
                population=['Router 1', 'Router 2'],
                weights=[
                    smart_router.routing_probabilities.get('Router 1', 0),
                    smart_router.routing_probabilities.get('Router 2', 0)
                ],
                k=1
            )[0]
            next_hop = router1 if next_hop_name == 'Router 1' else router2
            # Update routing table in Smart Router
            smart_router.update_routing_table(destination=server_B, next_hop=next_hop)
            # Server A sends data to Smart Router
            server_A.send_data(smart_router, data_size, path)
            # Process data at all routers and server_B
            for router in [smart_router, router1, router2, server_B]:
                router.process_data()
            # Collect packet loss probabilities and memory usage for plotting
            packet_loss_probs_router1.append(router1.packet_loss_prob)
            packet_loss_probs_router2.append(router2.packet_loss_prob)
            memory_usage_router1.append(router1.memory_space)
            memory_usage_router2.append(router2.memory_space)
            # No need for sleep since delay is removed

# Run the simulation
simulate_traffic(num_iterations=30)

# Plotting
iterations = list(range(1, len(probabilities_over_time) + 1))
if iterations:
    prob_router1 = [prob[0] for prob in probabilities_over_time]
    prob_router2 = [prob[1] for prob in probabilities_over_time]

    plt.figure(figsize=(12, 10))

    plt.subplot(3, 1, 1)
    plt.plot(iterations, prob_router1, label='Probability of Router 1')
    plt.plot(iterations, prob_router2, label='Probability of Router 2')
    plt.xlabel('Iteration')
    plt.ylabel('Routing Probability')
    plt.title('Smart Router Routing Probabilities Over Time')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(iterations, packet_loss_probs_router1[:len(iterations)], label='Packet Loss Prob - Router 1')
    plt.plot(iterations, packet_loss_probs_router2[:len(iterations)], label='Packet Loss Prob - Router 2')
    plt.xlabel('Iteration')
    plt.ylabel('Packet Loss Probability')
    plt.title('Packet Loss Probability of Routers Over Time')
    plt.legend()

    plt.subplot(3, 1, 3)
    router_choices = [1 if name == 'Router 1' else 2 for name in chosen_routers]
    plt.plot(iterations, router_choices, 'o-')
    plt.xlabel('Iteration')
    plt.ylabel('Chosen Router')
    plt.yticks([1,2], ['Router 1', 'Router 2'])
    plt.title('Router Choices Over Time')

    plt.tight_layout()
    plt.show()
else:
    print("No data to plot.")
