import random
import matplotlib.pyplot as plt
import numpy as np

# Define the Router class
class Router:
    def __init__(self, name, bandwidth, transmission_rate, processing_rate, total_capacity, node_type='router'):
        self.name = name
        self.bandwidth = bandwidth  # Not used directly but can represent link capacity
        self.transmission_rate = transmission_rate  # Not used directly but can represent link speed
        self.total_capacity = total_capacity  # Total memory capacity in MB
        self.memory_space = 0  # Current memory usage in MB
        self.processing_rate = processing_rate  # Packets processed per time unit
        self.neighbors = []
        self.routing_table = {}
        self.node_type = node_type  # 'router' or 'server'
        self.received_data = []  # List to store received packets information
        self.packet_loss_prob = 0.0  # Packet loss probability, calculated dynamically
        if self.name == 'Smart Router':
            self.routing_probabilities = {}  # Routing probabilities to neighbors
        self.packet_loss_prob_history = []  # History of packet loss probabilities
        self.memory_usage_history = []  # History of memory usage
        self.buffer_capacity = int(total_capacity / 50)  # Buffer capacity in packets (assuming 50 MB per packet)
        self.current_queue_length = 0  # Number of packets in the queue
        self.arrival_count = 0  # Number of packets arrived in the current time unit
        self.time_unit = 1  # Time unit for arrival rate calculation
        self.packet_size = 50  # Packet size in MB
        self.time_elapsed = 0  # Time elapsed for arrival rate calculation
        self.arrival_rate = 0  # Arrival rate (packets per time unit)
        self.last_arrival_time = 0  # Time of the last packet arrival
        self.delay_history = []  # History of delays experienced
        self.reward_history = []  # History of rewards calculated

    def add_neighbor(self, neighbor):
        # Add a neighboring router or server
        self.neighbors.append(neighbor)

    def update_routing_table(self, destination, next_hop):
        # Update the routing table with the next hop to a destination
        self.routing_table[destination.name] = next_hop

    def send_data(self, destination, data_size, path=[], current_time=0):
        # Send data to a destination through the network
        path = path + [self.name]
        if destination in self.neighbors:
            destination.receive_data(data_size, path, current_time)
        else:
            if destination.name in self.routing_table:
                next_hop = self.routing_table[destination.name]
                next_hop.receive_data(data_size, path, current_time)
            else:
                print(f"No route from {self.name} to {destination.name}")

    def simulate_packet_loss(self):
        # Calculate the traffic intensity (rho)
        service_rate = self.processing_rate  # Packets per time unit
        arrival_rate = self.arrival_rate  # Packets per time unit

        if service_rate == 0:
            service_rate = 1e-6  # Avoid division by zero

        rho = arrival_rate / service_rate

        # Ensure rho is less than 1 to avoid instability
        rho = min(rho, 0.999)

        K = self.buffer_capacity  # Buffer capacity in packets

        # Calculate packet loss probability using M/M/1/K formula
        numerator = (1 - rho) * rho ** K
        denominator = 1 - rho ** (K + 1)
        self.packet_loss_prob = numerator / denominator if denominator != 0 else 1.0

        # Ensure packet_loss_prob is between 0 and 1
        self.packet_loss_prob = max(0.0, min(1.0, self.packet_loss_prob))

        # Return True if packet is lost
        is_packet_lost = random.random() < self.packet_loss_prob

        # If packet is lost, decrement queue length (since it wasn't added)
        if is_packet_lost and self.current_queue_length > 0:
            self.current_queue_length -= 1

        return is_packet_lost

    def calculate_queuing_delay(self):
        # Calculate the queuing delay using M/M/1 formula
        service_rate = self.processing_rate  # Packets per time unit
        arrival_rate = self.arrival_rate

        if service_rate == 0:
            service_rate = 1e-6  # Avoid division by zero

        rho = arrival_rate / service_rate

        # Ensure rho is less than 1 to avoid infinite delay
        rho = min(rho, 0.999)

        # Calculate queuing delay
        if service_rate * (1 - rho) > 0:
            D_queue = rho / (service_rate * (1 - rho))
        else:
            D_queue = float('inf')  # System is overloaded

        return D_queue

    def receive_data(self, data_size, path, current_time):
        if self.node_type == 'router':
            # Update arrival count
            self.arrival_count += 1

            # Update time elapsed
            time_difference = current_time - self.last_arrival_time
            self.time_elapsed += time_difference
            self.last_arrival_time = current_time

            # Update arrival rate every time unit
            if self.time_elapsed >= self.time_unit:
                self.arrival_rate = self.arrival_count / self.time_elapsed
                self.arrival_count = 0
                self.time_elapsed = 0

            # Calculate delay
            queuing_delay = self.calculate_queuing_delay()
            packet_delay = queuing_delay  # No additional processing delay in this model

            # Increment queue length if buffer not full
            if self.current_queue_length < self.buffer_capacity:
                self.current_queue_length += 1
                packet_loss = self.simulate_packet_loss()
                self.packet_loss_prob_history.append(self.packet_loss_prob)
            else:
                # Buffer is full, packet is lost
                packet_loss = True
                self.packet_loss_prob = 1.0
                self.packet_loss_prob_history.append(self.packet_loss_prob)
                packet_delay = float('inf')  # Infinite delay due to packet loss

        else:
            # For servers, assume no packet loss and no delay
            packet_loss = False
            packet_delay = 0

        # Store the packet's delay and loss info
        self.received_data.append({
            'data_size': data_size,
            'packet_loss': packet_loss, # Boolean
            'delay': packet_delay
        })

        if packet_loss:
            print(f"Packet lost at {self.name}")
        else:
            # Process the packet (add to memory_space)
            self.memory_space += data_size
            print(f"{self.name} received data at time {current_time:.2f} with delay {packet_delay:.4f}. Memory usage: {self.memory_space}/{self.total_capacity}")

            # Forward packet or send metrics back
            if self.node_type == 'server' and self.name == 'Server B':
                send_metrics_back(path + [self.name], packet_delay)
            else:
                if 'Server B' in self.routing_table:
                    next_hop = self.routing_table['Server B']
                    next_hop.receive_data(data_size, path + [self.name], current_time + packet_delay)
        self.memory_usage_history.append(self.memory_space)
        self.delay_history.append(packet_delay)

    def process_data(self):
        if self.memory_space > 0:
            # Process a fixed amount of data per time unit
            processed_data = self.processing_rate * self.packet_size
            processed_data = min(processed_data, self.memory_space)
            self.memory_space -= processed_data
            # Update queue length
            packets_processed = int(processed_data / self.packet_size)
            self.current_queue_length = max(0, self.current_queue_length - packets_processed)
        else:
            # No data to process
            self.memory_usage_history.append(self.memory_space)
            self.packet_loss_prob_history.append(self.packet_loss_prob)


    def adjust_probabilities(self, next_hop_name, combined_metric):
        # Custom reward system to adjust routing probabilities based on combined metric
        learning_rate = 0.1  # Learning rate for probability adjustment

        # Update the probability for the next hop
        current_prob = self.routing_probabilities[next_hop_name]
        #Gradiend descent
        updated_prob = current_prob + learning_rate * (combined_metric - current_prob)

        # Ensure the probability stays within [0.1, 0.9]
        updated_prob = min(max(updated_prob, 0.1), 0.9)

        self.routing_probabilities[next_hop_name] = updated_prob

        # Adjust the other router's probability
        other_router = 'Router 1' if next_hop_name == 'Router 2' else 'Router 2'
        self.routing_probabilities[other_router] = 1.0 - updated_prob

        print(f"Updated routing probabilities: {self.routing_probabilities}")

        # Record the reward (combined metric) for analysis
        self.reward_history.append({
            'router': next_hop_name,
            'reward': combined_metric
        })

