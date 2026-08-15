import os
import random

import matplotlib.pyplot as plt
import numpy as np
import traci


SUMO_BINARY = os.getenv("SUMO_BINARY", "sumo")
CONFIG_FILE = os.getenv("SUMO_CONFIG", "osm.sumocfg")


class TrafficAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.q_table = {}
        self.epsilon = 0.1
        self.alpha = 0.1
        self.gamma = 0.9

    def get_qs(self, state):
        return self.q_table.get(
            tuple(state),
            np.zeros(self.action_size)
        )

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        qs = self.get_qs(state)
        return int(np.argmax(qs))

    def update(self, state, action, reward, next_state):
        qs = self.get_qs(state)
        next_qs = self.get_qs(next_state)

        best_next_action = np.argmax(next_qs)

        new_q = qs[action] + self.alpha * (
            reward
            + self.gamma * next_qs[best_next_action]
            - qs[action]
        )

        qs[action] = new_q
        self.q_table[tuple(state)] = qs


def get_state(tls_id):
    lanes = traci.trafficlight.getControlledLanes(tls_id)

    state = []

    for lane in lanes:
        queue = traci.lane.getLastStepHaltingNumber(lane)
        state.append(queue)

    return np.array(state)


def get_phase_count(tls_id):
    try:
        logic = traci.trafficlight.getCompleteRedYellowGreenDefinition(
            tls_id
        )[0]

        return len(logic.phases)

    except Exception:
        return 0


def get_valid_traffic_lights():
    valid_tls_ids = []

    for tls_id in traci.trafficlight.getIDList():
        if get_phase_count(tls_id) > 0:
            valid_tls_ids.append(tls_id)

    return valid_tls_ids


def set_action(tls_id, action):
    num_phases = get_phase_count(tls_id)

    if num_phases == 0:
        return

    if action >= num_phases:
        action = 0

    traci.trafficlight.setPhase(tls_id, action)


def get_reward(tls_id):
    lanes = traci.trafficlight.getControlledLanes(tls_id)

    total_waiting = 0

    for lane in lanes:
        total_waiting += traci.lane.getWaitingTime(lane)

    return -total_waiting


def train_agents(episodes=10, steps=500):
    rewards_per_episode = []

    for episode in range(episodes):
        try:
            traci.start([
                SUMO_BINARY,
                "-c",
                CONFIG_FILE
            ])

            tls_ids = get_valid_traffic_lights()

            agents = {}

            for tls_id in tls_ids:
                state = get_state(tls_id)
                action_size = get_phase_count(tls_id)

                agents[tls_id] = TrafficAgent(
                    state_size=len(state),
                    action_size=action_size
                )

            states = {
                tls_id: get_state(tls_id)
                for tls_id in tls_ids
            }

            total_reward = 0

            for _ in range(steps):

                actions = {}

                for tls_id, agent in agents.items():
                    action = agent.choose_action(
                        states[tls_id]
                    )

                    actions[tls_id] = action

                for tls_id, action in actions.items():
                    set_action(tls_id, action)

                traci.simulationStep()

                for tls_id, agent in agents.items():

                    reward = get_reward(tls_id)

                    next_state = get_state(tls_id)

                    agent.update(
                        states[tls_id],
                        actions[tls_id],
                        reward,
                        next_state
                    )

                    states[tls_id] = next_state

                    total_reward += reward

            traci.close()

            print(
                f"Episode {episode + 1}: "
                f"Total Reward = {total_reward}"
            )

            rewards_per_episode.append(total_reward)

        except Exception as error:

            print(
                f"Error during episode "
                f"{episode + 1}: {error}"
            )

            try:
                traci.close()
            except Exception:
                pass

            break

    return rewards_per_episode


def baseline_simulation(steps=500):
    try:
        traci.start([
            SUMO_BINARY,
            "-c",
            CONFIG_FILE
        ])

        total_waiting = 0

        tls_ids = get_valid_traffic_lights()

        for _ in range(steps):

            traci.simulationStep()

            for tls_id in tls_ids:

                lanes = traci.trafficlight.getControlledLanes(
                    tls_id
                )

                for lane in lanes:
                    total_waiting += traci.lane.getWaitingTime(
                        lane
                    )

        traci.close()

        return -total_waiting

    except Exception as error:

        print(
            f"Error during baseline simulation: {error}"
        )

        try:
            traci.close()
        except Exception:
            pass

        return None


def plot_results(rl_results, baseline_result):
    if not rl_results:
        print("No RL results to plot.")
        return

    episodes = range(1, len(rl_results) + 1)

    plt.plot(
        episodes,
        rl_results,
        label="RL Agents Reward"
    )

    if baseline_result is not None:
        plt.axhline(
            y=baseline_result,
            linestyle="--",
            label="Baseline"
        )

    plt.xlabel("Episode")
    plt.ylabel("Total Reward (negative waiting time)")
    plt.title(
        "Multi-Agent Traffic Signal Optimization: RL vs Fixed"
    )
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    episodes = 10
    steps = 500

    print("Running baseline simulation...")

    baseline_result = baseline_simulation(steps)

    print("Training RL agents...")

    rl_results = train_agents(
        episodes,
        steps
    )

    print("\n=== COMPARISON ===")

    print(
        f"Baseline total reward: "
        f"{baseline_result}"
    )

    if rl_results:
        print(
            f"RL average reward: "
            f"{np.mean(rl_results)}"
        )

        plot_results(
            rl_results,
            baseline_result
        )
    else:
        print("No RL results to plot.")


if __name__ == "__main__":
    main()
