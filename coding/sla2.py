# Another failed attempt
import gym
import random

env = gym.make('CartPole-v1')
states = env.observation_space.shape[0]
actions = env.action_space.n

episodes = 10

for episode in range(1, episodes + 1):
    state = env.reset()
    done = False
    score = 0

    while not done:
        env.render()
        action = random.choice([0, 1])
        n_state, reward, done, truncated, info = env.step(action)
        score += reward
    print("Episode: {} Score{}".format(episode, score))
