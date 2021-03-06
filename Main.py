from collections import namedtuple
import sys

### Variables ###
infinity = float('inf')
GameState = namedtuple('GameState', 'to_move, utility, board, moves')

def main_loop():
    print("|**********************************************|")
    print("|**************  Welcome!  ********************|")
    print("|**********************************************|\n")
    
    print("1. New Game")
    print("0. Quit")
    
    global colour_symbol, board_size, level
    
    choice = input("Enter number: ")
    if choice == '1':
        colour_symbol, board_size, level = input("\nColour of Player (Black or White), \nSize of Board (number must be positive and even), \nLevel (number must be positive)\nEnter separated by space: ").split()
        check_parameters(colour_symbol, int(board_size), int(level))
        run_game(colour_symbol, int(board_size))
        game_result()
    elif choice == '0':
        print("\nQuit!\n")
        sys.exit(0)
    else:
        print("\nError enter correct number please.\n")

def check_parameters(colour, size, level):
    global colour_symbol 
    
    if colour == 'Black':
        colour_symbol = 'B'
        True
    elif colour == 'White':
        colour_symbol = 'W'
        True
    else:
        return "You entered wrong Colour! Try again please.", main_loop()
    
    if size > 0:
        True
    else: 
        return "You entered wrong number Size of board! Try again please.", main_loop()
    
    if level > 0:
        True
    else:
        return "You entered wrong number of Level! Try again please.", main_loop()
    
    return True

def run_game(colour, size):
    game = Reversi(colour, size)
    game.play_game(human_player, alphabeta_player)

def game_result():
    if ScoreB > ScoreW:
        print("\nBlack Player Win !!!\n")
    elif ScoreW > ScoreB:
        print("\nWhite Player Win !!!\n")
    elif ScoreB == ScoreW:
        print("\nDraw !!!\n")
        
    choice = input("Do you want play again? (Yes/No)\n")
    if choice == "Yes":
        main_loop()
    elif choice == "No":
        sys.exit(0)
    else:
        print("Error enter correct answer please")
        game_result()
 
