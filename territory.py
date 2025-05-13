import pygame
import sys
import numpy as np
import random
import time
import math

# Constants
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 14, 14
TILE_SIZE = WIDTH // COLS
LIGHT_BG = (240, 240, 255)
GRID_COLOR = (180, 180, 200)
PLAYER_COLORS = [(80, 180, 255), (255, 100, 100)]
FONT_COLOR = (50, 50, 80)

# Power-up types and their properties
FREEZE = 0
BONUS = 1
SHIELD = 2
SPEED_BOOST = 3
TERRITORY_BOMB = 4
DOUBLE_POINTS = 5

POWERUP_TYPES = {
    FREEZE: {
        'color': (0, 255, 0),
        'duration': 5,  # seconds
        'spawn_weight': 1
    },
    BONUS: {
        'color': (255, 255, 0),
        'duration': 1,
        'spawn_weight': 1
    },
    SHIELD: {
        'color': (0, 0, 255),
        'duration': 5,  # seconds
        'spawn_weight': 1
    },
    SPEED_BOOST: {
        'color': (255, 0, 0),
        'duration': 5,  # seconds
        'spawn_weight': 1
    },
    TERRITORY_BOMB: {
        'color': (255, 165, 0),
        'duration': 1,
        'spawn_weight': 1
    },
    DOUBLE_POINTS: {
        'color': (0, 255, 128),
        'duration': 5,  # seconds
        'spawn_weight': 1
    }
}

# Powerup colors for visualization
POWERUP_COLORS = [p['color'] for p in POWERUP_TYPES.values()]
ANIMATION_FRAMES = 10

# New UI constants
BUTTON_COLOR = (255, 100, 100)
BUTTON_HOVER = (255, 150, 150)
BUTTON_TEXT = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 50)
TITLE_COLOR = (50, 50, 80)
DECORATIVE_COLOR = (180, 210, 255)

# Add player state and movement logic for real-time play
PLAYER_ICONS = [pygame.Surface((1, 1)), pygame.Surface((1, 1))]
PLAYER_STARTS = [(0, 0), (ROWS-1, COLS-1)]
PLAYER_KEYS = [
    {pygame.K_UP: (-1, 0), pygame.K_DOWN: (1, 0), pygame.K_LEFT: (0, -1), pygame.K_RIGHT: (0, 1)},
    None
]

# Add color palette and customization options
COLOR_PALETTE = [
    (80, 180, 255), (255, 100, 100), (120, 200, 120), (255, 180, 60), (180, 120, 255), (255, 120, 200), (80, 80, 180)
]
BOARD_SIZES = [8, 10, 12, 14]
TIMER_OPTIONS = [10, 60, 90, 120]
DIFFICULTY_OPTIONS = ["Easy", "Medium", "Hard"]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF)
pygame.display.set_caption('AI-Based Board Game: Territory Conquest')
font = pygame.font.SysFont('Roboto', 36, bold=True)
title_font = pygame.font.SysFont('Roboto', 64, bold=True)
clock = pygame.time.Clock()

