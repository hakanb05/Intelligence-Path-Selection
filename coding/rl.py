"""
Name: Hakan Bektas
Email: hakanbektas2@student.uva.nl / hakanbektas934@outlook.com
University: University of Amsterdam

Description:
This simulation implements an intelligent routing mechanism where a Smart Router
learns which of two routers (Router 1 or Router 2) is the better choice based on
their delay times. The routing probabilities are updated using a reinforcement
learning approach.

Experiment Overview:
1. Initially, Router 2 is better (lower delay).
2. Between iteration 20 and 40, additional delay is introduced to Router 2, making
   Router 1 the preferred choice, leading to system convergence.
3. After iteration 40, the extra delay is removed, making Router 2 the better
   choice again, and the system reconverges.

The simulation alternates between learning and inference phases:
- During the learning phase, the Smart Router adjusts its routing
  probabilities based on observed delays.
- During the inference phase, it uses the last learned probabilities without
  adjustments.

The goal is to observe how the system adapts to changing network conditions.
"""

import random
import matplotlib.pyplot as plt

# Global Configuration
learningIterations = 29  # Number of learning iterations before checking
                       # for convergence
convergenceThreshold = 0.05  # Probability difference threshold
convergenceCount = 3  # Consecutive stable updates for convergence
inferenceIterations = 15  # Iterations in inference mode
maxSimulationStages = 4  # Total phases possible (e.g. learning->inference->...)

phaseLearning = "learning"
phaseInference = "inference"

baseDelayR1 = 1.2  # Router1's base propagation delay
baseDelayR2 = 0.7  # Router2's base propagation delay (better one)

# Logs
probabilitiesLog = []  # List of (iteration, pRouter1, pRouter2)
choiceLog = []  # Which router was chosen each iteration
delayLogR1 = []  # Active delay of Router1 per iteration
delayLogR2 = []  # Active delay of Router2 per iteration
phaseLog = []  # List of (iteration, phase) for current phase
switchPoints = []  # Iteration indices where phase switches occur

# Phase / convergence state
currentPhase = phaseLearning
phaseIteration = 0
convergenceStableCount = 0
converged = False
phaseSwitchCount = 0

def switchToInferencePhase():
    global currentPhase, phaseIteration, phaseSwitchCount
    currentPhase = phaseInference
    phaseIteration = 0
    phaseSwitchCount += 1
    switchPoints.append(("inference", len(probabilitiesLog)))
    print(f"--- Switching to Inference (phase {phaseSwitchCount}) ---")

def switchToLearningPhase():
    global currentPhase, phaseIteration, converged
    global convergenceStableCount, phaseSwitchCount
    currentPhase = phaseLearning
    phaseIteration = 0
    converged = False
    convergenceStableCount = 0
    phaseSwitchCount += 1
    switchPoints.append(("learning", len(probabilitiesLog)))
    print(f"--- Switching to Learning (phase {phaseSwitchCount}) ---")

class SmartRouter:
    """
    Smart Router that picks Router1 or Router2 based on internal
    probabilities. Probabilities are updated (during learning) using an
    observed metric from delay.
    """
    def __init__(self):
        self.routingProbabilities = {"Router1": 0.5, "Router2": 0.5}
        self.learningRate = 0.1

    def chooseRouter(self):
        r = random.random()
        pR1 = self.routingProbabilities["Router1"]
        if r < pR1:
            return "Router1"
        return "Router2"

    def updateProbability(self, chosenRouter, metricValue):
        """
        In learning phase, update probability as:
        newProb = oldProb + learningRate*(metricValue - oldProb),
        clamped to [0.05, 0.95]. Check for convergence if enough
        iterations have passed.
        """
        global currentPhase, phaseIteration
        global converged, convergenceStableCount

        if currentPhase == phaseInference:
            return  # No update in inference phase

        oldProb = self.routingProbabilities[chosenRouter]
        alpha = self.learningRate
        newProb = oldProb + alpha * (metricValue - oldProb)
        newProb = max(0.05, min(0.95, newProb))
        diff = abs(newProb - oldProb)

        self.routingProbabilities[chosenRouter] = newProb
        if chosenRouter == "Router1":
            self.routingProbabilities["Router2"] = 1.0 - newProb
        else:
            self.routingProbabilities["Router1"] = 1.0 - newProb

        if phaseIteration >= learningIterations:
            if diff < convergenceThreshold:
                convergenceStableCount += 1
            else:
                convergenceStableCount = 0
            if convergenceStableCount >= convergenceCount:
                global phaseSwitchCount
                converged = True
                print("Converged => switching to inference.")
                switchToInferencePhase()

