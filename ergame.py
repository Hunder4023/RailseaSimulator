import pygame
import sys
import random
import pyfiglet

# Initialize Pygame
pygame.init()

# Screen and map settings
WIDTH, HEIGHT = 800, 600
MAP_WIDTH, MAP_HEIGHT = 750, 750
TILE_SIZE = 60
ZOOM = 2.0

# Colors
ROAD_COLOR = (50, 50, 50)
GRASS_COLOR = (34, 139, 34)
PLAYER_COLOR = (255, 255, 255)
BOUNDARY_COLOR = (0, 0, 255)
MOB_COLOR = (255, 0, 0)
SALVAGE_COLOR = (0, 255, 255)

# Font and popup settings
pygame.font.init()
font = pygame.font.SysFont(None, 36)
popup_message = ""
popup_timer = 0
pending_battle = False
pending_mob = None

# Player settings
player_size = 5
player_speed = 2
player_hp = 100
player_attacks = {
    "Super Punch": {"damage": 60, "accuracy": 0.8},
    "Super Kick": {"damage": 70, "accuracy": 0.7},
    "Salvage Attack": {"damage": 120, "accuracy": 0.4}
}

# Mob types
mob_types = {
    "Giant Molerat": {"hp": 120, "damage": 50, "accuracy": 0.7},
    "Giant Owl": {"hp": 80, "damage": 70, "accuracy": 0.6},
    "Pirates": {"hp": 90, "damage": 40, "accuracy": 1.0}
}

# Salvage types
salvage_types = ["Map", "Money", "Ordinator", "Radar", "Picture", "Ruined Ship", "Treasure"]

# Mob Kills
mob_kills = 0

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Railsea Simulator")
clock = pygame.time.Clock()

# Store road tiles
road_tiles = []

# Generate map
def generate_map():
    map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
    map_surface.fill(GRASS_COLOR)

    pygame.draw.rect(map_surface, BOUNDARY_COLOR, (0, 0, MAP_WIDTH, TILE_SIZE))
    pygame.draw.rect(map_surface, BOUNDARY_COLOR, (0, MAP_HEIGHT - TILE_SIZE, MAP_WIDTH, TILE_SIZE))
    pygame.draw.rect(map_surface, BOUNDARY_COLOR, (0, 0, TILE_SIZE, MAP_HEIGHT))
    pygame.draw.rect(map_surface, BOUNDARY_COLOR, (MAP_WIDTH - TILE_SIZE, 0, TILE_SIZE, MAP_HEIGHT))

    used_tiles = set()

    y = TILE_SIZE * 2
    while y < MAP_HEIGHT - TILE_SIZE * 2:
        for x in range(TILE_SIZE, MAP_WIDTH - TILE_SIZE, TILE_SIZE):
            tile_pos = (x, y)
            pygame.draw.rect(map_surface, ROAD_COLOR, (*tile_pos, TILE_SIZE, TILE_SIZE))
            used_tiles.add(tile_pos)
            road_tiles.append(tile_pos)
        y += TILE_SIZE * random.randint(5, 14)

    x = TILE_SIZE * 2
    while x < MAP_WIDTH - TILE_SIZE * 2:
        for y in range(TILE_SIZE, MAP_HEIGHT - TILE_SIZE, TILE_SIZE):
            tile_pos = (x, y)
            if tile_pos not in used_tiles:
                pygame.draw.rect(map_surface, ROAD_COLOR, (*tile_pos, TILE_SIZE, TILE_SIZE))
                used_tiles.add(tile_pos)
                road_tiles.append(tile_pos)
        x += TILE_SIZE * random.randint(5, 14)

    return map_surface

game_map = generate_map()
player_pos = list(random.choice(road_tiles))

class Mob:
    def __init__(self, position):
        self.position = position
        self.alive = True
        self.type = random.choice(list(mob_types.keys()))
        self.hp = mob_types[self.type]["hp"]
        self.damage = mob_types[self.type]["damage"]
        self.accuracy = mob_types[self.type]["accuracy"]

class Salvage:
    def __init__(self, position):
        self.position = position
        self.found = False
        self.item = random.choice(salvage_types)

mob_list = [Mob(pos) for pos in random.sample(road_tiles, 4)]
salvage_list = [Salvage(pos) for pos in random.sample(road_tiles, 4)]

def is_on_road(x, y):
    if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
        tile_x = x // TILE_SIZE * TILE_SIZE
        tile_y = y // TILE_SIZE * TILE_SIZE
        color = game_map.get_at((tile_x, tile_y))[:3]
        return color == ROAD_COLOR
    return False

def within_bounds(x, y):
    return 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT

def check_collision(player_pos, obj_pos):
    px, py = player_pos
    ox, oy = obj_pos
    return abs(px - ox) < TILE_SIZE // 2 and abs(py - oy) < TILE_SIZE // 2

