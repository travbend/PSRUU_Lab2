import numpy as np

class BoardState:
    """
    Represents a state in the game
    """

    def __init__(self):
        """
        Initializes a fresh game state
        """
        self.N_ROWS = 8
        self.N_COLS = 7

        self.state = np.array([1,2,3,4,5,3,50,51,52,53,54,52])
        self.decode_state = [self.decode_single_pos(d) for d in self.state]

    def update(self, idx, val):
        """
        Updates both the encoded and decoded states
        """
        self.state[idx] = val
        self.decode_state[idx] = self.decode_single_pos(self.state[idx])

    def make_state(self):
        """
        Creates a new decoded state list from the existing state array
        """
        return [self.decode_single_pos(d) for d in self.state]

    def encode_single_pos(self, cr: tuple):
        """
        Encodes a single coordinate (col, row) -> Z

        Input: a tuple (col, row)
        Output: an integer in the interval [0, 55] inclusive

        TODO: You need to implement this.
        """
        return self.N_COLS * cr[1] + cr[0]

    def decode_single_pos(self, n: int):
        """
        Decodes a single integer into a coordinate on the board: Z -> (col, row)

        Input: an integer in the interval [0, 55] inclusive
        Output: a tuple (col, row)

        TODO: You need to implement this.
        """
        return (n % self.N_COLS, n // self.N_COLS)

    def is_termination_state(self):
        """
        Checks if the current state is a termination state. Termination occurs when
        one of the player's move their ball to the opposite side of the board.

        You can assume that `self.state` contains the current state of the board, so
        check whether self.state represents a termainal board state, and return True or False.
        
        TODO: You need to implement this.
        """
        if not self.is_valid():
            return False

        p1_ball, _, p2_ball, _ = self.get_positions()

        if self.decode_single_pos(p1_ball)[1] == self.N_ROWS-1:
            return True
        
        if self.decode_single_pos(p2_ball)[1] == 0:
            return True
        
        return False
        

    def is_valid(self):
        """
        Checks if a board configuration is valid. This function checks whether the current
        value self.state represents a valid board configuration or not. This encodes and checks
        the various constrainsts that must always be satisfied in any valid board state during a game.

        If we give you a self.state array of 12 arbitrary integers, this function should indicate whether
        it represents a valid board configuration.

        Output: return True (if valid) or False (if not valid)
        
        TODO: You need to implement this.
        """
        p1_ball, p1_pos, p2_ball, p2_pos = self.get_positions()

        for pos in p1_pos:
            if pos < 0 or pos > self.encode_single_pos((self.N_COLS-1, self.N_ROWS-1)):
                return False
            
            if pos in p2_pos:
                return False
            
        for pos in p2_pos:
            if pos < 0 or pos > self.encode_single_pos((self.N_COLS-1, self.N_ROWS-1)):
                return False
            
            if pos in p1_pos:
                return False

        if p1_ball not in p1_pos or p2_ball not in p2_pos:
            return False
        
        return True
        
    def get_positions(self):
        p1_ball = self.state[len(self.state) // 2 - 1]
        p1_pos = self.state[:len(self.state) // 2 - 1]
        p2_ball = self.state[len(self.state) - 1]
        p2_pos = self.state[len(self.state) // 2: len(self.state) - 1]
        return (p1_ball, p1_pos, p2_ball, p2_pos)
    
    def single_piece_actions(self, piece_idx):
        pos = self.state[piece_idx]
        col, row = self.decode_single_pos(pos)
        result = []

        if col-2 >= 0:
            if row-1 >= 0:
                result.append(self.encode_single_pos((col-2, row-1)))
            
            if row+1 < self.N_ROWS:
                result.append(self.encode_single_pos((col-2, row+1)))
        
        if col+2 < self.N_COLS:
            if row-1 >= 0:
                result.append(self.encode_single_pos((col+2, row-1)))
            
            if row+1 < self.N_ROWS:
                result.append(self.encode_single_pos((col+2, row+1)))

        if row-2 >= 0:
            if col-1 >= 0:
                result.append(self.encode_single_pos((col-1, row-2)))
            
            if col+1 < self.N_COLS:
                result.append(self.encode_single_pos((col+1, row-2)))
        
        if row+2 < self.N_ROWS:
            if col-1 >= 0:
                result.append(self.encode_single_pos((col-1, row+2)))
            
            if col+1 < self.N_COLS:
                result.append(self.encode_single_pos((col+1, row+2)))
        
        return result
    
    def single_ball_actions(self, player_idx):
        p1_ball, p1_pos, p2_ball, p2_pos = self.get_positions()

        if player_idx == 0:
            player_pos = set(p1_pos)
            opponent_pos = set(p2_pos)
            ball_pos = p1_ball
        else:
            player_pos = set(p2_pos)
            opponent_pos = set(p1_pos)
            ball_pos = p2_ball

        result = set([ball_pos])
        self.recurse_ball_actions(result, ball_pos, player_pos, opponent_pos)
        result.remove(ball_pos)
        return result
    
    def recurse_ball_actions(self, result: set, pos: int, player_pos: set, opponent_pos: set):
        ball_col, ball_row = self.decode_single_pos(pos)

        for play_pos in player_pos:
            play_col, play_row = self.decode_single_pos(play_pos)

            if play_pos in result:
                continue

            if play_col == ball_col:
                valid = True
                for opp_pos in opponent_pos:
                    opp_col, opp_row = self.decode_single_pos(opp_pos)
                    if opp_col == play_col and (play_row < opp_row < ball_row or play_row > opp_row > ball_row):
                        valid = False
                        break

                if valid:
                    result.add(play_pos)
                    self.recurse_ball_actions(result, play_pos, player_pos, opponent_pos)
                
            if play_row == ball_row:
                valid = True
                for opp_pos in opponent_pos:
                    opp_col, opp_row = self.decode_single_pos(opp_pos)
                    if opp_row == play_row and (play_col < opp_col < ball_col or play_col > opp_col > ball_col):
                        valid = False
                        break

                if valid:
                    result.add(play_pos)
                    self.recurse_ball_actions(result, play_pos, player_pos, opponent_pos)

            if abs(play_row - ball_row) == abs(play_col - ball_col):
                valid = True
                for opp_pos in opponent_pos:
                    opp_col, opp_row = self.decode_single_pos(opp_pos)

                    if abs(opp_row - ball_row) == abs(opp_col - ball_col):
                        if (play_row < opp_row < ball_row or play_row > opp_row > ball_row) and (play_col < opp_col < ball_col or play_col > opp_col > ball_col):
                            valid = False
                            break

                if valid:
                    result.add(play_pos)
                    self.recurse_ball_actions(result, play_pos, player_pos, opponent_pos)


class Rules:

    @staticmethod
    def single_piece_actions(board_state, piece_idx):
        """
        Returns the set of possible actions for the given piece, assumed to be a valid piece located
        at piece_idx in the board_state.state.

        Inputs:
            - board_state, assumed to be a BoardState
            - piece_idx, assumed to be an index into board_state, identfying which piece we wish to
              enumerate the actions for.

        Output: an iterable (set or list or tuple) of integers which indicate the encoded positions
            that piece_idx can move to during this turn.
        
        TODO: You need to implement this.
        """
        return board_state.single_piece_actions(piece_idx)

    @staticmethod
    def single_ball_actions(board_state, player_idx):
        """
        Returns the set of possible actions for moving the specified ball, assumed to be the
        valid ball for plater_idx  in the board_state

        Inputs:
            - board_state, assumed to be a BoardState
            - player_idx, either 0 or 1, to indicate which player's ball we are enumerating over
        
        Output: an iterable (set or list or tuple) of integers which indicate the encoded positions
            that player_idx's ball can move to during this turn.
        
        TODO: You need to implement this.
        """
        return board_state.single_ball_actions(player_idx)

class GameSimulator:
    """
    Responsible for handling the game simulation
    """

    def __init__(self, players):
        self.game_state = BoardState()
        self.current_round = -1 ## The game starts on round 0; white's move on EVEN rounds; black's move on ODD rounds
        self.players = players

    def run(self):
        """
        Runs a game simulation
        """
        while not self.game_state.is_termination_state():
            ## Determine the round number, and the player who needs to move
            self.current_round += 1
            player_idx = self.current_round % 2
            ## For the player who needs to move, provide them with the current game state
            ## and then ask them to choose an action according to their policy
            action, value = self.players[player_idx].policy( self.game_state.make_state() )
            print(f"Round: {self.current_round} Player: {player_idx} State: {tuple(self.game_state.state)} Action: {action} Value: {value}")

            if not self.validate_action(action, player_idx):
                ## If an invalid action is provided, then the other player will be declared the winner
                if player_idx == 0:
                    return self.current_round, "BLACK", "White provided an invalid action"
                else:
                    return self.current_round, "WHITE", "Black probided an invalid action"

            ## Updates the game state
            self.update(action, player_idx)

        ## Player who moved last is the winner
        if player_idx == 0:
            return self.current_round, "WHITE", "No issues"
        else:
            return self.current_round, "BLACK", "No issues"

    def generate_valid_actions(self, player_idx: int):
        """
        Given a valid state, and a player's turn, generate the set of possible actions that player can take

        player_idx is either 0 or 1

        Input:
            - player_idx, which indicates the player that is moving this turn. This will help index into the
              current BoardState which is self.game_state
        Outputs:
            - a set of tuples (relative_idx, encoded position), each of which encodes an action. The set should include
              all possible actions that the player can take during this turn. relative_idx must be an
              integer on the interval [0, 5] inclusive. Given relative_idx and player_idx, the index for any
              piece in the boardstate can be obtained, so relative_idx is the index relative to current player's
              pieces. Pieces with relative index 0,1,2,3,4 are block pieces that like knights in chess, and
              relative index 5 is the player's ball piece.
            
        TODO: You need to implement this.
        """
        start = len(self.game_state.state) // 2 * player_idx
        end = len(self.game_state.state) // 2 * (player_idx+1)
        result = []
        for idx in range(start, end):
            if idx == end-1:
                for pos in Rules.single_ball_actions(self.game_state, player_idx):
                    result.append((idx-start, pos))
            else:
                for pos in Rules.single_piece_actions(self.game_state, idx):
                    result.append((idx-start, pos))

        return result

    def validate_action(self, action: tuple, player_idx: int):
        """
        Checks whether or not the specified action can be taken from this state by the specified player

        Inputs:
            - action is a tuple (relative_idx, encoded position)
            - player_idx is an integer 0 or 1 representing the player that is moving this turn
            - self.game_state represents the current BoardState

        Output:
            - if the action is valid, return True
            - if the action is not valid, raise ValueError
        
        TODO: You need to implement this.
        """
        idx, pos = action
        start = len(self.game_state.state) / 2 * player_idx
        end = len(self.game_state.state) / 2 * (player_idx+1)

        if idx < start or idx >= end:
            raise ValueError("Invalid relative index")
        
        if idx == (end-1) and pos not in Rules.single_ball_actions(self.game_state, player_idx):
            raise ValueError("Invalid ball action")
        
        if idx < (end-1) and pos not in Rules.single_piece_actions(self.game_state, idx):
            raise ValueError("Invalid piece action")
        
        return True
    
    def update(self, action: tuple, player_idx: int):
        """
        Uses a validated action and updates the game board state
        """
        offset_idx = player_idx * 6 ## Either 0 or 6
        idx, pos = action
        self.game_state.update(offset_idx + idx, pos)
