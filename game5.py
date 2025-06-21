import pygame
import sys
import os
import json

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1000, 700
WHITE = (255, 255, 255)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (70, 130, 180)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (138, 43, 226)

FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 50, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 20)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knapsack Quest")

# Game Variables
level = 1
capacity = 7
selected = []
hint_items = []
show_about = False
score = 0
best_scores = {}

SAVE_FILE = "knapsack_save.json"

levels = {
    1: [
        {"name": "Gold Coin", "weight": 3, "value": 60},
        {"name": "Silver Coin", "weight": 2, "value": 40},
        {"name": "Magic Potion", "weight": 4, "value": 100},
        {"name": "Gem", "weight": 1, "value": 20},
        {"name": "Scroll", "weight": 5, "value": 120}
    ],
    2: [
        {"name": "Helmet", "weight": 4, "value": 70},
        {"name": "Armor", "weight": 6, "value": 130},
        {"name": "Boots", "weight": 3, "value": 50},
        {"name": "Sword", "weight": 5, "value": 110},
        {"name": "Ring", "weight": 1, "value": 30}
    ],
    3: [
        {"name": "Relic", "weight": 7, "value": 150},
        {"name": "Talisman", "weight": 2, "value": 45},
        {"name": "Crystal", "weight": 5, "value": 90},
        {"name": "Ancient Book", "weight": 6, "value": 120},
        {"name": "Map", "weight": 1, "value": 25}
    ]
}

level_completed = {1: False, 2: False, 3: False}

def load_progress():
    global level, best_scores, level_completed
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            level = data.get("level", 1)
            best_scores = data.get("scores", {})
            level_completed.update(data.get("completed", {}))

def save_progress():
    with open(SAVE_FILE, 'w') as f:
        json.dump({"level": level, "scores": best_scores, "completed": level_completed}, f)

def get_items():
    return levels[level]

def draw_text(text, x, y, color=BLACK, font=FONT):
    txt = font.render(text, True, color)
    screen.blit(txt, (x, y))

def calculate_totals(selected):
    total_weight = sum(get_items()[i]["weight"] for i in selected)
    total_value = sum(get_items()[i]["value"] for i in selected)
    return total_weight, total_value

def knapsack_dp(capacity, items):
    n = len(items)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    for i in range(1, n+1):
        wt = items[i-1]["weight"]
        val = items[i-1]["value"]
        for w in range(capacity+1):
            if wt <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt] + val)
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]

def get_optimal_items(capacity, items):
    n = len(items)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    for i in range(1, n+1):
        wt = items[i-1]["weight"]
        val = items[i-1]["value"]
        for w in range(capacity+1):
            if wt <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-wt] + val)
            else:
                dp[i][w] = dp[i-1][w]
    res = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            res.append(i-1)
            w -= items[i-1]["weight"]
    return res

def draw_about():
    pygame.draw.rect(screen, WHITE, (100, 80, 800, 500))
    pygame.draw.rect(screen, DARK_GRAY, (100, 80, 800, 500), 2)
    lines = [
        "ABOUT KNAPSACK QUEST",
        "",
        "Objective:",
        "Select items with the highest value without exceeding the weight limit.",
        "",
        "Algorithm: 0/1 Knapsack (Dynamic Programming)",
        "dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w - wt[i-1]])",
        "Time Complexity: O(n * W)",
        "",
        "Gameplay:",
        "- Click to select items",
        "- Green: Selected | Yellow: Optimal Hint",
        "- Use Submit to check answer, Hint for help, Reset to try again",
        "- Levels increase in difficulty",
        "- Progress is saved automatically",
        "",
        "Created with pygame."
    ]
    for idx, line in enumerate(lines):
        draw_text(line, 120, 100 + idx * 30, font=SMALL_FONT)

