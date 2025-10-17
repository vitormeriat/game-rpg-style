import pygame
import random
import time
import math
import os
import json
from datetime import datetime
from queue import PriorityQueue

# Initialize pygame
pygame.init()

# Constants
WIDTH = 1000
GRID_WIDTH = 800
ROWS = 50
CELL_SIZE = GRID_WIDTH // ROWS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
RETRO_GREEN = (0, 255, 100)
RETRO_BLUE = (0, 100, 255)

# Create directories if they don't exist
os.makedirs("mazes", exist_ok=True)
os.makedirs("metadata", exist_ok=True)

# Window
WIN = pygame.display.set_mode((WIDTH, GRID_WIDTH))
pygame.display.set_caption("A* Pathfinding - Maze Solver")

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.x = row * CELL_SIZE
        self.y = col * CELL_SIZE
        self.color = WHITE
        self.neighbors = []
        self.parent = None
        self.g = float('inf')
        self.h = 0
        self.f = float('inf')
    
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
        return self.color == PURPLE
    
    def reset(self):
        self.color = WHITE
    
    def make_closed(self):
        self.color = RED
    
    def make_open(self):
        self.color = GREEN
    
    def make_barrier(self):
        self.color = BLACK
    
    def make_start(self):
        self.color = ORANGE
    
    def make_end(self):
        self.color = PURPLE
    
    def make_path(self):
        self.color = BLUE
    
    def draw(self, win, x_offset=0):
        pygame.draw.rect(win, self.color, (self.x + x_offset, self.y, CELL_SIZE, CELL_SIZE))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        
        # Down
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        
        # Right
        if self.col < ROWS - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
    
    def __lt__(self, other):
        return self.f < other.f

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont('retro', 30)
    
    def draw(self, win):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(win, color, self.rect, border_radius=5)
        pygame.draw.rect(win, BLACK, self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        win.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

def h(p1, p2):
    """Heuristic - Manhattan distance"""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def generate_random_grid():
    """Generates a random grid with walls"""
    grid = [[Node(i, j) for j in range(ROWS)] for i in range(ROWS)]
    
    for i in range(ROWS):
        for j in range(ROWS):
            if random.random() < 0.3:  # 30% chance to be a wall
                grid[i][j].make_barrier()
    
    return grid

def is_valid_grid(grid):
    """Checks if the grid is valid (path exists between start and end)"""
    # Find valid start and end points
    start = None
    end = None
    
    # Look for non-wall cells in corners
    corners = [(0, 0), (0, ROWS-1), (ROWS-1, 0), (ROWS-1, ROWS-1)]
    random.shuffle(corners)
    
    for i, j in corners:
        if not grid[i][j].is_barrier():
            if start is None:
                start = grid[i][j]
            elif end is None:
                end = grid[i][j]
                break
    
    if start is None or end is None:
        return False, None, None
    
    # Check path existence using BFS
    visited = [[False for _ in range(ROWS)] for _ in range(ROWS)]
    queue = []
    queue.append(start.get_pos())
    visited[start.row][start.col] = True
    
    while queue:
        row, col = queue.pop(0)
        
        if (row, col) == end.get_pos():
            return True, start, end
        
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r = row + dr
            c = col + dc
            
            if 0 <= r < ROWS and 0 <= c < ROWS:
                if not visited[r][c] and not grid[r][c].is_barrier():
                    visited[r][c] = True
                    queue.append((r, c))
    
    return False, None, None

def save_maze(grid, maze_id):
    """Saves the maze to a file"""
    maze_data = []
    for row in grid:
        maze_row = []
        for node in row:
            if node.is_barrier():
                maze_row.append(1)
            else:
                maze_row.append(0)
        maze_data.append(maze_row)
    
    with open(f"mazes/maze_{maze_id}.json", "w") as f:
        json.dump(maze_data, f)

def save_metadata(maze_id, stats):
    """Saves the performance metadata"""
    with open(f"metadata/meta_{maze_id}.json", "w") as f:
        json.dump(stats, f)

def load_recent_simulations():
    """Loads the 5 most recent simulations"""
    try:
        meta_files = sorted(os.listdir("metadata"), reverse=True)[:5]
        simulations = []
        
        for file in meta_files:
            with open(f"metadata/{file}", "r") as f:
                data = json.load(f)
                simulations.append(data)
        
        return simulations
    except:
        return []

def reconstruct_path(current, draw):
    """Reconstructs the path from end to start"""
    path_length = 0
    while current.parent:
        path_length += 1
        current = current.parent
        current.make_path()
        draw()
    return path_length

def a_star_algorithm(draw, grid, start, end):
    """A* algorithm implementation"""
    start_time = time.time()
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    start.g = 0
    start.h = h(start.get_pos(), end.get_pos())
    start.f = start.g + start.h
    
    open_set_hash = {start}
    nodes_visited = 0
    
    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
        
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end:
            path_length = reconstruct_path(end, draw)
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # Calculate complexity metrics
            total_nodes = ROWS * ROWS
            visited_percentage = (nodes_visited / total_nodes) * 100
            complexity = f"O(b^d) | Visited: {visited_percentage:.1f}%"
            
            stats = {
                "time": elapsed_time,
                "complexity": complexity,
                "nodes_visited": nodes_visited,
                "path_length": path_length,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return stats
        
        for neighbor in current.neighbors:
            temp_g = current.g + 1
            
            if temp_g < neighbor.g:
                neighbor.parent = current
                neighbor.g = temp_g
                neighbor.h = h(neighbor.get_pos(), end.get_pos())
                neighbor.f = neighbor.g + neighbor.h
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((neighbor.f, count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
                    nodes_visited += 1
        
        draw()
        
        if current != start:
            current.make_closed()
    
    return None

def draw_grid(win, rows, width, x_offset=0):
    """Draws grid lines"""
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRAY, (x_offset, i * gap), (x_offset + width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GRAY, (x_offset + j * gap, 0), (x_offset + j * gap, width))

def draw_main_screen(win, grid, buttons, recent_simulations):
    """Draws the main screen with buttons and preview"""
    win.fill(DARK_GRAY)
    
    # Draw title
    title_font = pygame.font.SysFont('retro', 60)
    title_text = title_font.render("MAZE SOLVER", True, RETRO_GREEN)
    win.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 30))
    
    # Draw buttons
    for button in buttons:
        button.draw(win)
    
    # Draw preview
    preview_font = pygame.font.SysFont('retro', 30)
    preview_text = preview_font.render("MAZE PREVIEW", True, WHITE)
    win.blit(preview_text, (GRID_WIDTH + 30, 150))
    
    # Draw small preview of the maze
    if grid:
        preview_size = 200
        preview_cell_size = preview_size // ROWS
        preview_x = GRID_WIDTH + (WIDTH - GRID_WIDTH - preview_size) // 2
        
        for row in grid:
            for node in row:
                pygame.draw.rect(win, node.color, 
                                (preview_x + node.row * preview_cell_size, 
                                 200 + node.col * preview_cell_size, 
                                 preview_cell_size, preview_cell_size))
        
        # Draw preview border
        pygame.draw.rect(win, WHITE, (preview_x, 200, preview_size, preview_size), 2)
    
    # Draw recent simulations
    recent_font = pygame.font.SysFont('retro', 30)
    recent_text = recent_font.render("RECENT SIMULATIONS", True, WHITE)
    win.blit(recent_text, (GRID_WIDTH + 30, 420))
    
    if recent_simulations:
        for i, sim in enumerate(recent_simulations[:5]):
            sim_text = recent_font.render(
                f"{i+1}. Time: {sim['time']:.2f}s | Nodes: {sim['nodes_visited']}", 
                True, LIGHT_GRAY
            )
            win.blit(sim_text, (GRID_WIDTH + 30, 470 + i * 30))
    else:
        no_data_text = recent_font.render("No simulations yet", True, LIGHT_GRAY)
        win.blit(no_data_text, (GRID_WIDTH + 30, 470))

def draw_solving_screen(win, grid, stats=None):
    """Draws the solving screen"""
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win, 0)
    
    draw_grid(win, ROWS, GRID_WIDTH)
    
    if stats:
        # Draw stats panel
        pygame.draw.rect(win, DARK_GRAY, (GRID_WIDTH, 0, WIDTH - GRID_WIDTH, GRID_WIDTH))
        
        stats_font = pygame.font.SysFont('retro', 30)
        
        title_text = stats_font.render("SOLUTION STATS", True, RETRO_GREEN)
        win.blit(title_text, (GRID_WIDTH + 30, 30))
        
        time_text = stats_font.render(f"Time: {stats['time']:.4f}s", True, WHITE)
        complexity_text = stats_font.render(f"Complexity: {stats['complexity']}", True, WHITE)
        visited_text = stats_font.render(f"Nodes visited: {stats['nodes_visited']}", True, WHITE)
        path_text = stats_font.render(f"Path length: {stats['path_length']}", True, WHITE)
        date_text = stats_font.render(f"Date: {stats['timestamp']}", True, WHITE)
        
        win.blit(time_text, (GRID_WIDTH + 30, 80))
        win.blit(complexity_text, (GRID_WIDTH + 30, 120))
        win.blit(visited_text, (GRID_WIDTH + 30, 160))
        win.blit(path_text, (GRID_WIDTH + 30, 200))
        win.blit(date_text, (GRID_WIDTH + 30, 240))
        
        # Back button
        back_button = Button(GRID_WIDTH + 30, GRID_WIDTH - 100, 200, 50, 
                           "BACK TO MENU", RETRO_BLUE, RETRO_GREEN, WHITE)
        back_button.draw(win)
        return back_button
    
    return None

def main():
    """Main function"""
    # Initialize variables
    grid = None
    start = None
    end = None
    maze_id = None
    stats = None
    recent_simulations = load_recent_simulations()
    
    # Create buttons
    generate_button = Button(GRID_WIDTH + 30, 100, 200, 50, 
                           "GENERATE MAZE", RETRO_BLUE, RETRO_GREEN)
    solve_button = Button(GRID_WIDTH + 30, 170, 200, 50, 
                        "SOLVE MAZE", RETRO_BLUE, RETRO_GREEN)
    
    buttons = [generate_button, solve_button]
    
    # Game states
    MAIN_MENU = 0
    SOLVING = 1
    current_state = MAIN_MENU
    
    run = True
    back_button = None
    
    while run:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if current_state == MAIN_MENU:
                # Check button hovers
                for button in buttons:
                    button.check_hover(mouse_pos)
                
                # Check button clicks
                if generate_button.is_clicked(mouse_pos, event):
                    # Generate until we get a valid maze
                    valid = False
                    while not valid:
                        grid = generate_random_grid()
                        valid, start, end = is_valid_grid(grid)
                    
                    if start:
                        start.make_start()
                    if end:
                        end.make_end()
                
                if solve_button.is_clicked(mouse_pos, event) and grid:
                    current_state = SOLVING
                    maze_id = str(int(time.time()))
                    save_maze(grid, maze_id)
                    
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    stats = a_star_algorithm(lambda: draw_solving_screen(WIN, grid, stats), grid, start, end)
                    
                    if stats:
                        stats["maze_id"] = maze_id
                        save_metadata(maze_id, stats)
                        recent_simulations = load_recent_simulations()
            
            elif current_state == SOLVING:
                if back_button and back_button.is_clicked(mouse_pos, event):
                    current_state = MAIN_MENU
        
        # Drawing
        if current_state == MAIN_MENU:
            draw_main_screen(WIN, grid, buttons, recent_simulations)
        elif current_state == SOLVING:
            back_button = draw_solving_screen(WIN, grid, stats)
            if back_button:
                back_button.check_hover(mouse_pos)
        
        pygame.display.update()
    
    pygame.quit()

if __name__ == "__main__":
    # Try to load retro font, fall back to default if not available
    try:
        pygame.font.SysFont('retro', 30)
    except:
        pass
    
    main()