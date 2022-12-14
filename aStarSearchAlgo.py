import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])
            
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])
            
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])
            
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(point1, point2):      # estimate distance from current to end node
    x1, y1 = point1     # split the point variables into x and y
    x2, y2 = point2
    
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw): # traverse from end to start and draw path
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end): # draw is passed as a function with lambda
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start)) # put start node in open_set
    came_from = {} # dictionary that keeps track of nodes in order to find efficent path
    g_score = {spot: float("inf") for row in grid for spot in row} # current shortest distance from start to current node
    g_score[start] = 0 # set g score at start to 0
    f_score = {spot: float("inf") for row in grid for spot in row} # prediction from current node to end node
    f_score[start] = h(start.get_pos(), end.get_pos()) 

    open_set_hash = {start}
    
    while not open_set.empty():     # quit game if user quits
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # use priortity queue to get the smallest element
        open_set_hash.remove(current) # remove this spot/element from current 

        if current == end: # finished
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors: # compare current node to it's neighbors
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]: # if temp g score is less than current g score then change to temp
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()


    return False   
                
def make_grid(rows, width):     # make the grid and assign nodes to grid
    grid = []
    gap = width // rows  # width of entire grid divided by how many rows we have
    for i in range(rows):
        grid.append([])  # append empty list to grid
        for j in range(rows):
            spot = Spot(i, j, gap, rows)  # pass the Node class to node
            grid[i].append(spot)  # append node with information to the grid at row i

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):     # draw horizontal lines
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # exit the pathfinder
                run = False

            if pygame.mouse.get_pressed()[0]:  # press left mouse button
                pos = pygame.mouse.get_pos()  # the x and y coordinate of the mouse
                row, col = get_clicked_pos(pos, ROWS, width)  # assign mouse position to row(x) and col(y)
                spot = grid[row][col]  # row and col assigned to the node
                if not start and spot != end:  # first left click with mouse is the start node
                    start = spot
                    start.make_start()

                elif not end and spot != start:  # second left click with mouse is the end node
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:     # third click makes barrier
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # press right mouse button
                pos = pygame.mouse.get_pos()  
                row, col = get_clicked_pos(pos, ROWS, width)   
                spot = grid[row][col]
                spot.reset() # using right mouse, spots can be reset 
                if spot == start:
                    start = None

                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()

main(WIN, WIDTH)