def main():
    global selected, hint_items, show_about, level, capacity, score
    load_progress()
    clock = pygame.time.Clock()
    running = True
    message = ""
    show_win = False

    while running:
        screen.fill(LIGHT_GRAY)
        draw_text(f"Knapsack Quest", 320, 20, font=BIG_FONT)
        draw_text(f"Level: {level}", 50, 20, font=FONT)
        draw_text(f"Score: {score}", 850, 20, font=FONT)

        if show_about:
            draw_about()
        else:
            items = get_items()
            y_offset = 100
            for i, item in enumerate(items):
                rect = pygame.Rect(50, y_offset + i * 90, 300, 70)
                color = GREEN if i in selected else YELLOW if i in hint_items else WHITE
                pygame.draw.rect(screen, color, rect, border_radius=12)
                pygame.draw.circle(screen, DARK_GRAY, (70, y_offset + i * 90 + 35), 20)
                draw_text(f"{item['name']} (W:{item['weight']}, V:{item['value']})", 110, y_offset + i * 90 + 20)

            total_weight, total_value = calculate_totals(selected)
            draw_text(f"Capacity: {capacity}", 500, 100)
            draw_text(f"Total Weight: {total_weight}", 500, 150)
            draw_text(f"Total Value: {total_value}", 500, 200)

            # Buttons
            submit_btn = pygame.Rect(500, 280, 150, 40)
            hint_btn = pygame.Rect(500, 340, 150, 40)
            reset_btn = pygame.Rect(500, 400, 150, 40)
            about_btn = pygame.Rect(500, 460, 150, 40)
            next_btn = pygame.Rect(700, 280, 150, 40)
            prev_btn = pygame.Rect(700, 340, 150, 40)

            pygame.draw.rect(screen, RED, submit_btn, border_radius=10)
            pygame.draw.rect(screen, BLUE, hint_btn, border_radius=10)
            pygame.draw.rect(screen, DARK_GRAY, reset_btn, border_radius=10)
            pygame.draw.rect(screen, DARK_GRAY, about_btn, border_radius=10)
            pygame.draw.rect(screen, ORANGE, next_btn, border_radius=10)
            pygame.draw.rect(screen, PURPLE, prev_btn, border_radius=10)

            draw_text("Submit", 545, 290, WHITE)
            draw_text("Hint", 570, 350, WHITE)
            draw_text("Reset", 560, 410, WHITE)
            draw_text("About", 555, 470, WHITE)
            draw_text("Next Level", 720, 290, WHITE)
            draw_text("Previous", 730, 350, WHITE)

            if message:
                draw_text(message, 400, 600, color=GREEN if show_win else RED)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if show_about:
                    show_about = False
                else:
                    items = get_items()
                    for i in range(len(items)):
                        if pygame.Rect(50, 100 + i * 90, 300, 70).collidepoint(mx, my):
                            if i in selected:
                                selected.remove(i)
                            else:
                                selected.append(i)
                            hint_items = []

                    if submit_btn.collidepoint(mx, my):
                        total_weight, total_value = calculate_totals(selected)
                        if total_weight > capacity:
                            message = "Too heavy! Try again."
                            show_win = False
                        else:
                            optimal = knapsack_dp(capacity, items)
                            if total_value == optimal:
                                message = "Victory! You found the optimal combo!"
                                show_win = True
                                score += 100
                                best_scores[str(level)] = max(best_scores.get(str(level), 0), score)
                                level_completed[level] = True
                                save_progress()
                            else:
                                message = f"Not optimal. Best value is {optimal}."
                                show_win = False

                    if hint_btn.collidepoint(mx, my):
                        hint_items = get_optimal_items(capacity, items)
                        message = "Hint shown. Yellow = optimal combo."

                    if reset_btn.collidepoint(mx, my):
                        selected = []
                        hint_items = []
                        message = ""
                        show_win = False

                    if about_btn.collidepoint(mx, my):
                        show_about = True

                    if next_btn.collidepoint(mx, my):
                        if level < 3 and level_completed[level]:
                            level += 1
                            capacity += 3
                            selected = []
                            hint_items = []
                            message = f"Welcome to Level {level}!"
                            show_win = False
                            save_progress()
                        elif not level_completed[level]:
                            message = "Complete the current level first!"

                    if prev_btn.collidepoint(mx, my):
                        if level > 1:
                            level -= 1
                            capacity -= 3
                            selected = []
                            hint_items = []
                            message = f"Back to Level {level}"
                            show_win = False
                            save_progress()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