def draw_powerup_icon(surface, icon_type, rect):
    color = POWERUP_TYPES[icon_type]['color']
    if icon_type == FREEZE:
        pygame.draw.circle(surface, color, rect.center, rect.width//2)
        for i in range(4):
            angle = i * math.pi/2
            end_x = rect.centerx + math.cos(angle) * rect.width//2
            end_y = rect.centery + math.sin(angle) * rect.height//2
            pygame.draw.line(surface, (255, 255, 255), rect.center, (end_x, end_y), 2)
    elif icon_type == BONUS:
        pygame.draw.circle(surface, color, rect.center, rect.width//2)
        for i in range(5):
            angle = i * 2 * math.pi/5 - math.pi/2
            end_x = rect.centerx + math.cos(angle) * rect.width//2
            end_y = rect.centery + math.sin(angle) * rect.height//2
            pygame.draw.line(surface, (255, 255, 255), rect.center, (end_x, end_y), 2)
    elif icon_type == SHIELD:
        pygame.draw.circle(surface, color, rect.center, rect.width//2)
        pygame.draw.arc(surface, (255, 255, 255), rect, 0, math.pi, 2)
    elif icon_type == SPEED_BOOST:
        points = [
            rect.center,
            (rect.centerx - rect.width//4, rect.centery - rect.height//4),
            (rect.centerx + rect.width//4, rect.centery),
            (rect.centerx - rect.width//4, rect.centery + rect.height//4),
            rect.center
        ]
        pygame.draw.lines(surface, color, False, points, 3)
    elif icon_type == TERRITORY_BOMB:
        pygame.draw.circle(surface, color, rect.center, rect.width//2)
        for i in range(8):
            angle = i * math.pi/4
            end_x = rect.centerx + math.cos(angle) * rect.width//2
            end_y = rect.centery + math.sin(angle) * rect.height//2
            pygame.draw.line(surface, (255, 255, 255), rect.center, (end_x, end_y), 2)
    elif icon_type == DOUBLE_POINTS:
        pygame.draw.circle(surface, color, rect.center, rect.width//2)
        for i in range(5):
            angle = i * 2 * math.pi/5 - math.pi/2
            end_x = rect.centerx + math.cos(angle) * rect.width//2
            end_y = rect.centery + math.sin(angle) * rect.height//2
            pygame.draw.line(surface, (255, 255, 255), rect.center, (end_x, end_y), 2)
        for i in range(5):
            angle = i * 2 * math.pi/5 - math.pi/2 + math.pi/5
            end_x = rect.centerx + math.cos(angle) * rect.width//3
            end_y = rect.centery + math.sin(angle) * rect.height//3
            pygame.draw.line(surface, (255, 255, 255), rect.center, (end_x, end_y), 2)

def draw_board(board, powerups, animations, player_positions, rows, cols, player_colors):
    sidebar_w = 220
    board_size = min(screen.get_width() - sidebar_w - 40, screen.get_height() - 120) * 0.95
    tile_size = int(board_size // cols)
    board_w = tile_size * cols
    board_h = tile_size * rows
    board_x = (screen.get_width() - sidebar_w - board_w) // 2
    board_y = (screen.get_height() - board_h) // 2 + 40
    shadow_surf = pygame.Surface((board_w + 16, board_h + 16), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (8, 8, board_w, board_h), border_radius=24)
    screen.blit(shadow_surf, (board_x - 8, board_y - 8))
    pygame.draw.rect(screen, (255, 255, 255), (board_x, board_y, board_w, board_h), border_radius=18)
    pygame.draw.rect(screen, GRID_COLOR, (board_x, board_y, board_w, board_h), 4, border_radius=18)
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(board_x + col * tile_size, board_y + row * tile_size, tile_size, tile_size)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1, border_radius=6)
            if board[row, col] != -1:
                color = player_colors[board[row, col]]
                glow_surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                pygame.draw.ellipse(glow_surf, (*color, 80), (0, 0, tile_size, tile_size))
                screen.blit(glow_surf, rect.topleft)
                pygame.draw.ellipse(screen, color, rect.inflate(-tile_size//8, -tile_size//8))
            #Visualize powerups on layout
            if powerups[row, col] != -1:
                powerup_rect = rect.inflate(-tile_size//2, -tile_size//2)
                draw_powerup_icon(screen, powerups[row, col], powerup_rect)
    for idx, (prow, pcol) in enumerate(player_positions):
        rect = pygame.Rect(board_x + pcol * tile_size, board_y + prow * tile_size, tile_size, tile_size)
        pygame.draw.ellipse(screen, player_colors[idx], rect.inflate(-tile_size//3, -tile_size//3), 0)
        pygame.draw.ellipse(screen, (255,255,255), rect.inflate(-tile_size//2, -tile_size//2), 2)
    return board_x, board_y, board_w, sidebar_w

def draw_ui(mode, current_player, speed, scores, board_x, board_y, board_w):
    indicator_y = board_y - 70
    indicator_x = board_x + board_w // 2
    turn_text = f"Player {current_player + 1}'s Turn"
    turn_color = PLAYER_COLORS[current_player]
    turn_font = pygame.font.SysFont('Roboto', 32, bold=True)
    text_surf = turn_font.render(turn_text, True, turn_color)
    text_rect = text_surf.get_rect(center=(indicator_x, indicator_y))
    screen.blit(text_surf, text_rect)
    # Draw a small circle icon for the player
    pygame.draw.circle(screen, turn_color, (indicator_x - text_rect.width // 2 - 30, indicator_y + 8), 14)
    # Score display
    score_font = pygame.font.SysFont('Roboto', 28, bold=True)
    score_text = f"Score:  Player 1: {scores[0]}    Player 2: {scores[1]}"
    score_surf = score_font.render(score_text, True, FONT_COLOR)
    score_rect = score_surf.get_rect(center=(indicator_x, indicator_y + 40))
    screen.blit(score_surf, score_rect)

def heuristic(board, player, rows, cols, player_positions):
    # Heuristic: controlled tiles + available moves + (optional) distance to center
    score = np.sum(board == player)
    moves = 0
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = player_positions[player][0]+dr, player_positions[player][1]+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            moves += 1
    #Center control (to come back in center)
    center = (rows//2, cols//2)
    dist_to_center = abs(player_positions[player][0]-center[0]) + abs(player_positions[player][1]-center[1])
    return score + 0.2*moves - 0.05*dist_to_center

def minimax(board, player_positions, rows, cols, player, depth, maximizing, max_player, min_player):
    if depth == 0:
        return heuristic(board, max_player, rows, cols, player_positions)
    moves = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = player_positions[player][0]+dr, player_positions[player][1]+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            moves.append((nr, nc))
    if not moves:
        return heuristic(board, max_player, rows, cols, player_positions)
    if maximizing:
        best = -float('inf')
        for nr, nc in moves:
            new_board = board.copy()
            new_positions = [list(pos) for pos in player_positions]
            new_positions[player] = [nr, nc]
            new_board[nr, nc] = player  #Steal tile
            val = minimax(new_board, new_positions, rows, cols, 1-player, depth-1, False, max_player, min_player)
            best = max(best, val)
        return best
    else:
        best = float('inf')
        for nr, nc in moves:
            new_board = board.copy()
            new_positions = [list(pos) for pos in player_positions]
            new_positions[player] = [nr, nc]
            new_board[nr, nc] = player  # Steal tile
            val = minimax(new_board, new_positions, rows, cols, 1-player, depth-1, True, max_player, min_player)
            best = min(best, val)
        return best

def ai_move(board, pos, rows, cols, difficulty, player_idx, player_positions, mode, powerups):
    #Get possible moves
    possible_moves = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = pos[0]+dr, pos[1]+dc
        if 0 <= nr < rows and 0 <= nc < cols:
            possible_moves.append((nr, nc))

    # If no possible moves, return current position
    if not possible_moves:
        return list(pos)

    # 1. PRIORITIZE POWERUPS
    for move in possible_moves:
        if powerups[move[0], move[1]] != -1:
            return [move[0], move[1]]

    # 2. Otherwise, use difficulty logic
    if difficulty == 0:
        return list(random.choice(possible_moves))

    smartness = 0.7 if difficulty == 1 else 0.9
    good_moves = [move for move in possible_moves if board[move[0], move[1]] != player_idx]
    
    if good_moves and random.random() < smartness:
        return list(random.choice(good_moves))
    else:
        return list(random.choice(possible_moves))

def spawn_powerup(powerups):
    empty_cells = [(row, col) for row in range(powerups.shape[0]) for col in range(powerups.shape[1]) if powerups[row, col] == -1]
    if empty_cells:
        row, col = random.choice(empty_cells)
        # Weighted random choice based on spawn_weight
        weights = [POWERUP_TYPES[i]['spawn_weight'] for i in range(len(POWERUP_TYPES))]
        powerup_type = random.choices(range(len(POWERUP_TYPES)), weights=weights)[0]
        powerups[row, col] = powerup_type

def claim_tile(board, powerups, animations, row, col, player, speed):
    board[row, col] = player
    animations[row, col] = ANIMATION_FRAMES
    if powerups[row, col] != -1:
        if powerups[row, col] == FREEZE:
            speed = 0.5  # Slow down AI
        elif powerups[row, col] == BONUS:
            # Claim an extra tile if possible
            for r in range(ROWS):
                for c in range(COLS):
                    if board[r, c] == -1 and (r != row or c != col):
                        board[r, c] = player
                        animations[r, c] = ANIMATION_FRAMES
                        break
                else:
                    continue
                break
        powerups[row, col] = -1
    return speed

def check_game_over(board):
    return np.all(board != -1)

def display_winner(scores):
    winner = 0 if scores[0] > scores[1] else 1 if scores[1] > scores[0] else -1
    if winner == -1:
        text = font.render("It's a tie!", True, FONT_COLOR)
    else:
        text = font.render(f'Player {winner + 1} wins!', True, FONT_COLOR)
    screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2))

def draw_animated_background(time_passed):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(LIGHT_BG[0] * (1 - ratio) + LIGHT_BG[0] * ratio)
        g = int(LIGHT_BG[1] * (1 - ratio) + LIGHT_BG[1] * ratio)
        b = int(LIGHT_BG[2] * (1 - ratio) + LIGHT_BG[2] * ratio)
        # Add subtle animation
        offset = math.sin(time_passed * 0.001 + y * 0.01) * 10
        pygame.draw.line(screen, (r, g, b), (0, y + offset), (WIDTH, y + offset))

def draw_decorative_border():
    border_width = 4
    pygame.draw.rect(screen, DECORATIVE_COLOR, (0, 0, WIDTH, HEIGHT), border_width)

def draw_title(text, pos):
    title_surf = title_font.render(text, True, TITLE_COLOR)
    screen.blit(title_surf, pos)

def draw_pattern_background(time_passed):
    screen.fill(LIGHT_BG)
    for x in range(0, WIDTH, 30):
        for y in range(0, HEIGHT, 30):
            
            x_offset = math.sin(time_passed * 0.001 + x * 0.01) * 5
            
            color_shift = int(30 * math.sin(time_passed * 0.001 + x * 0.02 + y * 0.02))
            dot_color = (
                min(255, DECORATIVE_COLOR[0] + color_shift),
                min(255, DECORATIVE_COLOR[1] + color_shift),
                min(255, DECORATIVE_COLOR[2] + color_shift)
            )
            dot_size = 2 + math.sin(time_passed * 0.001 + x * 0.01 + y * 0.01) * 0.7
        
            glow_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*dot_color, 50), (6, 6), int(dot_size*2.2))
            screen.blit(glow_surf, (x + x_offset - 6, y - 6))
            
            pygame.draw.circle(screen, dot_color, (int(x + x_offset), int(y)), int(dot_size))

def draw_decorative_header():
    header_height = 100 
    pygame.draw.rect(screen, DECORATIVE_COLOR, (0, 0, screen.get_width(), header_height))
    title = title_font.render('Territory Conquest', True, TITLE_COLOR)
    # Center the title horizontally and vertically in the header
    title_rect = title.get_rect(center=(screen.get_width() // 2, header_height // 2 + 5))  # +5 for slight drop
    screen.blit(title, title_rect)

def draw_button(text, rect, hovered, font_override=None):
    
    shadow_rect = rect.move(2, 4)
    shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    shadow_surf.fill(SHADOW_COLOR)
    screen.blit(shadow_surf, shadow_rect.topleft)
    color = BUTTON_HOVER if hovered else BUTTON_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=12)
    btn_font = font_override if font_override else pygame.font.SysFont('Roboto', 32, bold=True)
    # Make text fall in shape
    text_to_render = text
    max_width = rect.width - 32
    while btn_font.size(text_to_render)[0] > max_width and len(text_to_render) > 3:
        text_to_render = text_to_render[:-2] + '…'
    text_surf = btn_font.render(text_to_render, True, BUTTON_TEXT)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_menu(time_passed):
    draw_pattern_background(time_passed)
    draw_decorative_header()
    #Button layout
    btn_w, btn_h = 320, 60
    btn_x = WIDTH // 2 - btn_w // 2
    btn_y = HEIGHT // 2 - 40
    mouse = pygame.mouse.get_pos()
    buttons = [
        ('Play', pygame.Rect(btn_x, btn_y, btn_w, btn_h)),
        ('Group Members', pygame.Rect(btn_x, btn_y + 80, btn_w, btn_h)),
        ('Quit', pygame.Rect(btn_x, btn_y + 160, btn_w, btn_h)),
    ]
    for text, rect in buttons:
        hovered = rect.collidepoint(mouse)
        draw_button(text, rect, hovered)
    return buttons

def draw_game_modes(time_passed):
    draw_pattern_background(time_passed)
    draw_decorative_header()
    # Button layout
    btn_w, btn_h = 320, 60
    btn_x = screen.get_width() // 2 - btn_w // 2
    start_y = 200
    mouse = pygame.mouse.get_pos()
    buttons = [
        ('Human vs AI', pygame.Rect(btn_x, start_y, btn_w, btn_h)),
        ('AI vs AI', pygame.Rect(btn_x, start_y + 80, btn_w, btn_h)),
        ('Back', pygame.Rect(btn_x, start_y + 160, btn_w, btn_h)),
    ]
    for text, rect in buttons:
        hovered = rect.collidepoint(mouse)
        draw_button(text, rect, hovered)
    return buttons

def draw_group_members(time_passed):
    draw_pattern_background(time_passed)
    draw_decorative_header()
    # Button layout
    btn_w, btn_h = 520, 54 
    btn_x = screen.get_width() // 2 - btn_w // 2
    start_y = 200
    mouse = pygame.mouse.get_pos()
    small_font = pygame.font.SysFont('Roboto', 22, bold=True)
    buttons = [
        ('22K-0500 Anas Saleem', pygame.Rect(btn_x, start_y, btn_w, btn_h)),
        ('22K-4602 Emanay Arshad', pygame.Rect(btn_x, start_y + 70, btn_w, btn_h)),
        ('22K-4591 Ayesha Abdul Rehman', pygame.Rect(btn_x, start_y + 140, btn_w, btn_h)),
        ('Back', pygame.Rect(btn_x, start_y + 210, btn_w, btn_h)),
    ]
    for text, rect in buttons:
        hovered = rect.collidepoint(mouse)
        # Use smaller font for member names, normal for 'Back'
        font_override = small_font if text != 'Back' else None
        draw_button(text, rect, hovered, font_override)
    return buttons

def draw_sidebar(scores, time_left, powerups_list, sidebar_x, board_y, board_h):
    sidebar_rect = pygame.Rect(sidebar_x, board_y, 200, board_h)
    pygame.draw.rect(screen, (245, 245, 255), sidebar_rect, border_radius=18)
    pygame.draw.rect(screen, GRID_COLOR, sidebar_rect, 3, border_radius=18)
    font_big = pygame.font.SysFont('Roboto', 28, bold=True)
    font_small = pygame.font.SysFont('Roboto', 22, bold=True)
    #Scores
    score1 = font_big.render(f'Player 1: {scores[0]}', True, PLAYER_COLORS[0])
    score2 = font_big.render(f'Player 2: {scores[1]}', True, PLAYER_COLORS[1])
    screen.blit(score1, (sidebar_x + 20, board_y + 30))
    screen.blit(score2, (sidebar_x + 20, board_y + 70))
    #Timer
    timer = font_big.render(f'Time: {time_left}s', True, (80, 80, 120))
    screen.blit(timer, (sidebar_x + 20, board_y + 120))
    #Powerups
    screen.blit(font_small.render('Powerups:', True, (80, 80, 120)), (sidebar_x + 20, board_y + 180))
    for i, p in enumerate(powerups_list):
        if p == 0:
            pygame.draw.circle(screen, (0, 200, 0), (sidebar_x + 40, board_y + 220 + i*40), 14, 3)
        elif p == 1:
            pygame.draw.circle(screen, (200, 200, 0), (sidebar_x + 40, board_y + 220 + i*40), 14, 3)

def draw_customization_screen(selected_colors, selected_size, selected_timer, player_names, focus_idx, selected_difficulty):
    draw_pattern_background(pygame.time.get_ticks())
    draw_decorative_header()
    font_big = pygame.font.SysFont('Roboto', 32, bold=True)
    font_small = pygame.font.SysFont('Roboto', 24, bold=True)
    y = 140
    #Player 1 Color
    screen.blit(font_big.render('Player 1 Color:', True, FONT_COLOR), (80, y))
    for i, color in enumerate(COLOR_PALETTE):
        rect = pygame.Rect(300 + i*60, y, 40, 40)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if selected_colors[0] == i:
            pygame.draw.rect(screen, (40, 40, 80), rect, 4, border_radius=8)
        if selected_colors[1] == i:
            pygame.draw.line(screen, (180, 180, 180), rect.topleft, rect.bottomright, 4)
            pygame.draw.line(screen, (180, 180, 180), rect.topright, rect.bottomleft, 4)
    y += 60
    #Player 2 Color
    screen.blit(font_big.render('Player 2 Color:', True, FONT_COLOR), (80, y))
    for i, color in enumerate(COLOR_PALETTE):
        rect = pygame.Rect(300 + i*60, y, 40, 40)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if selected_colors[1] == i:
            pygame.draw.rect(screen, (40, 40, 80), rect, 4, border_radius=8)
        if selected_colors[0] == i:
            pygame.draw.line(screen, (180, 180, 180), rect.topleft, rect.bottomright, 4)
            pygame.draw.line(screen, (180, 180, 180), rect.topright, rect.bottomleft, 4)
    y += 70
    #Board Size
    screen.blit(font_big.render('Board Size:', True, FONT_COLOR), (80, y))
    for i, size in enumerate(BOARD_SIZES):
        rect = pygame.Rect(300 + i*70, y, 60, 40)
        pygame.draw.rect(screen, (220, 240, 255) if selected_size != i else (80, 180, 255), rect, border_radius=8)
        txt = font_small.render(f'{size}x{size}', True, (50, 50, 80) if selected_size != i else (255,255,255))
        screen.blit(txt, txt.get_rect(center=rect.center))
    y += 60
    #Timer
    screen.blit(font_big.render('Timer:', True, FONT_COLOR), (80, y))
    for i, t in enumerate(TIMER_OPTIONS):
        rect = pygame.Rect(300 + i*70, y, 60, 40)
        pygame.draw.rect(screen, (220, 240, 255) if selected_timer != i else (80, 180, 255), rect, border_radius=8)
        txt = font_small.render(f'{t}s', True, (50, 50, 80) if selected_timer != i else (255,255,255))
        screen.blit(txt, txt.get_rect(center=rect.center))
    y += 60
    #Difficulty
    screen.blit(font_big.render('Difficulty:', True, FONT_COLOR), (80, y))
    for i, diff in enumerate(DIFFICULTY_OPTIONS):
        rect = pygame.Rect(300 + i*110, y, 100, 40)
        pygame.draw.rect(screen, (220, 240, 255) if selected_difficulty != i else (80, 180, 255), rect, border_radius=8)
        txt = font_small.render(diff, True, (50, 50, 80) if selected_difficulty != i else (255,255,255))
        screen.blit(txt, txt.get_rect(center=rect.center))
    y += 60
    #Player Names
    screen.blit(font_big.render('Player 1 Name:', True, FONT_COLOR), (80, y))
    name_rect1 = pygame.Rect(300, y, 200, 36)
    pygame.draw.rect(screen, (255,255,255), name_rect1, border_radius=6)
    pygame.draw.rect(screen, (80,180,255) if focus_idx==0 else (180,180,200), name_rect1, 2, border_radius=6)
    name_surf1 = font_small.render(player_names[0], True, (50,50,80))
    screen.blit(name_surf1, (name_rect1.x+8, name_rect1.y+6))
    y += 50
    screen.blit(font_big.render('Player 2 Name:', True, FONT_COLOR), (80, y))
    name_rect2 = pygame.Rect(300, y, 200, 36)
    pygame.draw.rect(screen, (255,255,255), name_rect2, border_radius=6)
    pygame.draw.rect(screen, (80,180,255) if focus_idx==1 else (180,180,200), name_rect2, 2, border_radius=6)
    name_surf2 = font_small.render(player_names[1], True, (50,50,80))
    screen.blit(name_surf2, (name_rect2.x+8, name_rect2.y+6))
    #Start/Back buttons
    start_rect = pygame.Rect(300, y+60, 120, 48)
    back_rect = pygame.Rect(440, y+60, 120, 48)
    pygame.draw.rect(screen, (80, 180, 255), start_rect, border_radius=10)
    pygame.draw.rect(screen, (220, 100, 100), back_rect, border_radius=10)
    screen.blit(font_small.render('Start Game', True, (255,255,255)), start_rect.move(16,10))
    screen.blit(font_small.render('Back', True, (255,255,255)), back_rect.move(36,10))
    return {
        'color_rects': [(pygame.Rect(300 + i*60, 140, 40, 40), i, 0) for i in range(len(COLOR_PALETTE))] +
                      [(pygame.Rect(300 + i*60, 200, 40, 40), i, 1) for i in range(len(COLOR_PALETTE))],
        'size_rects': [pygame.Rect(300 + i*70, 270, 60, 40) for i in range(len(BOARD_SIZES))],
        'timer_rects': [pygame.Rect(300 + i*70, 330, 60, 40) for i in range(len(TIMER_OPTIONS))],
        'difficulty_rects': [pygame.Rect(300 + i*110, 390, 100, 40) for i in range(len(DIFFICULTY_OPTIONS))],
        'name_rects': [name_rect1, name_rect2],
        'start_rect': start_rect,
        'back_rect': back_rect
    }

def draw_powerup_legend_top():
    font_small = pygame.font.SysFont('Roboto', 18, bold=True)
    legend = [
        (FREEZE, 'Freeze', 'Freezes opponent for 5s'),
        (BONUS, 'Bonus', 'Claim +1 tile'),
        (SHIELD, 'Shield', 'Tile immunity 5s'),
        (SPEED_BOOST, 'Speed', 'Double speed 5s'),
        (TERRITORY_BOMB, 'Bomb', 'Claim adjacent tiles'),
        (DOUBLE_POINTS, 'Double Points', 'Double points 5s'),
    ]
    cols = 3
    col_width = 260
    row_height = 43
    x0, y0 = 30, 30
    for idx, (ptype, name, desc) in enumerate(legend):
        col = idx % cols
        row = idx // cols
        icon_rect = pygame.Rect(x0 + col*col_width, y0 + row*row_height, 20, 20)
        draw_powerup_icon(screen, ptype, icon_rect)
        screen.blit(font_small.render(name, True, (60,60,80)), (icon_rect.right + 4, icon_rect.y))
        screen.blit(font_small.render(desc, True, (120,120,120)), (icon_rect.right + 4, icon_rect.y + 14))

def draw_game_screen(board, powerups, player_positions, player_names, player_colors, scores, time_left, rows, cols, player_types, powerup_timers, powerup_effects, freeze_end_time, timer_paused_until):
    screen.fill((245, 245, 255))
    draw_powerup_legend_top()
    board_x, board_y, board_w, sidebar_w = draw_board(board, powerups, np.zeros((rows, cols), dtype=int), player_positions, rows, cols, player_colors)
    sidebar_rect = pygame.Rect(screen.get_width() - 220, board_y, 200, board_w)
    pygame.draw.rect(screen, (235, 235, 250), sidebar_rect, border_radius=18)
    pygame.draw.rect(screen, (180, 180, 200), sidebar_rect, 3, border_radius=18)
    font_big = pygame.font.SysFont('Roboto', 28, bold=True)
    font_small = pygame.font.SysFont('Roboto', 22, bold=True)
    font_timer = pygame.font.SysFont('Roboto', 18, bold=True)
    current_time = pygame.time.get_ticks()
    for i, (name, color, ptype) in enumerate(zip(player_names, player_colors, player_types)):
        y_offset = board_y + 40 + i*90  # Increased gap
        pygame.draw.circle(screen, color, (sidebar_rect.x + 30, y_offset), 16)
        screen.blit(font_big.render(name, True, color), (sidebar_rect.x + 60, y_offset - 12))
        screen.blit(font_small.render(f'Score: {scores[i]}', True, (80, 80, 120)), (sidebar_rect.x + 60, y_offset + 14))
        type_label = font_small.render(ptype, True, (120, 120, 120))
        screen.blit(type_label, (sidebar_rect.x + 60, y_offset + 34))
        # Show active powerup timers
        timer_y = y_offset + 54
        if powerup_effects[i]['shield'] and powerup_timers[i].get('shield', 0) > current_time:
            t = int((powerup_timers[i]['shield'] - current_time) / 1000)
            screen.blit(font_timer.render(f'Shield: {t}s', True, (0,0,255)), (sidebar_rect.x + 60, timer_y))
            timer_y += 18
        if powerup_effects[i]['speed_boost'] and powerup_timers[i].get('speed_boost', 0) > current_time:
            t = int((powerup_timers[i]['speed_boost'] - current_time) / 1000)
            screen.blit(font_timer.render(f'Speed: {t}s', True, (255,0,0)), (sidebar_rect.x + 60, timer_y))
            timer_y += 18
        if powerup_effects[i]['double_points'] and powerup_timers[i].get('double_points', 0) > current_time:
            t = int((powerup_timers[i]['double_points'] - current_time) / 1000)
            screen.blit(font_timer.render(f'Double Points: {t}s', True, (0,180,80)), (sidebar_rect.x + 60, timer_y))
            timer_y += 18
        # Show freeze timer if player is frozen
        if freeze_end_time[i] > current_time:
            t = int((freeze_end_time[i] - current_time) / 1000)
            screen.blit(font_timer.render(f'Freeze: {t}s', True, (0,200,0)), (sidebar_rect.x + 60, timer_y))
            timer_y += 18
    timer = font_big.render(f'Time: {time_left}s', True, (80, 80, 120))
    screen.blit(timer, (sidebar_rect.x + 20, board_y + board_w - 60))
    return {}

def main():
    running = True
    in_menu = True
    in_game_modes = False
    in_custom = False
    in_game = False
    in_group_members = False
    selected_colors = [0, 1]
    selected_size = 0
    selected_timer = 0
    selected_difficulty = 0
    player_names = ["Player 1", "Player 2"]
    focus_idx = -1
    game_mode = None
    while running:
        if in_menu:
            time_passed = pygame.time.get_ticks()
            buttons = draw_menu(time_passed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for idx, (text, rect) in enumerate(buttons):
                        if rect.collidepoint((x, y)):
                            if text == 'Play':
                                in_menu = False
                                in_game_modes = True
                            elif text == 'Group Members':
                                in_menu = False
                                in_group_members = True
                            elif text == 'Quit':
                                running = False
            pygame.display.flip()
        elif in_group_members:
            time_passed = pygame.time.get_ticks()
            buttons = draw_group_members(time_passed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for text, rect in buttons:
                        if rect.collidepoint((x, y)):
                            if text == 'Back':
                                in_group_members = False
                                in_menu = True
            pygame.display.flip()
        elif in_game_modes:
            time_passed = pygame.time.get_ticks()
            buttons = draw_game_modes(time_passed)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for text, rect in buttons:
                        if rect.collidepoint((x, y)):
                            if text == 'Human vs AI' or text == 'AI vs AI':
                                game_mode = text
                                in_game_modes = False
                                in_custom = True
                            elif text == 'Back':
                                in_menu = True
                                in_game_modes = False
            pygame.display.flip()
        elif in_custom:
            ui_rects = draw_customization_screen(selected_colors, selected_size, selected_timer, player_names, focus_idx, selected_difficulty)
            can_start = (
                selected_colors[0] != selected_colors[1] and
                all(name.strip() for name in player_names)
            )
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for rect, idx, which in ui_rects['color_rects']:
                        if rect.collidepoint((x, y)):
                            if which == 0 and idx != selected_colors[1]:
                                selected_colors[0] = idx
                            if which == 1 and idx != selected_colors[0]:
                                selected_colors[1] = idx
                    for i, rect in enumerate(ui_rects['size_rects']):
                        if rect.collidepoint((x, y)):
                            selected_size = i
                    for i, rect in enumerate(ui_rects['timer_rects']):
                        if rect.collidepoint((x, y)):
                            selected_timer = i
                    for i, rect in enumerate(ui_rects['difficulty_rects']):
                        if rect.collidepoint((x, y)):
                            selected_difficulty = i
                    for i, rect in enumerate(ui_rects['name_rects']):
                        if rect.collidepoint((x, y)):
                            focus_idx = i
                    if ui_rects['start_rect'].collidepoint((x, y)) and can_start:
                        in_custom = False
                        in_game = True
                        game_settings = {
                            'size': BOARD_SIZES[selected_size],
                            'timer': TIMER_OPTIONS[selected_timer],
                            'difficulty': selected_difficulty,
                            'player_colors': [COLOR_PALETTE[selected_colors[0]], COLOR_PALETTE[selected_colors[1]]],
                            'player_names': player_names[:],
                            'mode': game_mode
                        }
                    if ui_rects['back_rect'].collidepoint((x, y)):
                        in_custom = False
                        in_game_modes = True
                if event.type == pygame.KEYDOWN and focus_idx != -1:
                    if event.key == pygame.K_BACKSPACE:
                        player_names[focus_idx] = player_names[focus_idx][:-1]
                    elif event.key == pygame.K_RETURN:
                        focus_idx = -1
                    elif len(player_names[focus_idx]) < 16 and event.unicode.isprintable():
                        player_names[focus_idx] += event.unicode
            pygame.display.flip()
        elif in_game:
            try:
                size = game_settings['size']
                rows, cols = size, size
                player_colors = game_settings['player_colors']
                names = game_settings['player_names']
                timer = game_settings['timer']
                difficulty = game_settings['difficulty']
                game_mode = game_settings['mode']
                
                # Initialize game state
                player_positions = [list((0, 0)), list((rows-1, cols-1))]
                board = np.full((rows, cols), -1)
                board[player_positions[0][0], player_positions[0][1]] = 0
                board[player_positions[1][0], player_positions[1][1]] = 1
                scores = [1, 1]  # Each player starts with 1 tile
                
                # Initialize powerups and effects
                powerups = np.full((rows, cols), -1)
                powerup_end_times = {0: {}, 1: {}}
                powerup_effects = {
                    0: {'shield': False, 'speed_boost': False, 'double_points': False},
                    1: {'shield': False, 'speed_boost': False, 'double_points': False}
                }
                powerup_spawn_timer = pygame.time.get_ticks()
                POWERUP_SPAWN_INTERVAL = 5000
                
                game_running = True
                start_ticks = pygame.time.get_ticks()
                player_types = ["AI", "AI"] if game_mode == "AI vs AI" else ["Human", "AI"]
                last_move_time = {0: 0, 1: 0}
                MOVE_DELAY = 500
                freeze_end_time = {0: 0, 1: 0}
                
                while game_running:
                    current_time = pygame.time.get_ticks()
                    
                    # Handle game timer
                    time_left = max(0, timer - (current_time - start_ticks)//1000)
                    
                    # Handle powerup spawning
                    if current_time - powerup_spawn_timer > POWERUP_SPAWN_INTERVAL:
                        spawn_powerup(powerups)
                        powerup_spawn_timer = current_time
                    
                    # Update powerup effects based on current time and end times
                    for player in [0, 1]:
                        if current_time >= powerup_end_times[player].get('shield', 0):
                            powerup_effects[player]['shield'] = False
                        if current_time >= powerup_end_times[player].get('speed_boost', 0):
                            powerup_effects[player]['speed_boost'] = False
                        if current_time >= powerup_end_times[player].get('double_points', 0):
                            powerup_effects[player]['double_points'] = False
                    
                    # Calculate move delay based on speed boost
                    move_delays = [MOVE_DELAY, MOVE_DELAY]
                    if powerup_effects[0]['speed_boost']:
                        move_delays[0] = MOVE_DELAY // 7
                    if powerup_effects[1]['speed_boost']:
                        move_delays[1] = MOVE_DELAY // 7
                    
                    # Handle AI moves
                    for player_idx in [0, 1]:
                        if current_time < freeze_end_time[player_idx]: continue  # skip move if frozen
                        if current_time - last_move_time[player_idx] >= move_delays[player_idx]:
                            if player_types[player_idx] == "AI":
                                move_distance = 2 if powerup_effects[player_idx]['speed_boost'] else 1
                                ai_new_pos = ai_move(board, player_positions[player_idx], rows, cols, difficulty, player_idx, player_positions, game_mode, powerups)
                                
                                # Ensure the new position is valid
                                if not (0 <= ai_new_pos[0] < rows and 0 <= ai_new_pos[1] < cols):
                                    continue
                                
                                # Handle powerup collection
                                if powerups[ai_new_pos[0], ai_new_pos[1]] != -1:
                                    powerup_type = powerups[ai_new_pos[0], ai_new_pos[1]]
                                    if powerup_type == FREEZE:
                                        prev_end = freeze_end_time[1 - player_idx]
                                        if prev_end > current_time:
                                            freeze_end_time[1 - player_idx] = prev_end + POWERUP_TYPES[FREEZE]['duration'] * 1000
                                        else:
                                            freeze_end_time[1 - player_idx] = current_time + POWERUP_TYPES[FREEZE]['duration'] * 1000
                                    elif powerup_type == BONUS:
                                        board[ai_new_pos[0], ai_new_pos[1]] = player_idx
                                        for r in range(rows):
                                            for c in range(cols):
                                                if board[r, c] == -1 and (r != ai_new_pos[0] or c != ai_new_pos[1]):
                                                    board[r, c] = player_idx
                                                    break
                                            else:
                                                continue
                                            break
                                    elif powerup_type == SHIELD:
                                        powerup_effects[player_idx]['shield'] = True
                                        prev_end = powerup_end_times[player_idx].get('shield', 0)
                                        if prev_end > current_time:
                                            powerup_end_times[player_idx]['shield'] = prev_end + POWERUP_TYPES[SHIELD]['duration'] * 1000
                                        else:
                                            powerup_end_times[player_idx]['shield'] = current_time + POWERUP_TYPES[SHIELD]['duration'] * 1000
                                    elif powerup_type == SPEED_BOOST:
                                        powerup_effects[player_idx]['speed_boost'] = True
                                        prev_end = powerup_end_times[player_idx].get('speed_boost', 0)
                                        if prev_end > current_time:
                                            powerup_end_times[player_idx]['speed_boost'] = prev_end + POWERUP_TYPES[SPEED_BOOST]['duration'] * 1000
                                        else:
                                            powerup_end_times[player_idx]['speed_boost'] = current_time + POWERUP_TYPES[SPEED_BOOST]['duration'] * 1000
                                    elif powerup_type == TERRITORY_BOMB:
                                        for adr, adc in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                                            nr, nc = ai_new_pos[0] + adr, ai_new_pos[1] + adc
                                            if 0 <= nr < rows and 0 <= nc < cols:
                                                board[nr, nc] = player_idx
                                    elif powerup_type == DOUBLE_POINTS:
                                        powerup_effects[player_idx]['double_points'] = True
                                        prev_end = powerup_end_times[player_idx].get('double_points', 0)
                                        if prev_end > current_time:
                                            powerup_end_times[player_idx]['double_points'] = prev_end + POWERUP_TYPES[DOUBLE_POINTS]['duration'] * 1000
                                        else:
                                            powerup_end_times[player_idx]['double_points'] = current_time + POWERUP_TYPES[DOUBLE_POINTS]['duration'] * 1000
                                    powerups[ai_new_pos[0], ai_new_pos[1]] = -1
                                
                                # Update board and scores
                                cell_owner = board[ai_new_pos[0], ai_new_pos[1]]
                                if not (cell_owner != -1 and powerup_effects[cell_owner]['shield'] and cell_owner != player_idx):
                                    if cell_owner != player_idx:
                                        board[ai_new_pos[0], ai_new_pos[1]] = player_idx
                                        if cell_owner != -1 and cell_owner != player_idx:
                                            if scores[cell_owner] > 0:
                                                scores[cell_owner] -= 1
                                        if powerup_effects[player_idx]['double_points']:
                                            scores[player_idx] += 2
                                        else:
                                            scores[player_idx] += 1
                                
                                player_positions[player_idx] = ai_new_pos
                                last_move_time[player_idx] = current_time
                    
                    # Handle human input in Human vs AI mode
                    if game_mode == "Human vs AI":
                        if current_time < freeze_end_time[0]: continue  # skip input if frozen
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                                game_running = False
                            if event.type == pygame.KEYDOWN:
                                for key, delta in PLAYER_KEYS[0].items():
                                    if event.key == key:
                                        move_distance = 2 if powerup_effects[0]['speed_boost'] else 1
                                        valid_move = True
                                        prev_pos = player_positions[0][:]
                                        for step in range(1, move_distance + 1):
                                            new_row = prev_pos[0] + delta[0] * step
                                            new_col = prev_pos[1] + delta[1] * step
                                            if not (0 <= new_row < rows and 0 <= new_col < cols):
                                                valid_move = False
                                                break
                                        if valid_move:
                                            for step in range(1, move_distance + 1):
                                                new_row = prev_pos[0] + delta[0] * step
                                                new_col = prev_pos[1] + delta[1] * step
                                                # Check for powerup
                                                if powerups[new_row, new_col] != -1:
                                                    powerup_type = powerups[new_row, new_col]
                                                    if powerup_type == FREEZE:
                                                        prev_end = freeze_end_time[1]
                                                        if prev_end > current_time:
                                                            freeze_end_time[1] = prev_end + POWERUP_TYPES[FREEZE]['duration'] * 1000
                                                        else:
                                                            freeze_end_time[1] = current_time + POWERUP_TYPES[FREEZE]['duration'] * 1000
                                                    elif powerup_type == BONUS:
                                                        board[new_row, new_col] = 0
                                                        for r in range(rows):
                                                            for c in range(cols):
                                                                if board[r, c] == -1 and (r != new_row or c != new_col):
                                                                    board[r, c] = 0
                                                                    break
                                                            else:
                                                                continue
                                                            break
                                                    elif powerup_type == SHIELD:
                                                        powerup_effects[0]['shield'] = True
                                                        prev_end = powerup_end_times[0].get('shield', 0)
                                                        if prev_end > current_time:
                                                            powerup_end_times[0]['shield'] = prev_end + POWERUP_TYPES[SHIELD]['duration'] * 1000
                                                        else:
                                                            powerup_end_times[0]['shield'] = current_time + POWERUP_TYPES[SHIELD]['duration'] * 1000
                                                    elif powerup_type == SPEED_BOOST:
                                                        powerup_effects[0]['speed_boost'] = True
                                                        prev_end = powerup_end_times[0].get('speed_boost', 0)
                                                        if prev_end > current_time:
                                                            powerup_end_times[0]['speed_boost'] = prev_end + POWERUP_TYPES[SPEED_BOOST]['duration'] * 1000
                                                        else:
                                                            powerup_end_times[0]['speed_boost'] = current_time + POWERUP_TYPES[SPEED_BOOST]['duration'] * 1000
                                                    elif powerup_type == TERRITORY_BOMB:
                                                        for adr, adc in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                                                            anr, anc = new_row + adr, new_col + adc
                                                            if 0 <= anr < rows and 0 <= anc < cols:
                                                                board[anr, anc] = 0
                                                    elif powerup_type == DOUBLE_POINTS:
                                                        powerup_effects[0]['double_points'] = True
                                                        prev_end = powerup_end_times[0].get('double_points', 0)
                                                        if prev_end > current_time:
                                                            powerup_end_times[0]['double_points'] = prev_end + POWERUP_TYPES[DOUBLE_POINTS]['duration'] * 1000
                                                        else:
                                                            powerup_end_times[0]['double_points'] = current_time + POWERUP_TYPES[DOUBLE_POINTS]['duration'] * 1000
                                                    powerups[new_row, new_col] = -1
                                                # PATCH: Score only increases if a new tile is claimed (not if moving onto own tile)
                                                cell_owner = board[new_row, new_col]
                                                if not (cell_owner != -1 and powerup_effects[cell_owner]['shield'] and cell_owner != 0):
                                                    if cell_owner != 0:
                                                        board[new_row, new_col] = 0
                                                        if cell_owner != -1 and cell_owner != 0:
                                                            if scores[cell_owner] > 0:
                                                                scores[cell_owner] -= 1
                                                        if powerup_effects[0]['double_points']:
                                                            scores[0] += 2
                                                        else:
                                                            scores[0] += 1
                                            player_positions[0] = [prev_pos[0] + delta[0] * move_distance, prev_pos[1] + delta[1] * move_distance]
                    
                    ui_rects = draw_game_screen(board, powerups, player_positions, names, player_colors, scores, time_left, rows, cols, player_types, powerup_end_times, powerup_effects, freeze_end_time, 0)
                    pygame.display.flip()
                    pygame.time.Clock().tick(60)
                    
                    if time_left <= 0:
                        game_running = False
                
                scores = [np.sum(board == 0), np.sum(board == 1)]
                winner = 0 if scores[0] > scores[1] else 1 if scores[1] > scores[0] else -1
                screen.fill((255,255,255))
                font_big = pygame.font.SysFont('Roboto', 48, bold=True)
                if winner == -1:
                    msg = 'It\'s a tie!'
                else:
                    msg = f'{names[winner]} wins!'
                text = font_big.render(msg, True, (80,80,120))
                screen.blit(text, text.get_rect(center=(screen.get_width()//2, screen.get_height()//2-40)))
                # Display both player scores
                font_score = pygame.font.SysFont('Roboto', 36, bold=True)
                score_text = f"{names[0]}: {scores[0]}    {names[1]}: {scores[1]}"
                score_surf = font_score.render(score_text, True, (80,80,120))
                screen.blit(score_surf, score_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2+10)))
                font_count = pygame.font.SysFont('Roboto', 36, bold=True)
                for countdown in range(3, 0, -1):
                    count_text = font_count.render(f'Redirecting in {countdown}...', True, (120,120,120))
                    screen.blit(count_text, count_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2+40)))
                    screen.blit(score_surf, score_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2+10)))
                    pygame.display.flip()
                    pygame.time.wait(1000)
                    screen.fill((255,255,255))
                    screen.blit(text, text.get_rect(center=(screen.get_width()//2, screen.get_height()//2-40)))
                    screen.blit(score_surf, score_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//2+10)))
                in_game = False
                in_menu = True
            except Exception as e:
                print(f"Game error: {str(e)}")
                in_game = False
                in_menu = True

if __name__ == '__main__':
    main() 