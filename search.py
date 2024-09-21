import numpy as np
import queue
from game import BoardState, GameSimulator, Rules

class Problem:
    """
    This is an interface which GameStateProblem implements.
    You will be using GameStateProblem in your code. Please see
    GameStateProblem for details on the format of the inputs and
    outputs.
    """

    def __init__(self, initial_state, goal_state_set: set):
        self.initial_state = initial_state
        self.goal_state_set = goal_state_set

    def get_actions(self, state):
        """
        Returns a set of valid actions that can be taken from this state
        """
        pass

    def execute(self, state, action):
        """
        Transitions from the state to the next state that results from taking the action
        """
        pass

    def is_goal(self, state):
        """
        Checks if the state is a goal state in the set of goal states
        """
        return state in self.goal_state_set

class GameStateProblem(Problem):

    def __init__(self, initial_board_state, goal_board_state, player_idx):
        """
        player_idx is 0 or 1, depending on which player will be first to move from this initial state.

        Inputs for this constructor:
            - initial_board_state: an instance of BoardState
            - goal_board_state: an instance of BoardState
            - player_idx: an element from {0, 1}

        How Problem.initial_state and Problem.goal_state_set are represented:
            - initial_state: ((game board state tuple), player_idx ) <--- indicates state of board and who's turn it is to move
              ---specifically it is of the form: tuple( ( tuple(initial_board_state.state), player_idx ) )

            - goal_state_set: set([tuple((tuple(goal_board_state.state), 0)), tuple((tuple(goal_board_state.state), 1))])
              ---in otherwords, the goal_state_set allows the goal_board_state.state to be reached on either player 0 or player 1's
              turn.
        """
        super().__init__(tuple((tuple(initial_board_state.state), player_idx)), set([tuple((tuple(goal_board_state.state), 0)), tuple((tuple(goal_board_state.state), 1))]))
        self.sim = GameSimulator(None)
        self.search_alg_fnc = None
        self.set_search_alg()

    def set_search_alg(self, alg=""):
        """
        If you decide to implement several search algorithms, and you wish to switch between them,
        pass a string as a parameter to alg, and then set:
            self.search_alg_fnc = self.your_method
        to indicate which algorithm you'd like to run.

        TODO: You need to set self.search_alg_fnc here
        """
        self.search_alg_fnc = self.a_star_algorithm

    def get_actions(self, state: tuple):
        """
        From the given state, provide the set possible actions that can be taken from the state

        Inputs: 
            state: (encoded_state, player_idx), where encoded_state is a tuple of 12 integers,
                and player_idx is the player that is moving this turn

        Outputs:
            returns a set of actions
        """
        s, p = state
        np_state = np.array(s)
        self.sim.game_state.state = np_state
        self.sim.game_state.decode_state = self.sim.game_state.make_state()

        return self.sim.generate_valid_actions(p)

    def execute(self, state: tuple, action: tuple):
        """
        From the given state, executes the given action

        The action is given with respect to the current player

        Inputs: 
            state: is a tuple (encoded_state, player_idx), where encoded_state is a tuple of 12 integers,
                and player_idx is the player that is moving this turn
            action: (relative_idx, position), where relative_idx is an index into the encoded_state
                with respect to the player_idx, and position is the encoded position where the indexed piece should move to.
        Outputs:
            the next state tuple that results from taking action in state
        """
        s, p = state
        k, v = action
        offset_idx = p * 6
        return tuple((tuple( s[i] if i != offset_idx + k else v for i in range(len(s))), (p + 1) % 2))

    ## TODO: Implement your search algorithm(s) here as methods of the GameStateProblem.
    ##       You are free to specify parameters that your method may require.
    ##       However, you must ensure that your method returns a list of (state, action) pairs, where
    ##       the first state and action in the list correspond to the initial state and action taken from
    ##       the initial state, and the last (s,a) pair has s as a goal state, and a=None, and the intermediate
    ##       (s,a) pairs correspond to the sequence of states and actions taken from the initial to goal state.
    ##
    ## NOTE: Here is an example of the format:
    ##       [(s1, a1),(s2, a2), (s3, a3), ..., (sN, aN)] where
    ##          sN is an element of self.goal_state_set
    ##          aN is None
    ##          All sK for K=1...N are in the form (encoded_state, player_idx), where encoded_state is a tuple of 12 integers,
    ##              effectively encoded_state is the result of tuple(BoardState.state)
    ##          All aK for K=1...N are in the form (int, int)
    ##
    ## NOTE: The format of state is a tuple: (encoded_state, player_idx), where encoded_state is a tuple of 12 integers
    ##       (mirroring the contents of BoardState.state), and player_idx is 0 or 1, indicating the player that is
    ##       moving in this state.
    ##       The format of action is a tuple: (relative_idx, position), where relative_idx the relative index into encoded_state
    ##       with respect to player_idx, and position is the encoded position where the piece should move to with this action.
    ## NOTE: self.get_actions will obtain the current actions available in current game state.
    ## NOTE: self.execute acts like the transition function.
    ## NOTE: Remember to set self.search_alg_fnc in set_search_alg above.
    ## 
    """ Here is an example:
    
    def my_snazzy_search_algorithm(self):
        ## Some kind of search algorithm
        ## ...
        return solution ## Solution is an ordered list of (s,a)
    """

    def breadth_first_algorithm(self):
        q = queue.Queue()

        if self.is_goal(self.initial_state):
            return [(self.initial_state, None)]

        for action in self.get_actions(self.initial_state):
            new_state = self.execute(self.initial_state, action)
            q.put((new_state, action, [(self.initial_state, action)]))

        while not q.empty():
            state, action, path = q.get()

            if self.is_goal(state):
                path.append((state, None))
                return path
            
            for action in self.get_actions(state):
                new_state = self.execute(state, action)
                new_path = list(path)
                new_path.append((state, action))
                q.put((new_state, action, new_path))

    def create_hash(self, state: tuple):
        board = ','.join(str(pos) for pos in state[0])
        return board + ':' + str(state[1])

    def heuristic(self, state: tuple):
        h = np.inf

        for goal in self.goal_state_set:
            count = 0
            for i in range(len(goal[0])):
                if state[0][i] != goal[0][i]:
                    count += 1

            if state[1] != goal[1]:
                count += 1

            if count < h:
                h = count

        return h

        
    def reconstruct_path(self, came_from, state):
        total_path = []
        total_path.append((state, None))
        state_hash = self.create_hash(state)
        while state_hash in came_from:
            action, state = came_from[state_hash]
            state_hash = self.create_hash(state)
            total_path.append((state, action))
        return list(reversed(total_path))

    def a_star_algorithm(self):
        min_queue = queue.PriorityQueue()
        queue_set = set()
        came_from = {}
        g_score = {}

        init_hash = self.create_hash(self.initial_state)
        g_score[init_hash] = 0
        init_heuristic = self.heuristic(self.initial_state)
        min_queue.put((init_heuristic, self.initial_state))
        queue_set.add(init_hash)

        while not min_queue.empty():
            _, state = min_queue.get()
            state_hash = self.create_hash(state)
            queue_set.remove(state_hash)

            if self.is_goal(state):
                return self.reconstruct_path(came_from, state)
            
            for action in self.get_actions(state):
                new_state = self.execute(state, action)
                new_state_hash = self.create_hash(new_state)

                tentative_g_score = g_score[state_hash] + 1
                if new_state_hash not in g_score or tentative_g_score < g_score[new_state_hash]:
                    came_from[new_state_hash] = (action, state)
                    g_score[new_state_hash] = tentative_g_score
                    new_score = tentative_g_score + self.heuristic(new_state)
                    if new_state_hash not in queue_set:
                        min_queue.put((new_score, new_state))
                        queue_set.add(new_state_hash)


        return "ERROR"
