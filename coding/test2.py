import random
import matplotlib.pyplot as plt
import numpy as np

# Define maximum expected delay (for normalization)
max_delay = 0.5  # Adjust based on expected maximum delay in the network

# Convergence parameters
CONVERGENCE_THRESHOLD = 0.01   # Probability change threshold
CONVERGENCE_COUNT = 5          # Number of consecutive stable iterations required
convergence_stable_count = 0   # Counter for stable iterations
converged = False              # Flag to indicate if the system has converged

# Additional Parameters for alternating between learning and inference
MIN_LEARNING_ITERATIONS = 20   # Minimum learning iterations before checking convergence
INFERENCE_ITERATIONS = 10      # Number of iterations to run in inference mode after convergence
phase = 'learning'             # Can be 'learning' or 'inference'
phase_iteration = 0            # Count iterations in the current phase

class Router:
    def __init__(self, name, bandwidth, transmission_rate, processing_rate, total_capacity, node_type='router'):
        self.name = name
        self.bandwidth = bandwidth
        self.transmission_rate = transmission_rate
        self.total_capacity = total_capacity  # MB
        self.memory_space = 0  # Current memory usage in MB
        self.processing_rate = processing_rate  
        self.neighbors = []
        self.routing_table = {}
        self.node_type = node_type
        self.received_data = []
        self.packet_loss_prob = 0.0
        
        # Als dit de "Smart Router" is, krijgt-ie een routing_probabilities dict.
        if self.name == 'Smart Router':
            self.routing_probabilities = {}

        self.packet_loss_prob_history = []
        self.memory_usage_history = []
        # Elk pakket is 50MB, dus buffer_capacity is total_capacity // 50
        self.buffer_capacity = int(total_capacity / 50)
        self.current_queue_length = 0
        
        self.arrival_count = 0
        self.time_unit = 1
        self.packet_size = 50  # MB
        self.time_elapsed = 0
        self.arrival_rate = 0
        self.last_arrival_time = 0

        self.delay_history = []
        self.reward_history = []

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def update_routing_table(self, destination, next_hop):
        self.routing_table[destination.name] = next_hop

    def send_data(self, destination, data_size, path=[], current_time=0):
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
        if self.processing_rate == 0:
            service_rate = 1e-6
        else:
            service_rate = self.processing_rate

        rho = self.arrival_rate / service_rate
        rho = min(rho, 0.999)

        K = self.buffer_capacity
        numerator = (1 - rho) * (rho ** K)
        denominator = 1 - rho ** (K + 1)
        self.packet_loss_prob = numerator / denominator if denominator != 0 else 1.0
        self.packet_loss_prob = max(0.0, min(1.0, self.packet_loss_prob))

        is_packet_lost = random.random() < self.packet_loss_prob
        if is_packet_lost and self.current_queue_length > 0:
            self.current_queue_length -= 1
        return is_packet_lost

    def calculate_queuing_delay(self):
        if self.processing_rate == 0:
            service_rate = 1e-6
        else:
            service_rate = self.processing_rate

        rho = self.arrival_rate / service_rate
        rho = min(rho, 0.999)

        if service_rate * (1 - rho) > 0:
            D_queue = rho / (service_rate * (1 - rho))
        else:
            D_queue = float('inf')
        return D_queue

    def receive_data(self, data_size, path, current_time):
        # Als dit een router is, bereken arrival rate etc.
        if self.node_type == 'router':
            self.arrival_count += 1
            time_difference = current_time - self.last_arrival_time
            self.time_elapsed += time_difference
            self.last_arrival_time = current_time

            if self.time_elapsed >= self.time_unit:
                self.arrival_rate = self.arrival_count / self.time_elapsed
                self.arrival_count = 0
                self.time_elapsed = 0

            queuing_delay = self.calculate_queuing_delay()
            packet_delay = queuing_delay

            if self.current_queue_length < self.buffer_capacity:
                self.current_queue_length += 1
                packet_loss = self.simulate_packet_loss()
                self.packet_loss_prob_history.append(self.packet_loss_prob)
            else:
                # Buffer vol => packet lost
                packet_loss = True
                self.packet_loss_prob = 1.0
                self.packet_loss_prob_history.append(self.packet_loss_prob)
                packet_delay = float('inf')
        else:
            # server
            packet_loss = False
            packet_delay = 0

        self.received_data.append({
            'data_size': data_size,
            'packet_loss': packet_loss,
            'delay': packet_delay
        })

        if packet_loss:
            print(f"Packet lost at {self.name}")
        else:
            # Packet arrives in memory
            self.memory_space += data_size
            if (self.name != "Server B" and self.name != "Smart Router"):
                print(f"{self.name} received data at time {current_time:.2f} "
                    f"with delay {packet_delay:.4f}. "
                    f"Memory usage: {self.memory_space}/{self.total_capacity}")

            if self.node_type == 'server' and self.name == 'Server B':
                send_metrics_back(path + [self.name], packet_delay)
            else:
                if ('Server B' in self.routing_table):
                    next_hop = self.routing_table['Server B']
                    next_hop.receive_data(data_size, path + [self.name], current_time + packet_delay)

        self.memory_usage_history.append(self.memory_space)
        self.delay_history.append(packet_delay)

    def process_data(self):
        """
        We override the default approach: 
        - Router 1 processes 39MB each time it's called.
        - Router 2 processes 43MB each time it's called.
        - Smart Router or other nodes can keep the old approach or 
          we define a custom approach for them as well.
        """
        if self.memory_space > 0:
            # Default processed_data
            processed_data = 0

            if self.name == 'Router 1':
                # Router 1 processes 39 MB each time
                processed_data = 39  
            elif self.name == 'Router 2':
                # Router 2 processes 43 MB each time
                processed_data = 43 
            else:
                # Smart Router or other node => keep the old approach?
                processed_data = self.processing_rate * self.packet_size

            # We cannot process more than we have
            processed_data = min(processed_data, self.memory_space)
            self.memory_space -= processed_data

            # Each 'processed_data' chunk corresponds to processed_data MB
            # Because each 'packet' is 50MB, but we are ignoring partial packets logic here.
            # If you want partial packets => you could interpret this differently.
            # For now, we assume each MB is just data, no strict packet boundaries.

            # Let's also reduce the queue_length accordingly
            # If 'processed_data' is the number of MB removed, how many packets is that?
            # We'll do integer division by 50 to see how many 'full' 50MB chunks are removed from the queue. 
            # This is a simplificatie, want in real scenario is partial packet processing. 
            full_packets_processed = int(processed_data // 50)  
            self.current_queue_length = max(0, self.current_queue_length - full_packets_processed)
        else:
            # No data to process => log
            self.memory_usage_history.append(self.memory_space)
            self.packet_loss_prob_history.append(self.packet_loss_prob)

    def adjust_probabilities(self, next_hop_name, combined_metric):
        global converged, convergence_stable_count, phase, phase_iteration

        if phase == 'inference':
            return

        learning_rate = 0.1
        current_prob = self.routing_probabilities[next_hop_name]
        updated_prob = current_prob + learning_rate * (combined_metric - current_prob)

        updated_prob = min(max(updated_prob, 0.1), 0.9)
        diff = abs(updated_prob - current_prob)

        self.routing_probabilities[next_hop_name] = updated_prob

        other_router = 'Router 1' if next_hop_name == 'Router 2' else 'Router 2'
        self.routing_probabilities[other_router] = 1.0 - updated_prob

        print(f"Updated routing probabilities: {self.routing_probabilities}")

        self.reward_history.append({
            'router': next_hop_name,
            'reward': combined_metric
        })

        if phase_iteration >= MIN_LEARNING_ITERATIONS:
            if diff < CONVERGENCE_THRESHOLD:
                convergence_stable_count += 1
            else:
                convergence_stable_count = 0

            if convergence_stable_count >= CONVERGENCE_COUNT:
                converged = True
                print("Converged! Entering inference phase.")
                switch_to_inference_phase()

def switch_to_inference_phase():
    global phase, phase_iteration
    phase = 'inference'
    phase_iteration = 0
    print("Switching to inference phase. No learning adjustments will be made for a while.")

def switch_to_learning_phase():
    global converged, phase, phase_iteration, convergence_stable_count
    phase = 'learning'
    phase_iteration = 0
    converged = False
    convergence_stable_count = 0
    print("Re-entering learning phase after inference phase.")

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
                    if next_hop.received_data:
                        packet_info = next_hop.received_data[-1]
                        packet_loss = packet_info['packet_loss']
                        delay = packet_info['delay']
                        packet_loss_prob = next_hop.packet_loss_prob

                        normalized_delay = max_delay - min(delay, max_delay)
                        delay_metric = normalized_delay / max_delay

                        if packet_loss:
                            combined_metric = 0
                        else:
                            combined_metric = (1 - packet_loss_prob) * delay_metric

                        print(f"Combined metric for {next_hop_name}: {combined_metric:.4f}")

                        smart_router.adjust_probabilities(next_hop_name, combined_metric)

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

# Instantiate the network
smart_router = Router(
    name='Smart Router',
    bandwidth=100,
    transmission_rate=1000,
    total_capacity=500,
    processing_rate=50
)

router1 = Router(
    name='Router 1',
    bandwidth=80,
    transmission_rate=800,
    total_capacity=420,
    processing_rate=20  # We don't use this for the actual processing MB, but it's a param
)

router2 = Router(
    name='Router 2',
    bandwidth=90,
    transmission_rate=90,
    total_capacity=52,
    processing_rate=10  # again, used in arrival rate calc, but we override memory processing
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

smart_router.update_routing_table(destination=server_B, next_hop=None)
router1.update_routing_table(destination=server_B, next_hop=server_B)
router2.update_routing_table(destination=server_B, next_hop=server_B)

smart_router.routing_probabilities = {'Router 1': 0.5, 'Router 2': 0.5}

nodes = [smart_router, router1, router2, server_A, server_B]

probabilities_over_time = []
chosen_routers = []
reward_over_time = []

def simulate_traffic(num_iterations):
    global phase, phase_iteration, converged
    current_time = 0
    for i in range(num_iterations):
        phase_iteration += 1
        print(f"\nIteration {i+1}, Phase: {phase}, Iter: {phase_iteration} in this phase")

        if phase == 'inference':
            if phase_iteration > INFERENCE_ITERATIONS:
                switch_to_learning_phase()
        # If learning phase and converged is True => we don't forcibly switch here
        # the transition is triggered in adjust_probabilities

        total_time = 10
        lam = 5
        num_packets = np.random.poisson(lam * total_time)

        inter_arrival_times = np.random.exponential(scale=1 / lam, size=num_packets)
        arrival_times = current_time + np.cumsum(inter_arrival_times)
        arrival_times = arrival_times[arrival_times <= current_time + total_time]

        if len(arrival_times) > 0:
            current_time = arrival_times[-1]
        else:
            current_time += total_time

        for packet_time in arrival_times:
            data_size = 50
            current_time = packet_time

            next_hop_name = random.choices(
                population=['Router 1', 'Router 2'],
                weights=[
                    smart_router.routing_probabilities.get('Router 1', 0),
                    smart_router.routing_probabilities.get('Router 2', 0)
                ],
                k=1
            )[0]

            if next_hop_name == 'Router 1':
                next_hop = router1
            else:
                next_hop = router2

            smart_router.update_routing_table(destination=server_B, next_hop=next_hop)

            # Server A sends data => smart router => ...
            server_A.send_data(smart_router, data_size, [], current_time)

            # process data in all routers
            for r in [smart_router, router1, router2, server_B]:
                r.process_data()

        current_time += total_time

# Run the simulation
simulate_traffic(5)

# Plot results
iterations = list(range(1, len(probabilities_over_time) + 1))
if iterations:
    prob_router1 = [prob[0] for prob in probabilities_over_time]
    prob_router2 = [prob[1] for prob in probabilities_over_time]

    plt.figure(figsize=(10, 6))
    plt.plot(iterations, prob_router1, label='Prob Router 1')
    plt.plot(iterations, prob_router2, label='Prob Router 2')
    plt.xlabel('Iteration')
    plt.ylabel('Probability')
    plt.title('Routing Probabilities Over Time')
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 6))
    plt.plot(iterations, reward_over_time, label='Reward (Combined Metric)')
    plt.xlabel('Iteration')
    plt.ylabel('Reward')
    plt.title('Reward Over Time')
    plt.legend()
    plt.show()

    plt.figure(figsize=(10, 6))
    router_choices = [1 if name == 'Router 1' else 2 for name in chosen_routers]
    plt.plot(iterations, router_choices, 'o-')
    plt.xlabel('Iteration')
    plt.ylabel('Chosen Router')
    plt.yticks([1,2], ['Router 1', 'Router 2'])
    plt.title('Router Choices Over Time')
    plt.show()
else:
    print("No data to plot.")
