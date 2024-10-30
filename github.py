import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 830
FPS = 60
CAR_WIDTH, CAR_HEIGHT = 60, 100
OTHER_CAR_WIDTH, OTHER_CAR_HEIGHT = 60, 100
NUM_LANES = 5
LANE_WIDTH = WIDTH // NUM_LANES

try:
    player_car_image = pygame.image.load("koenigseggpygametransparent.png")
    other_car_image = pygame.image.load("carpygametransparent.png")
except pygame.error as e:
    print(f"Failed to load images: {e}")
    pygame.quit()
    sys.exit()

player_car_image = pygame.transform.scale(player_car_image, (CAR_WIDTH, CAR_HEIGHT))
other_car_image = pygame.transform.scale(other_car_image, (OTHER_CAR_WIDTH, OTHER_CAR_HEIGHT))

try:
    accelerate_sound = pygame.mixer.Sound("bestacceleration.mp3")
    brake_sound = pygame.mixer.Sound("tiresscreeching.wav")
except pygame.error as e:
    print(f"Failed to load sound: {e}")
    accelerate_sound = None
    brake_sound = None

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

cars = {
    "Fast": {"top_speed": 399.117, "acceleration": 0.49, "steering_speed": 8},
    "Medium": {"top_speed": 350, "acceleration": 0.11, "steering_speed": 9},
    "Slow": {"top_speed": 300, "acceleration": 0.13, "steering_speed": 10},
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retro Racing Game")

font = pygame.font.Font(None, 38)

def draw_road():
    screen.fill(BLACK)
    for i in range(NUM_LANES + 1):
        lane_x = i * LANE_WIDTH
        pygame.draw.rect(screen, WHITE, (lane_x - 5, 0, 10, HEIGHT))

def draw_player_car(x, y, angle):
    rotated_image = pygame.transform.rotate(player_car_image, angle)
    new_rect = rotated_image.get_rect(center=(x + CAR_WIDTH // 2, y + CAR_HEIGHT // 2))
    screen.blit(rotated_image, new_rect.topleft)

def draw_other_cars(other_cars):
    for car in other_cars:
        screen.blit(other_car_image, (car['x'], car['y']))

def check_collision(player_x, player_y, other_cars):
    player_rect = pygame.Rect(player_x + 27, player_y + 27, CAR_WIDTH - 27, CAR_HEIGHT - 27)
    for car in other_cars:
        car_rect = pygame.Rect(car['x'], car['y'], OTHER_CAR_WIDTH, OTHER_CAR_HEIGHT)
        if player_rect.colliderect(car_rect):
            return True
    return False

def draw_damage_bar(damage, max_damage):
    bar_width = 350
    bar_height = 20
    x = (WIDTH - bar_width) // 2
    y = 10
    damage_ratio = damage / max_damage
    current_bar_width = bar_width * damage_ratio

    pygame.draw.rect(screen, WHITE, (x, y, bar_width, bar_height))
    pygame.draw.rect(screen, RED, (x, y, current_bar_width, bar_height))

def car_selection():
    selected_car = "Fast"
    cars_list = list(cars.keys())
    index = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            index = (index - 1) % len(cars_list)
            selected_car = cars_list[index]
        if keys[pygame.K_RIGHT]:
            index = (index + 1) % len(cars_list)
            selected_car = cars_list[index]
        if keys[pygame.K_RETURN]:
            return selected_car

        draw_road()
        title_text = font.render("Select Your Car", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))

        for i, car in enumerate(cars_list):
            color = WHITE if i == index else (150, 150, 150)
            car_text = font.render(car, True, color)
            screen.blit(car_text, (WIDTH // 2 - car_text.get_width() // 2, HEIGHT // 2 + i * 30))

        pygame.display.flip()
        pygame.time.delay(100)

def crash_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        draw_road()
        title_text = font.render("Crashed! Press R to Respawn or Q to Quit", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))

        pygame.display.flip()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            return True
        if keys[pygame.K_q]:
            pygame.quit()
            sys.exit()

def main(selected_car):
    player_x = WIDTH // 2 - CAR_WIDTH // 2
    player_y = HEIGHT - CAR_HEIGHT - 50
    player_speed = 0
    angle = 0

    damage = 0
    MAX_DAMAGE = 800
    sound_playing = False

    boosted_top_speed = cars[selected_car]["top_speed"] * 1000 / 3585 + 40 / 3.6

    other_cars = []
    for _ in range(4):
        lane_index = random.randint(0, NUM_LANES - 1)
        car_x = lane_index * LANE_WIDTH + (LANE_WIDTH - OTHER_CAR_WIDTH) // 2
        car_y = random.randint(-HEIGHT, 0)
        other_cars.append({'x': car_x, 'y': car_y})

    clock = pygame.time.Clock()
    damaged_cars = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        took_damage = False
        keys = pygame.key.get_pressed()
        turning = False

        if keys[pygame.K_a] and player_x > 0:
            player_x -= cars[selected_car]["steering_speed"]
            angle += 1
            turning = True
        if keys[pygame.K_d] and player_x < WIDTH - CAR_WIDTH:
            player_x += cars[selected_car]["steering_speed"]
            angle -= 1
            turning = True

        if keys[pygame.K_w]:
            if player_speed < cars[selected_car]["top_speed"] * 1000 / 3585:
                player_speed += cars[selected_car]["acceleration"]
                if player_speed > cars[selected_car]["top_speed"] * 1000 / 3585:
                    player_speed = cars[selected_car]["top_speed"] * 1000 / 3585
                if accelerate_sound and not sound_playing:
                    accelerate_sound.play(-1)
                    sound_playing = True
            else:
                player_speed += 0.005
                if player_speed > boosted_top_speed:
                    player_speed = boosted_top_speed
        else:
            if sound_playing:
                accelerate_sound.stop()
                sound_playing = False

        if keys[pygame.K_SPACE]:
            player_speed -= 0.1
            if player_speed < 0:
                player_speed = 0
            if brake_sound:
                brake_sound.play()
        else:
            if player_speed > 0:
                brake_sound.stop()

        if not turning:
            if angle > 0:
                angle -= 3
                if angle < 0:
                    angle = 0
            elif angle < 0:
                angle += 3
                if angle > 0:
                    angle = 0

        for i, car in enumerate(other_cars):
            car_rect = pygame.Rect(car['x'], car['y'], OTHER_CAR_WIDTH, OTHER_CAR_HEIGHT)
            player_rect = pygame.Rect(player_x + 27, player_y + 27, CAR_WIDTH - 27, CAR_HEIGHT - 27)

            if player_rect.colliderect(car_rect):
                took_damage = True
                damage += 2
                if i not in damaged_cars:
                    damaged_cars.append(i)

                if player_y + CAR_HEIGHT <= car['y'] + 20:
                    player_y = car['y'] - CAR_HEIGHT
                elif player_y >= car['y'] + 20 + OTHER_CAR_HEIGHT:
                    player_y = car['y'] + OTHER_CAR_HEIGHT
                elif player_x + CAR_WIDTH <= car['x'] + 20:
                    player_x = car['x'] - CAR_WIDTH
                elif player_x >= car['x'] + 20 + OTHER_CAR_WIDTH:
                    player_x = car['x'] + OTHER_CAR_WIDTH

                print("Crashed! Damage:", damage)
                if damage >= MAX_DAMAGE:
                    print("Car is destroyed!")
                    if crash_screen():
                        damage = 0
                        main(selected_car)
                    else:
                        return
                else:
                    player_speed = 0

        damaged_cars.clear()

        for car in other_cars:
            car['y'] += (1 + player_speed * 0.48)
            if car['y'] > HEIGHT:
                lane_index = random.randint(0, NUM_LANES - 1)
                car['x'] = lane_index * LANE_WIDTH + (LANE_WIDTH - OTHER_CAR_WIDTH) // 2
                car['y'] = random.randint(-HEIGHT, 0)

        draw_road()
        draw_player_car(player_x, player_y, angle)
        draw_other_cars(other_cars)
        draw_damage_bar(damage, MAX_DAMAGE)

        speed_text = font.render(f'Speed: {int(player_speed * 3600 / 1000)} km/h', True, WHITE)
        screen.blit(speed_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    selected_car = car_selection()
    main(selected_car)
