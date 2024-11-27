import random
import matplotlib.pyplot as plt
import time

# Define the Router class
class Router:
    def __init__(self, name, bandwidth, transmission_rate, total_capacity, node_type='router'):
        self.name = name  # Unique identifier for the router (now all strings)
        self.bandwidth = bandwidth  # in Mbps
        self.transmission_rate = transmission_rate  # in packets per second
        self.total_capacity = total_capacity  # in MB
        self.memory_space = 0  # current usage in MB
        self.processing_rate = 20  # in MB per iteration (Adjusted to be less than data_size)
        self.neighbors = []  # List of neighboring routers
        self.routing_table = {}  # Routing table mapping destinations to next hops
        self.node_type = node_type  # 'router' or 'server'
        self.received_data = []  # Data received for metrics
        self.packet_loss_prob = 0.0
        self.packet_loss_deterioration = 0.005
        # For Smart Router
        if self.name == 'Smart Router':
            self.routing_probabilities = {}
        # Initialize lists to track packet loss probability and memory usage
        self.packet_loss_prob_history = []
        self.memory_usage_history = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def update_routing_table(self, destination, next_hop):
        # Update routing table with destination and next hop router
        self.routing_table[destination.name] = next_hop

    def send_data(self, destination, data_size, path=[]):
        # Simulate sending data to a destination
        path = path + [self.name]
        if destination in self.neighbors:
            # Directly send to neighbor
            destination.receive_data(data_size, path)
        else:
            # No direct route; use routing table
            if destination.name in self.routing_table:
                next_hop = self.routing_table[destination.name]
                next_hop.receive_data(data_size, path)
            else:
                print(f"No route from {self.name} to {destination.name}")

    def simulate_packet_loss(self):
        """Update packet loss probability dynamically."""
        if self.name == "Router 1":
            # Gradually increase packet loss probability for Router 1
            self.packet_loss_prob = min(1.0, self.packet_loss_prob + self.packet_loss_deterioration)
        return random.random() < self.packet_loss_prob

    def receive_data(self, data_size, path):
        """Simulate receiving data and processing."""
        if self.node_type == 'router':
            # Use the dynamic packet loss probability for routers
            packet_loss = self.simulate_packet_loss()
            print("LOSSS" + str(self.packet_loss_prob) + "\n")
            self.packet_loss_prob_history.append(self.packet_loss_prob)  # Track history
        else:
            packet_loss = False  # Assume servers do not lose packets

        if packet_loss:
            print(f"Packet lost at {self.name}")
        else:
            # Accumulate memory space
            self.memory_space += data_size
            print(f"{self.name} received data. Memory usage: {self.memory_space}/{self.total_capacity}")
            if self.node_type == 'server' and self.name == 'Server B':
                # Server B received data, send back metrics
                send_metrics_back(path + [self.name])
            else:
                # Forward data to the next hop towards Server B
                if 'Server B' in self.routing_table:
                    next_hop = self.routing_table['Server B']
                    next_hop.receive_data(data_size, path + [self.name])
        # Update memory usage history
        self.memory_usage_history.append(self.memory_space)
        # Update metrics
        self.received_data.append({'data_size': data_size, 'packet_loss': packet_loss})



    # def receive_data(self, data_size, path):
    #     # Simulate receiving data and processing
    #     if self.node_type == 'router':
    #         packet_loss_prob = min(1, self.memory_space / self.total_capacity)
    #         packet_loss = random.random() < packet_loss_prob
    #         self.packet_loss_prob_history.append(packet_loss_prob)
    #     else:
    #         packet_loss = False  # Assume servers do not lose packets
    #     if packet_loss:
    #         print(f"Packet lost at {self.name}")
    #     else:
    #         # Accumulate memory space
    #         self.memory_space += data_size
    #         print(f"{self.name} received data. Memory usage: {self.memory_space}/{self.total_capacity}")
    #         if self.node_type == 'server' and self.name == 'Server B':
    #             # Server B received data, send back metrics
    #             send_metrics_back(path + [self.name])
    #         else:
    #             # Forward data to the next hop towards Server B
    #             if 'Server B' in self.routing_table:
    #                 next_hop = self.routing_table['Server B']
    #                 next_hop.receive_data(data_size, path + [self.name])
    #     # Update memory usage history
    #     self.memory_usage_history.append(self.memory_space)
    #     # Update metrics
    #     self.received_data.append({'data_size': data_size, 'packet_loss': packet_loss})


    def process_data(self):
        # Simulate processing data and freeing up memory_space
        if self.memory_space > 0:
            processed_data = min(self.processing_rate, self.memory_space)
            self.memory_space -= processed_data
            print(f"{self.name} processed {processed_data} MB. Remaining memory: {self.memory_space}/{self.total_capacity}")
        else:
            # Even if there's no data to process, log the current state
            self.memory_usage_history.append(self.memory_space)
            self.packet_loss_prob_history.append(0)

