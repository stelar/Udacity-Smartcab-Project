import random
import math
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import itertools
import math
import random


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

    def __init__(self, env, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)  # Set the agent in the evironment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning  # Whether the agent is expected to learn
        self.Q = dict()  # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon  # Random exploration factor
        self.alpha = alpha  # Learning factor

        # Set any additional class parameters as needed
        self.t = 0
        self.state_def = [
            ['left', 'right', 'forward'],
            ['red', 'green'],
            ['left', 'right', 'forward', None],
            ['left', 'right', 'forward', None]
        ]

        self.template_q = dict((k, 0.0) for k in self.valid_actions)

        for state_tuple in itertools.product(*self.state_def):
            self.Q[state_tuple] = self.template_q.copy()

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """


        self.planner.route_to(destination)

        if testing:
            self.epsilon = 0
            self.alpha = 0
        else:

            self.epsilon = math.exp(-self.alpha * self.t)
            self.t += 1

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the
            environment. The next waypoint, the intersection inputs, and the deadline
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint()  # The next waypoint
        inputs = self.env.sense(self)  # Visual input - intersection light and traffic
        deadline = self.env.get_deadline(self)  # Remaining deadline

        # Set 'state' as a tuple of relevant data for the agent.  Ensure it is the same order as
        # in the class initializer
        state = (waypoint, inputs['light'], inputs['left'], inputs['oncoming'])

        return state

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        # Calculate the maximum Q-value of all actions for a given state

        maxQ = max(self.Q[state].values())
        maxQ_actions = []
        for action, Q in self.Q[state].items():
            if Q == maxQ:
                maxQ_actions.append(action)

        return maxQ, maxQ_actions

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        # Note: This is already performed in class constructor, but replicated here too
        if self.learning:
            if not state in self.Q:
                self.Q[state] = self.template_q.copy()
            return

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()
        action = None

        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        # Otherwise, choose an action with the highest Q-value for the current state

        if not self.learning or random.random() <= self.epsilon:
            action = random.choice(self.valid_actions)
        else:
            maxQ, maxQ_actions = self.get_maxQ(state)
            action = random.choice(maxQ_actions)

        return action

    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards
            when conducting learning. """

        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            pastcount = self.Q[state][action]
            self.Q[state][action] = reward * self.alpha +pastcount * (1 - self.alpha)

        return

    def update(self):
        """ The update function is called when a time step is completed in the
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()  # Get current state
        self.createQ(state)  # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action)  # Receive a reward
        self.learn(state, action, reward)  # Q-learn

        return


def run():
    """ Driving function for running the simulation.
        Press ESC to close the simulation, or [SPACE] to pause the simulation. """

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment()

    ##############
    # Create the driving agent
    # Flags:
    #   learning   - set to True to force the driving agent to use Q-learning
    #    * epsilon - continuous value for the exploration factor, default is 1
    #    * alpha   - continuous value for the learning rate, default is 0.5
    agent = env.create_agent(LearningAgent, learning=True, alpha=0.003, epsilon=1)

    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=True)

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, update_delay=0.00, log_metrics=True, optimized=True, display=False)

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05
    #   n_test     - discrete number of testing trials to perform, default is 0
    sim.run(n_test=50, tolerance=0.01)


if __name__ == '__main__':
    run()