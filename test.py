import pygame
import sys
from copy import deepcopy
import torch
from torch import nn

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("6x6 Othello")

# Initialize the game board
board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
board[3][4] = board[4][3] = 2  # Black
board[3][3] = board[4][4] = 1  # White
        

# Current player (1 for White, 2 for Black)
current_player = 2

def draw_board():
    screen.fill(GREEN)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(screen, BLACK, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            if board[y][x] == 1:
                pygame.draw.circle(screen, WHITE, (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2), CELL_SIZE//2 - 5)
            elif board[y][x] == 2:
                pygame.draw.circle(screen, BLACK, (x*CELL_SIZE + CELL_SIZE//2, y*CELL_SIZE + CELL_SIZE//2), CELL_SIZE//2 - 5)

def is_valid_move(x, y,board):
    if board[y][x] != 0:
        return False
    
    directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
    for dx, dy in directions:
        if check_direction(x, y, dx, dy,board):
            return True
    return False

def check_direction(x, y, dx, dy,board):
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

def make_move(x, y,board):
    board[y][x] = current_player
    directions = [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]
    for dx, dy in directions:
        if check_direction(x, y, dx, dy,board):
            flip_direction(x, y, dx, dy,board)

def flip_direction(x, y, dx, dy,board):
    x, y = x + dx, y + dy
    while board[y][x] != current_player:
        board[y][x] = current_player
        x, y = x + dx, y + dy

def switch_player():
    global current_player
    current_player = 1 if current_player == 2 else 2

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(13, 32),
            nn.LeakyReLU(),
            nn.Linear(32,32),
            nn.LeakyReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits
 
device = "cpu"
model = NeuralNetwork().to(device)
learning_rate = 1e-5 * 2
loss_fn = nn.MSELoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)

def get_moves():
    valid_moves = []
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if is_valid_move(x,y): valid_moves.append((x,y))
    
    points = []

    for x,y in valid_moves:
        points.append(StaticEval(x,y))

def StaticEval(x,y):
    simboard = deepcopy(board)
    make_move(x,y,board)

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
            if is_valid_move(grid_x, grid_y,board):
                make_move(grid_x, grid_y,board)
                switch_player()
    
    draw_board()
    pygame.display.flip()
