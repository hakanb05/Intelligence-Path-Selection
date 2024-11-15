import random
import matplotlib.pyplot as plt
import time

class Router:
    def __init__(self, name, bandwidth, transmission_rate, total_capacity):
        self.name = name
        self.bandwidth = bandwidth  # in Mbps
        self.transmission_rate = transmission_rate  # in packets per second
        self.total_capacity = total_capacity  # in MB
        self.memory_space = 0  # current usage in MB
        self.neighbors = []
        self.routing_table = [[None for _ in range(4)] for _ in range(4)]  # 2D array for routes
        self.total_wasted = 0  # Total wasted capacity over time

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def update_routing_table(self, destination, next_hop):
        # Update routing table for SLA with destination and next hop router
        self.routing_table[self.name][destination.name] = next_hop.name

    def send_data(self, destination, data="Hello, world!"):
        if destination in self.neighbors:
            print(f"Router {self.name} -> {destination.name}: {data}")
        else:
            print(f"No direct route from {self.name} to {destination.name}.")

    def receive_data(self, data_size):
        # Simulate receiving data and update memory usage and waste tracking
        if self.memory_space + data_size <= self.total_capacity:
            self.memory_space += data_size
            return 0  # No waste
        else:
            # Calculate waste when over capacity
            wasted = data_size - (self.total_capacity - self.memory_space)
            self.total_wasted += wasted  # Track total wasted capacity
            self.memory_space = self.total_capacity  # Cap memory usage at total capacity
            return wasted

def generate_fake_traffic(router, destination, duration=30, data_size=50):
    start_time = time.time()
    time_data = []
    speed_data = []
    memory_data = []
    wasted_data = []

    while time.time() - start_time < duration:
        router.send_data(destination)

        # Simulate receiving data and track wasted capacity
        wasted = router.receive_data(data_size)
        memory_data.append(router.total_capacity - router.memory_space)
        wasted_data.append(router.total_wasted)  # Accumulate total wasted

        # Collect time and transmission speed data
        time_data.append(time.time() - start_time)
        speed_data.append(random.uniform(0, router.transmission_rate))

        time.sleep(1)  # Wait for simulation time

    return time_data, speed_data, memory_data, wasted_data

# Create Router objects
r1 = Router(name=0, bandwidth=100, transmission_rate=1000, total_capacity=500)
r2 = Router(name=1, bandwidth=80, transmission_rate=800, total_capacity=400)

# Define neighbors
r1.add_neighbor(r2)
r2.add_neighbor(r1)

# Update Routing tables
r1.update_routing_table(destination=r2, next_hop=r2)
r2.update_routing_table(destination=r1, next_hop=r1)

# Generate traffic data and display in plots
time_data, speed_data, memory_data, wasted_data = generate_fake_traffic(r1, r2)

# Combined plot with three subplots
fig, axs = plt.subplots(3, 1, figsize=(10, 12))
fig.suptitle("Router Traffic Simulation Data")

# Plot for Transmission Rate
axs[0].plot(time_data, speed_data, label=f"Router {r1.name} -> Router {r2.name}")
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("Transmission Rate (packets/s)")
axs[0].set_title("Transmission Rate over Time")
axs[0].legend()

# Plot for Available Memory Space
axs[1].plot(time_data, memory_data, label="Available Memory Space (MB)")
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Available Memory (MB)")
axs[1].set_title("Memory Availability over Time")
axs[1].legend()

# Plot for Total Wasted Capacity
axs[2].plot(time_data, wasted_data, label="Total Wasted Capacity (MB)", color='red')
axs[2].set_xlabel("Time (s)")
axs[2].set_ylabel("Total Wasted (MB)")
axs[2].set_title("Total Wasted Capacity over Time")
axs[2].legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