def battle(mob):
    global player_hp, mob_kills
    print(f"\n🔥 Battle Start: You vs {mob.type}")
    print(f"{mob.type} HP: {mob.hp} | Your HP: {player_hp}")

    while mob.hp > 0 and player_hp > 0:
        print("\nChoose your attack:")
        for i, (attack, attack_info) in enumerate(player_attacks.items()):
            print(f"{i + 1}. {attack} (Damage: {attack_info['damage']}, Accuracy: {int(attack_info['accuracy'] * 100)}%)")
        choice = input("Enter attack number: ")
        if choice not in ["1", "2", "3"]:
            print("Invalid choice.")
            continue

        attack_name = list(player_attacks.keys())[int(choice) - 1]
        attack = player_attacks[attack_name]

        if random.random() < attack["accuracy"]:
            mob.hp -= attack["damage"]
            print(f"You hit with {attack_name}! {attack['damage']} damage.")
        else:
            print(f"{attack_name} missed!")

        if mob.hp <= 0:
            print(f"{mob.type} defeated!")
            mob.alive = False
            mob_kills += 1
            print(f"🏆 Total mobs defeated: {mob_kills}")
            break

        if random.random() < mob.accuracy:
            player_hp -= mob.damage
            print(f"{mob.type} hits you for {mob.damage} damage!")
        else:
            print(f"{mob.type} missed!")

        print(f"{mob.type} HP: {mob.hp} | Your HP: {player_hp}")

    if player_hp <= 0:
        print("💀 You were defeated...")
        pygame.quit()
        sys.exit()

# Rules text in terminal
print(pyfiglet.figlet_format("RAILSEA"))
print("Welcome to Railsea\nHere are the rules")
print("This is a Railsea simulator where you fight various monsters throughout the world of Railsea")
print("Find Salvages to upgrade your abilities")
print("You can fight mobs in this terminal environment")

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    new_pos = player_pos[:]

    if keys[pygame.K_LEFT]: 
        new_pos[0] -= player_speed
    if keys[pygame.K_RIGHT]: 
        new_pos[0] += player_speed
    if keys[pygame.K_UP]: 
        new_pos[1] -= player_speed
    if keys[pygame.K_DOWN]: 
        new_pos[1] += player_speed

    if within_bounds(new_pos[0], new_pos[1]) and is_on_road(new_pos[0], new_pos[1]):
        player_pos = new_pos

    offset_x = player_pos[0] - WIDTH // (2 * ZOOM)
    offset_y = player_pos[1] - HEIGHT // (2 * ZOOM)

    view_rect = pygame.Rect(offset_x, offset_y, WIDTH // ZOOM, HEIGHT // ZOOM)
    zoom_surface = pygame.Surface((WIDTH // ZOOM, HEIGHT // ZOOM))
    zoom_surface.blit(game_map, (0, 0), view_rect)

    scaled_surface = pygame.transform.scale(zoom_surface, (WIDTH, HEIGHT))
    screen.blit(scaled_surface, (0, 0))

    pygame.draw.rect(screen, PLAYER_COLOR, (
        WIDTH // 2 - player_size * ZOOM // 2,
        HEIGHT // 2 - player_size * ZOOM // 2,
        player_size * ZOOM,
        player_size * ZOOM
    ))

    # Mob Kills Draw
    # Display mob kill count
    kill_text = font.render(f"Mobs Defeated: {mob_kills}", True, (255, 255, 255))
    screen.blit(kill_text, (20, 20))

    for mob in mob_list:
        if mob.alive:
            screen_x = (mob.position[0] - offset_x) * ZOOM
            screen_y = (mob.position[1] - offset_y) * ZOOM
            pygame.draw.rect(screen, MOB_COLOR, (
                screen_x, screen_y, 10 * ZOOM, 10 * ZOOM
            ))
            if mob.alive and check_collision(player_pos, mob.position):
                if pending_mob != mob:
                    popup_message = f"You have encountered a {mob.type}! Press F to fight in terminal!"
                    popup_timer = 120
                    pending_battle = True
                    pending_mob = mob

    for salvage in salvage_list:
        if not salvage.found:
            screen_x = (salvage.position[0] - offset_x) * ZOOM
            screen_y = (salvage.position[1] - offset_y) * ZOOM
            pygame.draw.rect(screen, SALVAGE_COLOR, (
                screen_x,
                                screen_y,
                10 * ZOOM,
                10 * ZOOM
            ))

            if check_collision(player_pos, salvage.position):
                popup_message = f"You found a {salvage.item} salvage!!"
                popup_timer = 120
                salvage.found = True

                # Boost player stats
                player_hp += 20
                for attack in player_attacks.values():
                    attack["damage"] += 10

    # Handle F key to trigger battle
    if pending_battle and pending_mob and keys[pygame.K_f]:
        battle(pending_mob)
        pending_battle = False
        pending_mob = None

    # Display popup message
    if popup_timer > 0:
        text_surface = font.render(popup_message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(text_surface, text_rect)
        popup_timer -= 1

    # Update display and tick clock
    pygame.display.flip()
    clock.tick(60)