class Router:
    """
    A router with a base delay and adjustable overhead.
    getCurrentDelay() returns the sum of base delay and extra overhead.
    """
    def __init__(self, name, baseDelay):
        self.name = name
        self.baseDelay = baseDelay
        self.extraOverhead = 0.0  # Can be adjusted at runtime

    def getCurrentDelay(self):
        return self.baseDelay + self.extraOverhead

class Environment:
    def __init__(self):
        self.smartRouter = SmartRouter()
        self.router1 = Router("Router1", baseDelay=baseDelayR1)
        self.router2 = Router("Router2", baseDelay=baseDelayR2)

    def runOneIteration(self, iterationIdx):
        # Adjust Router2 overhead to simulate network changes
        if 20 <= iterationIdx < 40:
            self.router2.extraOverhead = 1.0
        elif 40 <= iterationIdx < 60:
            self.router2.extraOverhead = 0.0
        elif 60 <= iterationIdx < 70:
            self.router2.extraOverhead = 0.5
        else:
            self.router2.extraOverhead = 0.0

        chosen = self.smartRouter.chooseRouter()
        if chosen == "Router1":
            usedDelay = self.router1.getCurrentDelay()
        else:
            usedDelay = self.router2.getCurrentDelay()

        baseFactor = 2.0
        raw = 1.0 - (usedDelay / baseFactor)
        metricValue = max(0.0, min(1.0, raw))

        self.smartRouter.updateProbability(chosen, metricValue)
        return (chosen, usedDelay)

def main():
    global currentPhase, phaseIteration, converged
    env = Environment()
    totalIterations = 80  # Total simulation steps

    for i in range(totalIterations):
        if (currentPhase == phaseInference and
                phaseIteration >= inferenceIterations):
            switchToLearningPhase()

        chosen, actualDelay = env.runOneIteration(i)
        pR1 = env.smartRouter.routingProbabilities["Router1"]
        pR2 = env.smartRouter.routingProbabilities["Router2"]
        probabilitiesLog.append((i, pR1, pR2))
        choiceLog.append(chosen)
        delayLogR1.append(env.router1.getCurrentDelay())
        delayLogR2.append(env.router2.getCurrentDelay())
        phaseLog.append((i, currentPhase))
        phaseIteration += 1

        if currentPhase == phaseLearning and converged:
            switchToInferencePhase()

    plotResults()

def plotResults():
    import matplotlib.pyplot as plt
    iterations = [x[0] for x in probabilitiesLog]
    probR1 = [x[1] for x in probabilitiesLog]
    probR2 = [x[2] for x in probabilitiesLog]

    plt.figure(figsize=(10, 10))

    # Subplot 1: Routing probabilities
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(iterations, probR1, color='blue',
             label='Prob(Router1)')
    ax1.plot(iterations, probR2, color='orange',
             label='Prob(Router2)')

    # Mark phase switches
    for i in range(1, len(phaseLog)):
        prevPhase = phaseLog[i - 1][1]
        currPhase = phaseLog[i][1]
        if currPhase != prevPhase:
            switchIter = phaseLog[i][0]
            if currPhase == phaseInference:
                labelText = ("Switch->Inference" if
                             "Switch->Inference" not in
                             ax1.get_legend_handles_labels()[1] else "")
                ax1.scatter(switchIter, 1.05, color='red', marker='x',
                            s=100, label=labelText)
            else:
                labelText = ("Switch->Learning" if
                             "Switch->Learning" not in
                             ax1.get_legend_handles_labels()[1] else "")
                ax1.scatter(switchIter, 1.1, color='green', marker='o',
                            s=100, label=labelText)

    ax1.set_ylim([0, 1.2])
    ax1.set_title("Smart Router Probability Over Time")
    ax1.set_xlabel("Iteration")
    ax1.set_ylabel("Probability")
    ax1.legend()

    # Subplot 2: Chosen router
    ax2 = plt.subplot(3, 1, 2)
    x2 = range(len(choiceLog))
    y2 = [1 if c == "Router1" else 2 for c in choiceLog]
    ax2.plot(x2, y2, 'o-')
    ax2.set_yticks([1, 2])
    ax2.set_yticklabels(["Router1", "Router2"])
    ax2.set_title("Which Router Was Chosen")
    ax2.set_ylabel("Chosen Router")
    ax2.set_xlabel("Iteration #")

    # Subplot 3: Router delays
    ax3 = plt.subplot(3, 1, 3)
    ax3.plot(delayLogR1, '.', color='blue', label='Router1 Delay')
    ax3.plot(delayLogR2, '.', color='orange', label='Router2 Delay')
    ax3.set_title("Router Delays Each Iteration (Base + Overhead)")
    ax3.set_ylabel("Delay")
    ax3.set_xlabel("Iteration #")
    ax3.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