def alphabeta_cutoff_search(state, game, d, cutoff_test = None, eval_fn = None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    # Functions used by alphabeta
    def max_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = -infinity
        for a in game.actions(state):
            v = max(v, min_value(game.result(state, a),
                                 alpha, beta, depth + 1))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth):
        if cutoff_test(state, depth):
            return eval_fn(state)
        v = infinity
        for a in game.actions(state):
            v = min(v, max_value(game.result(state, a),
                                 alpha, beta, depth + 1))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alphabeta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state
    cutoff_test = (cutoff_test or
                   (lambda state, depth: depth > d or
                                         game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -infinity
    beta = infinity
    best_action = None
    for a in game.actions(state):
        v = min_value(game.result(state, a), best_score, beta, 1)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action

def human_player(game, state):
    """Make a move by querying standard input."""
    if colour_symbol == 'W':
        print("\nHuman - White Player")
    else:
        print("\nHuman - Black Player")

    print("Current state:")
    game.display(state)
    print("Available moves: {}".format(game.actions(state)))
    move_string = input("Human move: ")
    
    if move_string == "quit":
        sys.exit(0)
    elif move_string == "showstate":
        game.display(state)
    else:
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    
    return move

def alphabeta_player(game, state):
    if colour_symbol == 'W':
        print("\nAI - Black Player")
    else:
        print("\nAI - White Player")
    
    print("Current state:")
    game.display(state)
    print("Available moves: {}".format(game.actions(state)))
    move = alphabeta_cutoff_search(state, game, d = int(level))
    print("AI move: ", move)
    try:
        move = eval(str(move))
    except NameError:
        move = move
    return move

class GamePattern:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError
    
    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        raise NotImplementedError

class Reversi(GamePattern):
    """Reversi game."""
    global  ScoreB, ScoreW
    
    def __init__(self, colour, size):
        self.height = size
        self.width = size
        init_white_pos = [(size/2, size/2), ((size/2)+1, (size/2)+1)]
        init_black_pos = [(size/2, (size/2)+1), ((size/2)+1, size/2)]
        init_white_board = dict.fromkeys(init_white_pos, 'W')
        init_black_board = dict.fromkeys(init_black_pos, 'B')
        board = {**init_white_board, **init_black_board}
        moves = self.get_valid_moves(board, colour)
        self.initial = GameState(
            to_move = colour, utility = 0, board = board, moves = moves)

    def capture_enemy_in_dir(self, board, move, player, delta_x_y):
        """Returns true if any enemy is captured in the specified direction."""
        enemy = 'B' if player == 'W' else 'W'
        (delta_x, delta_y) = delta_x_y
        x, y = move
        x, y = x + delta_x, y + delta_y
        enemy_list_0 = []
        while board.get((x, y)) == enemy:
            enemy_list_0.append((x, y))
            x, y = x + delta_x, y + delta_y
        if board.get((x, y)) != player:
            del enemy_list_0[:]
        x, y = move
        x, y = x - delta_x, y - delta_y
        enemy_list_1 = []
        while board.get((x, y)) == enemy:
            enemy_list_1.append((x, y))
            x, y = x - delta_x, y - delta_y
        if board.get((x, y)) != player:
            del enemy_list_1[:]
        return enemy_list_0 + enemy_list_1

    def enemy_captured_by_move(self, board, move, player):
        return self.capture_enemy_in_dir(board, move, player, (0, 1)) \
               + self.capture_enemy_in_dir(board, move, player, (1, 0)) \
               + self.capture_enemy_in_dir(board, move, player, (1, -1)) \
               + self.capture_enemy_in_dir(board, move, player, (1, 1))

    def actions(self, state):
        """Legal moves."""
        return state.moves

    def get_valid_moves(self, board, player):
        """Returns a list of valid moves for the player judging from the board."""
        return [(x, y) for x in range(1, self.width + 1)
                for y in range(1, self.height + 1)
                if (x, y) not in board.keys() and
                self.enemy_captured_by_move(board, (x, y), player)]

    def result(self, state, move):
        # Invalid move
        if move not in state.moves:
            return state
        opponent_player = 'W' if state.to_move == 'B' else 'B'
        board = state.board.copy()
        board[move] = state.to_move  # Show the move on the board
        # Flip enemy
        for enemy in self.enemy_captured_by_move(board, move, state.to_move):
            board[enemy] = state.to_move
        # Regenerate valid moves
        moves = self.get_valid_moves(board, opponent_player)
        return GameState(to_move=opponent_player,
                         utility=self.compute_utility(
                             board, move, state.to_move),
                         board=board, moves=moves)

    def utility(self, state, player):
        return state.utility if player == 'B' else -state.utility

    def terminal_test(self, state):
        return len(state.moves) == 0
    
    def display(self, state):
        board = state.board
        for y in range(0, self.height + 1):
            for x in range(0, self.width + 1):
                if x > 0 and y > 0:
                    if (x, y) in state.moves:
                        print(board.get((x, y), '*',), end=' ')
                    else:
                        print(board.get((x, y), '.',), end=' ')
                if x == 0:
                    if y > 0:
                        print(y, end=' ')
                if y == 0:
                    print(x, end=' ')
            print()
        
        global ScoreB, ScoreW
        b = 0
        w = 0
        for x in board.values():
            if x == 'B':
                b += 1
                ScoreB = b
            elif x == 'W':
                w += 1 
                ScoreW = w
        
        print("Black: {0} - White: {1}".format(b, w))

    def compute_utility(self, board, move, player):
        if len(self.get_valid_moves(board, player)) == 0:
            return +100 if player == 'B' else -100
        else:
            return 0.4 * self.coin_diff(board) + 0.3 * self.choice_diff(board) + 0.3 * self.corner_diff(board)

    @staticmethod
    def coin_diff(board):
        """Difference in the number of coins."""
        return 100 * (sum(x == 'B' for x in board.values()) - sum(x == 'W' for x in board.values())) / len(board)

    def choice_diff(self, board):
        """Difference in the number of choices available."""
        black_moves_num = len(self.get_valid_moves(board, 'B'))
        white_moves_num = len(self.get_valid_moves(board, 'W'))
        if (black_moves_num + white_moves_num) != 0:
            return 100 * (black_moves_num - white_moves_num) / (black_moves_num + white_moves_num)
        else:
            return 0

    def corner_diff(self, board):
        """Difference in the number of corners captured."""
        corner = [board.get((1, 1)), board.get((1, self.height)), board.get((self.width, 1)),
                  board.get((self.width, self.height))]
        black_corner = corner.count('B')
        white_corner = corner.count('W')
        if (black_corner + white_corner) != 0:
            return 100 * (black_corner - white_corner) / (black_corner + white_corner)
        else:
            return 0

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))

main_loop()