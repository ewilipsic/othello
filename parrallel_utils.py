GRID_SIZE = 8

def is_valid_move(x, y,board,current_player):
    if board[y][x] != 0:
        return False
    directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
    for dx, dy in directions:
        if check_direction(x, y, dx, dy,board,current_player):
            return True
    return False

def check_direction(x, y, dx, dy,board,current_player):
    opponent = 1 if current_player == 2 else 2
    x, y = x + dx, y + dy
    if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE) or board[y][x] != opponent:
        return False
    while 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
        if board[y][x] == 0:
            return False
        if board[y][x] == current_player:
            return True
        x, y = x + dx, y + dy
    return False

def make_move(x, y,board,current_player):
    board[y][x] = current_player
    directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
    for dx, dy in directions:
        if check_direction(x, y, dx, dy,board,current_player):
            flip_direction(x, y, dx, dy,board,current_player)

def flip_direction(x, y, dx, dy,board,current_player):
    x, y = x + dx, y + dy
    while board[y][x] != current_player:
        board[y][x] = current_player
        x, y = x + dx, y + dy

def decide_winner(board,current_player):
    black = 0
    white = 0
    for x in board:
        for y in x:
            black += (y == 2)
            white += (y == 1)
    if(black + white != 64) and current_player == 2:
        return 0
    if(black + white != 64) and current_player == 1:
        return 1
    return int(black >= 32)

import random 
import math
from copy import deepcopy
def get_move_random(board,current_player):
    valid_moves = []
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if is_valid_move(x,y,board,current_player): valid_moves.append((x,y))
    if(len(valid_moves) == 0): return None    
    return valid_moves[random.randint(0,len(valid_moves)-1)]

class ParallelNode():
    def __init__(self,x,y,player_who_decides_next):
        self.x = x
        self.y = y
        self.children = []
        self.visits = 0
        self.wins = 0
        self.player = player_who_decides_next
    
    def generate_children(self,board):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if is_valid_move(x,y,board,self.player): 
                    if self.player == 1: self.children.append(ParallelNode(x,y,2))
                    if self.player == 2: self.children.append(ParallelNode(x,y,1))
        if len(self.children) == 0:
            self.children = None

    def select(self,C):
        if(self.player == 2):
            ret = max(self.children,key = lambda child: child.wins/(child.visits+0.001) +  C*( 
            (2.0*math.log(self.visits))/(child.visits+0.001))**0.5)
            return ret
        else:
            # USING LOSES FOR MINIMIZING PLAYER
            ret = max(self.children,key = lambda child: ((child.visits - child.wins)/(child.visits+0.0001) +  C*( 
            (2.0*math.log(self.visits))/(child.visits+0.0001))**0.5))
            return ret

    def rollout(self,depth,C,board): # 1 == simulate from children
        self.visits += 1

        if depth == 0:
            ret = self.simulate(board)
            self.wins += ret
            return ret
        
        
        if self.children == None: 
            ret = decide_winner(board,self.player)
            self.wins += ret
            return ret
        if len(self.children) == 0: self.generate_children(board)
        if self.children == None: 
            ret = decide_winner(board,self.player)
            self.wins += ret
            return ret
        
        
        child = self.select(C)
        make_move(child.x,child.y,board,self.player)
        ret = child.rollout(depth-1,C,board)
        self.wins += ret
        return ret
    
    def simulate(self,board):
        current_player = self.player
        while True:
            move = get_move_random(board,current_player)
            if(move == None): break
            make_move(move[0],move[1],board,current_player)
            if current_player == 2: current_player = 1
            else: current_player = 2
        return decide_winner(board,current_player)
    
def run_mcts_instance(board,current_player,selectionDepth,explorationFactor,num_rollouts):

    try:
        root  = ParallelNode(-1,-1,current_player)
        board_copy = deepcopy(board)
        for i in range(num_rollouts):
            sim_board = deepcopy(board_copy)
            root.rollout(selectionDepth,explorationFactor,sim_board)
            del(sim_board)
        return root
    except Exception as e:
        print(f"Error in worker process: {e}")
        # Return a default value or re-raise
        raise