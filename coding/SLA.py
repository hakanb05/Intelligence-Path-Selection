import gymnasium as gym

env = gym.make('Taxi-v3', render_mode="rgb_array")
env.reset()

# Provided by the tutorial, but led to an error.
# state = env.encode(3, 1, 2, 0)

# Use unwrapped to get access to the encode method.
# (taxi row, taxi column, passenger index, destination index)
state = env.unwrapped.encode(3, 1, 2, 0)
print("State:", state)

env.s = state

env.render()

print("Action Space {}".format(env.action_space))
print("State Space {}".format(env.observation_space))
