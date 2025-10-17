import pygame
import random
import time
import math
from queue import PriorityQueue

# Inicializa o pygame
pygame.init()

# Constantes
WIDTH = 800
ROWS = 50
CELL_SIZE = WIDTH // ROWS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Janela
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding - Labirinto")

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
    
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, CELL_SIZE, CELL_SIZE))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        
        # Baixo
        if self.row < ROWS - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        
        # Cima
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        
        # Direita
        if self.col < ROWS - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        
        # Esquerda
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])
    
    def __lt__(self, other):
        return self.f < other.f

def h(p1, p2):
    """Heurística - Distância de Manhattan"""
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def generate_random_grid():
    """Gera uma grade aleatória com paredes"""
    grid = [[Node(i, j) for j in range(ROWS)] for i in range(ROWS)]
    
    for i in range(ROWS):
        for j in range(ROWS):
            if random.random() < 0.3:  # 30% de chance de ser parede
                grid[i][j].make_barrier()
    
    return grid

def is_valid_grid(grid):
    """Verifica se a grade é válida (existe caminho entre início e fim)"""
    # Encontra um ponto de início e fim válidos
    start = None
    end = None
    
    # Procura por células que não são paredes nos cantos
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
        return False
    
    # Verifica se há caminho usando BFS
    visited = [[False for _ in range(ROWS)] for _ in range(ROWS)]
    queue = []
    queue.append(start.get_pos())
    visited[start.row][start.col] = True
    
    while queue:
        row, col = queue.pop(0)
        
        if (row, col) == end.get_pos():
            return True
        
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            r = row + dr
            c = col + dc
            
            if 0 <= r < ROWS and 0 <= c < ROWS:
                if not visited[r][c] and not grid[r][c].is_barrier():
                    visited[r][c] = True
                    queue.append((r, c))
    
    return False

def reconstruct_path(current, draw):
    """Reconstrói o caminho do fim ao início"""
    path_length = 0
    while current.parent:
        path_length += 1
        current = current.parent
        current.make_path()
        draw()
    return path_length

def a_star_algorithm(draw, grid, start, end):
    """Implementação do algoritmo A*"""
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
                return None, None, None, None
        
        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end:
            path_length = reconstruct_path(end, draw)
            end_time = time.time()
            elapsed_time = end_time - start_time
            # Complexidade: O(b^d) onde b é o fator de ramificação e d é a profundidade da solução
            complexity = f"O(b^d) - b: fator de ramificação, d: profundidade"
            return elapsed_time, complexity, nodes_visited, path_length
        
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
    
    return None, None, None, None

def draw_grid(win, rows, width):
    """Desenha as linhas da grade"""
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRAY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GRAY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width, stats=None):
    """Desenha tudo na tela"""
    win.fill(WHITE)
    
    for row in grid:
        for node in row:
            node.draw(win)
    
    draw_grid(win, rows, width)
    
    if stats:
        elapsed_time, complexity, nodes_visited, path_length = stats
        
        font = pygame.font.SysFont('Arial', 20)
        
        time_text = font.render(f"Tempo: {elapsed_time:.4f}s", True, BLACK)
        complexity_text = font.render(f"Complexidade: {complexity}", True, BLACK)
        visited_text = font.render(f"Nós visitados: {nodes_visited}", True, BLACK)
        path_text = font.render(f"Tamanho do caminho: {path_length}", True, BLACK)
        
        win.blit(time_text, (10, 10))
        win.blit(complexity_text, (10, 40))
        win.blit(visited_text, (10, 70))
        win.blit(path_text, (10, 100))
    
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    """Obtém a posição do clique na grade"""
    gap = width // rows
    y, x = pos
    
    row = y // gap
    col = x // gap
    
    return row, col

def main():
    """Função principal"""
    # Gera uma grade válida
    while True:
        grid = generate_random_grid()
        if is_valid_grid(grid):
            break
    
    # Encontra início e fim válidos
    start = None
    end = None
    corners = [(0, 0), (0, ROWS-1), (ROWS-1, 0), (ROWS-1, ROWS-1)]
    random.shuffle(corners)
    
    for i, j in corners:
        if not grid[i][j].is_barrier():
            if start is None:
                start = grid[i][j]
                start.make_start()
            elif end is None:
                end = grid[i][j]
                end.make_end()
                break
    
    run = True
    started = False
    stats = None
    
    while run:
        draw(WIN, grid, ROWS, WIDTH, stats)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if started:
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    
                    stats = a_star_algorithm(lambda: draw(WIN, grid, ROWS, WIDTH, stats), grid, start, end)
    
    pygame.quit()

if __name__ == "__main__":
    main()