"""
Name: Hakan Bektas
Email: hakanbektas2@student.uva.nl / hakanbektas934@outlook.com
University: University of Amsterdam

Description:
This simulation implements a Q-learning agent that learns to navigate a taxi.
The agent learns to pick up a passenger and drop them off at the correct
destination while avoiding penalties. The Q-learning algorithm is used to
update the Q-values in a Q-table based on the rewards received.

Experiment Overview:
1. The agent is trained over 100,000 episodes to learn the optimal policy.
2. After training, the agent's performance is evaluated over 100 episodes to
   measure the average timesteps and penalties per episode.

This was the first simulation I have written using Rl, the idea was to understand
the main core idea of Reinforcement Learning. The simulation is based on the
Taxi-v3 environment from OpenAI Gym. I have used online resources and
documentation to understand and implement the Q-learning algorithm.
"""

import gymnasium as gym
import numpy as np
import random

# Initialize the Taxi-v3 environment
env = gym.make('Taxi-v3', render_mode="rgb_array")
env.reset()

# Create a Q-table with zeros, dimensions are state space size by action space
# size
q_table = np.zeros([env.observation_space.n, env.action_space.n])

# Set the hyperparameters for learning rate (alpha), discount factor (gamma),
# and epsilon for exploration
alpha = 0.1
gamma = 0.6
epsilon = 0.1

# Create lists to track statistics for epochs and penalties
all_epochs = []
all_penalties = []

# Train the agent over 100,000 episodes
for i in range(1, 100001):
    # Reset the environment and get the initial state
    state, _ = env.reset()

    # Initialize variables for tracking the number of steps (epochs), penalties,
    # and reward
    epochs, penalties, reward = 0, 0, 0
    done = False

    while not done:
        # Use epsilon-greedy strategy to select an action
        if random.uniform(0, 1) < epsilon:
            #  Explore by choosing a random action
            action = env.action_space.sample()
        else:
            # Exploit by choosing the best known action
            action = np.argmax(q_table[state])

        # Perform the chosen action and get the results
        next_state, reward, done, _, info = env.step(action)

        # Retrieve the old Q-value for the current state-action pair
        old_value = q_table[state, action]

        # Get the maximum Q-value for the next state
        next_max = np.max(q_table[next_state])

        # Calculate the new Q-value using the Q-learning formula
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value

        # Increment the penalties counter if a penalty reward is received
        if reward == -10:
            penalties += 1

        # Update the state to the next state and increment the step count
        state = next_state
        epochs += 1

    # Print progress every 10,000 episodes
    if i % 10000 == 0:
        print(f"Episode: {i}")

# Indicate that the training has finished
print("Training finished.\n")

# Evaluate the agent's performance after training
print("\nEvaluating the agent's performance after training...")

# Initialize counters for total steps (epochs) and penalties across all
# evaluation episodes
total_epochs, total_penalties = 0, 0
episodes = 100

# Evaluate the agent over 100 episodes
for _ in range(episodes):
    # Reset the environment and get the initial state
    state, _ = env.reset()
    epochs, penalties, reward = 0, 0, 0

    done = False

    while not done:
        # Always choose the best action according to the Q-table
        action = np.argmax(q_table[state])

        # Perform the chosen action and get the results
        next_state, reward, done, _, info = env.step(action)

        # Increment penalties if a penalty reward is received
        if reward == -10:
            penalties += 1

        # Update the state to the next state and increment the step count
        state = next_state
        epochs += 1

    # Add the number of steps and penalties to the total count
    total_penalties += penalties
    total_epochs += epochs

# Print the evaluation results
print(f"Results after {episodes} episodes:")
print(f"Average timesteps per episode: {total_epochs / episodes}")
print(f"Average penalties per episode: {total_penalties / episodes}")