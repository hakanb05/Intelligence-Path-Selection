# Pure created for the purpose of getting the average delays, anything which is
# not related to the average delays is omitted.

import matplotlib.pyplot as plt
import random

# ---------- Settigs ----------
totalIterations = 80
baseDelayR1 = 1.2
baseDelayR2 = 0.2

# ---------- Delay function ----------
def getRouter2Delay(iteration):
    if 20 <= iteration < 40:
        return baseDelayR2 + 2.3
    elif 60 <= iteration < 70:
        return baseDelayR2 + 0.5
    else:
        return baseDelayR2 + 0.0

# ---------- Reinforcement router ----------
class SmartRouter:
    def __init__(self):
        self.probabilities = {"Router1": 0.5, "Router2": 0.5}
        self.learningRate = 0.23

    def choose(self):
        p1 = self.probabilities["Router1"]
        p2 = self.probabilities["Router2"]
        if p1 > p2:
            p1_adj = min(1.0, p1 + 0.2)
            p2_adj = max(0.0, 1.0 - p1_adj)
        else:
            p2_adj = min(1.0, p2 + 0.1)
            p1_adj = max(0.0, 1.0 - p2_adj)
        return random.choices(["Router1", "Router2"], weights=[p1_adj, p2_adj])[0]

    def update(self, chosen, reward):
        old = self.probabilities[chosen]
        new = old + self.learningRate * (reward - old)
        new = max(0.05, min(0.95, new))
        self.probabilities[chosen] = new
        self.probabilities["Router1" if chosen == "Router2" else "Router2"] = 1.0 - new

def runReinforcement():
    router = SmartRouter()
    delays = []

    for i in range(totalIterations):
        delay1 = baseDelayR1
        delay2 = getRouter2Delay(i)

        chosen = router.choose()
        if chosen == "Router1":
            delay = delay1
        else:
            delay = delay2

        reward = max(0.0, min(1.0, 1.0 - (delay / 2.5)))
        router.update(chosen, reward)
        delays.append(delay)

    return delays

# ---------- Naive router ----------
def runNaive():
    delays = []
    for i in range(totalIterations):
        delay = getRouter2Delay(i)
        delays.append(delay)
    return delays

# ---------- Plot ----------
def plotAndCompare(rDelays, nDelays):
    avgR = sum(rDelays) / len(rDelays)
    avgN = sum(nDelays) / len(nDelays)

    # Print exact waarden
    print(f"Average Delay - Reinforcement: {avgR:.3f}")
    print(f"Average Delay - Naive:         {avgN:.3f}")

    # Staafdiagram
    labels = ['Reinforcement', 'Naive']
    averages = [avgR, avgN]
    colors = ['purple', 'blue']

    plt.figure(figsize=(6, 5))
    plt.bar(labels, averages, color=colors)
    plt.ylabel("Average Delay")
    plt.title("Average Delay Comparison")
    plt.ylim(0, max(averages) + 0.5)
    for i, v in enumerate(averages):
        plt.text(i, v + 0.05, f"{v:.2f}", ha='center', fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()


# ---------- Main ----------
if __name__ == "__main__":
    reinforcementDelays = runReinforcement()
    naiveDelays = runNaive()
    plotAndCompare(reinforcementDelays, naiveDelays)