# Function to send metrics back to Smart Router
def send_metrics_back(path, packet_delay):
    print(f"Server B is sending metrics to Smart Router")
    smart_router = next((node for node in nodes if node.name == 'Smart Router'), None)
    if smart_router:
        if 'Smart Router' in path:
            smart_router_index = path.index('Smart Router')
            if smart_router_index + 1 < len(path):
                next_hop_name = path[smart_router_index + 1]
                next_hop = next((node for node in nodes if node.name == next_hop_name), None)
                if next_hop_name in smart_router.routing_probabilities and next_hop:
                    # Use packet_loss and delay as metrics
                    if next_hop.received_data:
                        # Get the last packet's information
                        packet_info = next_hop.received_data[-1]
                        packet_loss = packet_info['packet_loss']
                        delay = packet_info['delay']

                        # Use packet_loss_prob from the router
                        packet_loss_prob = next_hop.packet_loss_prob

                        # Normalize delay
                        normalized_delay = max_delay - min(delay, max_delay)
                        delay_metric = normalized_delay / max_delay

                        # Combined metric considering both packet loss probability and delay
                        combined_metric = (1 - packet_loss_prob) * delay_metric


                        print(f"Combined metric for {next_hop_name}: {combined_metric:.4f}")

                        # Adjust routing probabilities based on combined metric
                        smart_router.adjust_probabilities(next_hop_name, combined_metric)

                        # Record metrics for plotting
                        probabilities_over_time.append((
                            smart_router.routing_probabilities.get('Router 1', 0),
                            smart_router.routing_probabilities.get('Router 2', 0)
                        ))
                        chosen_routers.append(next_hop_name)
                        reward_over_time.append(combined_metric)
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
    total_capacity=500,
    processing_rate=50  # Adjusted processing rate for Smart Router
)
router1 = Router(
    name='Router 1',
    bandwidth=80,
    transmission_rate=800,
    total_capacity=420,
    processing_rate=20  # Lower processing rate to induce congestion
)
router2 = Router(
    name='Router 2',
    bandwidth=90,
    transmission_rate=900,
    total_capacity=520,
    processing_rate=100  # Higher processing rate
)
server_A = Router(
    name='Server A',
    bandwidth=1000,
    transmission_rate=2000,
    total_capacity=1000,
    processing_rate=100,
    node_type='server'
)
server_B = Router(
    name='Server B',
    bandwidth=1000,
    transmission_rate=2000,
    total_capacity=1000,
    processing_rate=100,
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
delay_router1 = []
delay_router2 = []
memory_usage_router1 = []
memory_usage_router2 = []
chosen_routers = []
reward_over_time = []

# Define maximum expected delay (for normalization)
max_delay = 0.5  # Adjust based on expected maximum delay in the network

# Function to simulate network traffic and Smart Router's learning
# Function to simulate network traffic with Poisson and Exponential distributions
def simulate_traffic(num_iterations):
    current_time = 0  # Initialize simulation time

    for i in range(num_iterations):
        print(f"\nIteration {i+1}")
        path = []

        # Generate number of packets using Poisson distribution
        lam = 5  # Average rate (events per time unit)
        total_time = 10  # Time period per iteration
        num_packets = np.random.poisson(lam * total_time)

        # Generate inter-arrival times using Exponential distribution based on
        # poisson distrubution
        inter_arrival_times = np.random.exponential(scale=1 / lam, size=num_packets)

        # Calculate cumulative arrival times, starting from the last arrival time
        arrival_times = current_time + np.cumsum(inter_arrival_times)

        # Filter arrival times to ensure they fall within the current iteration's period
        arrival_times = arrival_times[arrival_times <= current_time + total_time]

        # Update current_time to the last arrival time in this iteration
        if len(arrival_times) > 0:
            current_time = arrival_times[-1]
        else:
            current_time += total_time  # Move to the next iteration's start time if no packets

        # commment out
        # print(f"Number of packets to send: {len(arrival_times)}")
        # print("arrival times: \n" + str(arrival_times))

        # Simulate sending the packets at their arrival times
        for packet_time in arrival_times:
            data_size = 50  # MB per packet
            current_time = packet_time  # Update current_time to the packet's arrival time

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
            server_A.send_data(smart_router, data_size, path, current_time)

            # Process data at all routers and server_B
            for router in [smart_router, router1, router2, server_B]:
                router.process_data()

            # Collect packet loss probabilities and memory usage for plotting
            packet_loss_probs_router1.append(router1.packet_loss_prob)
            packet_loss_probs_router2.append(router2.packet_loss_prob)
            memory_usage_router1.append(router1.memory_space)
            memory_usage_router2.append(router2.memory_space)

            # Collect delays for plotting
            if next_hop_name == 'Router 1':
                delay_router1.append(router1.delay_history[-1])
                delay_router2.append(None)
            else:
                delay_router1.append(None)
                delay_router2.append(router2.delay_history[-1])

        # Update current_time to the end of this iteration
        current_time += total_time

# Run the simulation
simulate_traffic(25)

# Plotting
iterations = list(range(1, len(probabilities_over_time) + 1))
if iterations:
    prob_router1 = [prob[0] for prob in probabilities_over_time]
    prob_router2 = [prob[1] for prob in probabilities_over_time]

    plt.figure(figsize=(15, 12))

    # Plot Routing Probabilities Over Time
    plt.subplot(4, 1, 1)
    plt.plot(iterations, prob_router1, label='Probability of Router 1')
    plt.plot(iterations, prob_router2, label='Probability of Router 2')
    plt.xlabel('Iteration')
    plt.ylabel('Routing Probability')
    plt.title('Smart Router Routing Probabilities Over Time')
    plt.legend()

    # Plot Packet Loss Probability of Routers Over Time
    plt.subplot(4, 1, 2)
    plt.plot(packet_loss_probs_router1, label='Packet Loss Prob - Router 1')
    plt.plot(packet_loss_probs_router2, label='Packet Loss Prob - Router 2')
    plt.xlabel('Packet Number')
    plt.ylabel('Packet Loss Probability')
    plt.title('Packet Loss Probability of Routers Over Time')
    plt.legend()

    # Plot Delays Over Time
    plt.subplot(4, 1, 3)
    plt.plot(delay_router1, label='Delay - Router 1')
    plt.plot(delay_router2, label='Delay - Router 2')
    plt.xlabel('Packet Number')
    plt.ylabel('Delay (Time Units)')
    plt.title('Packet Delay Over Time')
    plt.legend()

    # Plot Router Choices Over Time
    plt.subplot(4, 1, 4)
    router_choices = [1 if name == 'Router 1' else 2 for name in chosen_routers]
    plt.plot(iterations, router_choices, 'o-')
    plt.xlabel('Iteration')
    plt.ylabel('Chosen Router')
    plt.yticks([1,2], ['Router 1', 'Router 2'])
    plt.title('Router Choices Over Time')

    plt.tight_layout()
    plt.show()

    # Plot Reward Over Time
    plt.figure(figsize=(10, 5))
    plt.plot(iterations, reward_over_time, label='Reward (Combined Metric)')
    plt.xlabel('Iteration')
    plt.ylabel('Reward')
    plt.title('Reward Over Time')
    plt.legend()
    plt.show()
else:
    print("No data to plot.")