# Function to send metrics back to Smart Router
def send_metrics_back(path):
    # Send metrics directly to Smart Router
    print(f"Server B is sending metrics to Smart Router")
    smart_router = next((node for node in nodes if node.name == 'Smart Router'), None)
    if smart_router:
        total_packet_loss = 0
        # Calculate total packet loss along the path
        for node_name in path:
            node = next(node for node in nodes if node.name == node_name)
            if node.received_data:
                packet_loss = node.received_data[-1]['packet_loss']
                total_packet_loss += packet_loss
        # Identify the next hop after Smart Router
        if 'Smart Router' in path:
            smart_router_index = path.index('Smart Router')
            if smart_router_index + 1 < len(path):
                next_hop_name = path[smart_router_index + 1]
                if next_hop_name in smart_router.routing_probabilities:
                    if total_packet_loss > 0:
                        # Decrease probability of the router used
                        smart_router.routing_probabilities[next_hop_name] *= 0.9  # Decrease by 10%
                    else:
                        # Increase probability
                        smart_router.routing_probabilities[next_hop_name] *= 1.1  # Increase by 10%
                    # Normalize probabilities
                    total_prob = sum(smart_router.routing_probabilities.values())
                    for key in smart_router.routing_probabilities:
                        smart_router.routing_probabilities[key] /= total_prob
                else:
                    print(f"Next hop {next_hop_name} not in routing probabilities.")
            else:
                print("No next hop after Smart Router in path.")
        else:
            print("Smart Router not in path.")
        # Record metrics for this iteration
        probabilities_over_time.append((
            smart_router.routing_probabilities.get('Router 1', 0),
            smart_router.routing_probabilities.get('Router 2', 0)
        ))
        packet_losses.append(total_packet_loss > 0)
    else:
        print("Smart Router not found.")

# Create the network infrastructure
# Create Router objects with string names
smart_router = Router(name='Smart Router', bandwidth=100, transmission_rate=1000, total_capacity=500)
router1 = Router(name='Router 1', bandwidth=80, transmission_rate=800, total_capacity=400)
router2 = Router(name='Router 2', bandwidth=90, transmission_rate=900, total_capacity=450)
server_A = Router(name='Server A', bandwidth=1000, transmission_rate=2000, total_capacity=1000, node_type='server')
server_B = Router(name='Server B', bandwidth=1000, transmission_rate=2000, total_capacity=1000, node_type='server')

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
router1.update_routing_table(destination=server_B, next_hop=server_B)
router2.update_routing_table(destination=server_B, next_hop=server_B)

# Initialize routing probabilities in Smart Router with string keys
smart_router.routing_probabilities = {'Router 1': 0.5, 'Router 2': 0.5}

# List of all nodes for easy access
nodes = [smart_router, router1, router2, server_A, server_B]

# Variables to collect metrics over time
probabilities_over_time = []
packet_losses = []
packet_loss_probs_router1 = []
packet_loss_probs_router2 = []
memory_usage_router1 = []
memory_usage_router2 = []

# Function to simulate network traffic and Smart Router's learning
def simulate_traffic(num_iterations=100):
    for i in range(num_iterations):
        print(f"\nIteration {i+1}")
        data_size = 50  # MB
        path = []
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
        packet_loss_probs_router1.append(router1.packet_loss_prob_history[-1] if router1.packet_loss_prob_history else 0)
        packet_loss_probs_router2.append(router2.packet_loss_prob_history[-1] if router2.packet_loss_prob_history else 0)
        memory_usage_router1.append(router1.memory_space)
        memory_usage_router2.append(router2.memory_space)
        # If no metrics were recorded (packet lost before reaching server_B), record current probabilities
        if len(probabilities_over_time) < i + 1:
            probabilities_over_time.append((
                smart_router.routing_probabilities.get('Router 1', 0),
                smart_router.routing_probabilities.get('Router 2', 0)
            ))
            packet_losses.append(True)  # Assume packet was lost
        # Wait for a short time to simulate processing
        time.sleep(0.01)  # Reduced delay for faster simulation

# Run the simulation
simulate_traffic(num_iterations=1000)

# Plot the routing probabilities and packet losses over time
iterations = list(range(1, len(probabilities_over_time) + 1))
prob_router1 = [prob[0] for prob in probabilities_over_time]
prob_router2 = [prob[1] for prob in probabilities_over_time]
packet_loss_values = [1 if loss else 0 for loss in packet_losses]

plt.figure(figsize=(12, 12))

plt.subplot(3, 1, 1)
plt.plot(iterations, prob_router1, label='Probability of Router 1')
plt.plot(iterations, prob_router2, label='Probability of Router 2')
plt.xlabel('Iteration')
plt.ylabel('Routing Probability')
plt.title('Smart Router Routing Probabilities Over Time')
plt.legend()

plt.subplot(3, 1, 2)
plt.plot(iterations, packet_loss_probs_router1, label='Packet Loss Prob - Router 1')
plt.plot(iterations, packet_loss_probs_router2, label='Packet Loss Prob - Router 2')
plt.xlabel('Iteration')
plt.ylabel('Packet Loss Probability')
plt.title('Packet Loss Probability of Routers Over Time')
plt.legend()

plt.subplot(3, 1, 3)
plt.plot(iterations, memory_usage_router1, label='Memory Usage - Router 1')
plt.plot(iterations, memory_usage_router2, label='Memory Usage - Router 2')
plt.xlabel('Iteration')
plt.ylabel('Memory Usage (MB)')
plt.title('Memory Usage of Routers Over Time')
plt.legend()

plt.tight_layout()
plt.show()
