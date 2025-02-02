"""
Name: Hakan Bektas
Email: hakanbektas2@student.uva.nl /
       hakanbektas934@outlook.com
University: University of Amsterdam

Description:
This simulation implements a fixed routing decision mechanism where two
routers are simulated. Router2 is always chosen, but its delay vary due to
manually introduced delays.

Experiment Overview:
- Router1 has a fixed base delay.
- Router2 has a lower base delay (thus better) except during iterations 20 to
  40, when an extra delay is imposed.
- The simulation logs the chosen router, delays for both routers, and fixed
  probabilities.
- Results are plotted in three subplots: fixed routing probabilities, router
  choices, and delays over iterations.
"""

import random
import matplotlib.pyplot as plt

totalIterations = 80

baseDelayR1 = 1.2  # Router1's base propagation delay
baseDelayR2 = 0.7  # Router2's base propagation delay (the better one)

delayAdjustStart = 20
delayAdjustEnd = 40
extraDelay = 1.0  # Extra delay imposed on Router2

probR1 = 0.1
probR2 = 0.9

chosenRouterLog = []     # Which router was chosen each iteration
delayLogR1 = []          # Active delay of Router1
delayLogR2 = []          # Active delay of Router2
probabilityLog = []      # Probability logs for both routers

class Router:
    def __init__(self, name, baseDelay):
        self.name = name
        self.baseDelay = baseDelay
        self.extraOverhead = 0.0  # Can be changed at runtime

    def getCurrentDelay(self, iteration):
        # Introduce extra delay for Router2 between specified iterations
        if (self.name == "Router2" and
            delayAdjustStart <= iteration < delayAdjustEnd):
            return self.baseDelay + extraDelay
        return self.baseDelay

def runSimulation():
    router1 = Router("Router1", baseDelay=baseDelayR1)
    router2 = Router("Router2", baseDelay=baseDelayR2)

    for i in range(totalIterations):
        # Router2 is always selected as the preferred choice
        chosen = "Router2"

        # Measure delays
        delayR1 = router1.getCurrentDelay(i)
        delayR2 = router2.getCurrentDelay(i)

        # Log data
        chosenRouterLog.append(chosen)
        delayLogR1.append(delayR1)
        delayLogR2.append(delayR2)
        probabilityLog.append((probR1, probR2))

def plotResults():
    iters = range(totalIterations)

    # Subplot 1: Probability evolution
    probR1List = [p[0] for p in probabilityLog]
    probR2List = [p[1] for p in probabilityLog]

    plt.figure(figsize=(10, 4))
    plt.plot(iters, probR1List, label="Prob(Router1)", color='blue')
    plt.plot(iters, probR2List, label="Prob(Router2)", color='orange')
    plt.ylim([0, 1])
    plt.title("Fixed Routing Probability Over Time")
    plt.xlabel("Iteration")
    plt.ylabel("Probability")
    plt.legend()
    plt.show()

    # Subplot 2: Which router was chosen
    plt.figure(figsize=(10, 4))
    x2 = range(len(chosenRouterLog))
    y2 = [1 if c == "Router1" else 2 for c in chosenRouterLog]
    plt.plot(x2, y2, 'o-')
    plt.yticks([1, 2], ["Router1", "Router2"])
    plt.title("Which Router Was Chosen")
    plt.ylabel("Chosen Router")
    plt.xlabel("Iteration #")
    plt.show()

    # Subplot 3: Delays
    plt.figure(figsize=(10, 4))
    plt.plot(delayLogR1, '.', color='blue', label='Router1 Delay')
    plt.plot(delayLogR2, '.', color='orange', label='Router2 Delay')
    plt.title("Router Delays Each Iteration (Base + Overhead)")
    plt.ylabel("Delay")
    plt.xlabel("Iteration #")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    runSimulation()
    plotResults()
