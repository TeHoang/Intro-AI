import pygame
import sys
import os
import subprocess
import threading
import math

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
HIGHLIGHT_COLOR = (255, 255, 0)

TILE_SIZE = 60
BUTTON_SIZE = TILE_SIZE * 1.5

rock_img = pygame.image.load("./asset/crate_07.png")
rock_img = pygame.transform.scale(rock_img, (TILE_SIZE, TILE_SIZE))

switch_img = pygame.image.load("./asset/switch.png")
switch_img = pygame.transform.scale(switch_img, (TILE_SIZE, TILE_SIZE))

wall_img = pygame.image.load("./asset/wall.png")
wall_img = pygame.transform.scale(wall_img, (TILE_SIZE, TILE_SIZE))

player_img = pygame.image.load("./asset/main_character.png")
player_img = pygame.transform.scale(player_img, (TILE_SIZE, TILE_SIZE))

floor_img = pygame.image.load("./asset/floor.png")
floor_img = pygame.transform.scale(floor_img, (TILE_SIZE, TILE_SIZE))

pause_button_img = pygame.image.load("./asset/pause_button.png")
pause_button_img = pygame.transform.scale(pause_button_img, (BUTTON_SIZE, BUTTON_SIZE))

play_button_img = pygame.image.load("./asset/play_button.png")
play_button_img = pygame.transform.scale(play_button_img, (BUTTON_SIZE, BUTTON_SIZE))

home_button_img = pygame.image.load("./asset/home_button.png")
home_button_img = pygame.transform.scale(home_button_img, (BUTTON_SIZE, BUTTON_SIZE))

restart_button_img = pygame.image.load("./asset/restart_button.png")
restart_button_img = pygame.transform.scale(restart_button_img, (BUTTON_SIZE, BUTTON_SIZE))
restart_button_rect = restart_button_img.get_rect(topleft=(1200 - BUTTON_SIZE * 3 - 30, 10))

menu_button_img = pygame.image.load("./asset/menu_button.png")
menu_button_img = pygame.transform.scale(menu_button_img, (BUTTON_SIZE, BUTTON_SIZE))
menu_button_rect = menu_button_img.get_rect(topleft=(1200 - BUTTON_SIZE, 10))


step_dic = {
    'l': [0, -1],
    'r': [0, 1],
    'u': [-1, 0],
    'd': [1, 0]
}

new_pos_dict = {
    'L': [0, -2],
    'R': [0, 2],
    'U': [-2, 0],
    'D': [2, 0]
}

class MainScreen:
    MAIN_SCREEN_SIZE = (800, 600)
    def __init__(self):
        self.screen_name = 'Main Screen'

    def draw(self, screen):
        screen.fill(BLUE)
        #pygame.display.set_caption(self.screen_name)

    def handle_event(self, event, screen):
        if event.type == pygame.MOUSEBUTTONUP:
            return 'play_screen'
        return None

    def get_size(self):
        return self.MAIN_SCREEN_SIZE

START_POS_X = BUTTON_SIZE + 100
START_POS_Y = BUTTON_SIZE + 50

class PlayScreen:
    def __init__(self, file_name):
        self.input_file_name = f'./input/input-{file_name}.txt'
        self.output_file_name = f'./output/output-{file_name}.txt'
        self.screen_name = 'Play Screen'
        self.font = pygame.font.Font(None, 50)
        self.PLAY_SCREEN_SIZE = (1200, 900)
        self.read_input()

        self.texts = ["BFS", "DFS", "UCS", "A*"]
        self.is_selected = [True, False, False, False]
        self.text_rects = []
        self.current_algo = 'BFS'

        for i, text in enumerate(self.texts):
            text_surface = self.font.render(text, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.PLAY_SCREEN_SIZE[0] - 70, 180 + i * 80))
            self.text_rects.append((text_surface, text_rect))

    def read_input(self):
        self.game_map = []
        self.step_count = 0
        self.sum_weight = 0

        self.stone_list = {}

        with open(self.output_file_name, 'r') as file:
                #self.sol = file.readlines()[2].strip()
                file_lines = file.readlines()
                self.sol = {}
                self.sol['BFS'] = file_lines[2].strip()
                self.sol['DFS'] = file_lines[5].strip()
                self.sol['UCS'] = file_lines[8].strip()
                self.sol['A*'] = file_lines[11].strip()

        self.current_step = 0

        self.status = {
            'running': False
        }
        self.play_button_rect = play_button_img.get_rect(topleft=(1200 - BUTTON_SIZE * 4 - 40, 10))
        self.pause_button_rect = None
        self.home_button_rect = home_button_img.get_rect(topleft=(1200 - BUTTON_SIZE * 2 - 20, 10))

        with open(self.input_file_name, 'r') as file:
            self.stone_weights = file.readline().split()
            lines = file.readlines()
            for line in lines:
                line = line.rstrip('\n')
                row_game_map = []
                for item in line:
                    row_game_map.append(list(item))
                self.game_map.append(row_game_map)    

        stone_idx = 0
        for row_index, row in enumerate(self.game_map):
            for col_index, tile in enumerate(row):
                new_tile = []
                for item in tile:
                    new_tile.append(item)
                    if item == '@':
                        self.i = row_index
                        self.j = col_index
                        new_tile.insert(0, ' ')
                    elif item == '$':
                        self.stone_list[f'{row_index}:{col_index}'] = int(self.stone_weights[stone_idx])
                        stone_idx += 1
                        new_tile.insert(0, ' ')
                    elif item == '*':
                        new_tile = ['.', '$']
                        self.stone_list[f'{row_index}:{col_index}'] = int(self.stone_weights[stone_idx])
                        stone_idx += 1
                    elif item == '+':
                        new_tile = ['.', '@']
                self.game_map[row_index][col_index] = new_tile

        my_queue = []
        my_queue.append((self.i, self.j))
        vis = set()
        vis.add(f'{self.i},{self.j}')
        dxy = [[-1, 0], [0, 1], [1, 0], [0, -1]]
        while my_queue:
            current_x = my_queue[0][0]
            current_y = my_queue[0][1]

            del my_queue[0]
            
            self.game_map[current_x][current_y].insert(0, '_')

            for dx, dy in dxy:
                new_x = current_x + dx
                new_y = current_y + dy
                if 0 <= new_x < len(self.game_map) and 0 <= new_y < len(self.game_map[new_x]):
                    if f'{new_x},{new_y}' not in vis and self.game_map[new_x][new_y][0] != '#':
                        my_queue.append((new_x, new_y))
                        vis.add(f'{new_x},{new_y}')


    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def draw(self, screen):
        screen.fill(self.hex_to_rgb('#608BC1'))
        for row_index, row in enumerate(self.game_map):
            for col_index, tile in enumerate(row):
                x = START_POS_X + col_index * TILE_SIZE
                y = START_POS_Y + row_index * TILE_SIZE
                for pic in tile:
                    if pic == '#':
                        screen.blit(wall_img, (x, y))
                    elif pic == ' ':
                        pass
                    elif pic == '$':
                        screen.blit(rock_img, (x, y))
                    elif pic == '@':
                        screen.blit(player_img, (x, y))
                    elif pic == '.':
                        screen.blit(switch_img, (x, y))
                    elif pic == '_':
                        screen.blit(floor_img, (x, y))

        step_text = self.font.render(f"Step: {self.step_count}", True, WHITE)
        screen.blit(step_text, (10, 10))

        sum_weight = self.font.render(f"Weight: {self.sum_weight}", True, WHITE)
        screen.blit(sum_weight, (10, 70))

        screen.blit(menu_button_img, (self.PLAY_SCREEN_SIZE[0] - BUTTON_SIZE, 10))

        screen.blit(home_button_img, (self.PLAY_SCREEN_SIZE[0] - BUTTON_SIZE * 2 - 20, 10))

        screen.blit(restart_button_img, (self.PLAY_SCREEN_SIZE[0] - BUTTON_SIZE * 3 - 30, 10))

        if not self.status['running']:
            screen.blit(play_button_img,  (self.PLAY_SCREEN_SIZE[0] - BUTTON_SIZE * 4 - 40, 10))
        else:
            screen.blit(pause_button_img,  (self.PLAY_SCREEN_SIZE[0] - BUTTON_SIZE * 4 - 40, 10))

        for i, (surface, rect) in enumerate(self.text_rects):
            if self.is_selected[i]:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect.inflate(10, 10))
            else:
                pygame.draw.rect(screen, GRAY, rect.inflate(10, 10))
            screen.blit(surface, rect)

        for key, value in self.stone_list.items():
            x, y = key.split(':')
            font = pygame.font.Font(None, 48)
            step_text = font.render(f"{value}", True, WHITE)
            def add_x_y(str):
                if len(str) == 1:
                    return 40
                elif len(str) == 2:
                    return 48
                elif len(str) == 3:
                    return 58
                else:
                    return 70
            screen.blit(step_text, (START_POS_X + int(y) * TILE_SIZE + (TILE_SIZE - add_x_y(str(value))), START_POS_Y +  int(x) * TILE_SIZE + (TILE_SIZE - 46)))

        pygame.display.update()

    def handle_event(self, screen):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.home_button_rect.collidepoint(mouse_pos):
                    return 'menu_screen'
                elif menu_button_rect.collidepoint(mouse_pos):
                    pass
                elif self.play_button_rect is not None and self.play_button_rect.collidepoint(mouse_pos):
                    self.play_button_rect = None
                    self.pause_button_rect = pause_button_img.get_rect(topleft=(1200 - BUTTON_SIZE * 4 - 40, 10))
                    self.status['running'] = True
                elif self.pause_button_rect is not None and self.pause_button_rect.collidepoint(mouse_pos):
                    self.pause_button_rect = None
                    self.play_button_rect = play_button_img.get_rect(topleft=(1200 - BUTTON_SIZE * 4 - 40, 10))
                    self.status['running'] = False
                elif restart_button_rect.collidepoint(mouse_pos):
                    self.read_input()
                    pass
                else:
                    for i, (_, rect) in enumerate(self.text_rects):
                        if rect.collidepoint(event.pos):
                            self.is_selected = [False] * 4
                            self.is_selected[i] = not self.is_selected[i]
                            self.current_algo = self.texts[i]
                            self.read_input()
                self.draw(screen)
                

        if self.status['running']:
            if self.current_step < len(self.sol[self.current_algo]):
                step = self.sol[self.current_algo][self.current_step]

                next_i = self.i + step_dic[step.lower()][0]
                next_j = self.j + step_dic[step.lower()][1]

                if step.isupper():
                    del self.game_map[next_i][next_j][-1]
                    self.game_map[self.i + new_pos_dict[step][0]][self.j + new_pos_dict[step][1]].append('$')
                    self.sum_weight += self.stone_list[f'{next_i}:{next_j}']
                    self.stone_list[f'{self.i + new_pos_dict[step][0]}:{self.j + new_pos_dict[step][1]}'] = self.stone_list[f'{next_i}:{next_j}']
                    del self.stone_list[f'{next_i}:{next_j}']
                # else:
                #     self.sum_weight += 1

                del self.game_map[self.i][self.j][-1]
                self.game_map[next_i][next_j].append('@')

                self.i = next_i
                self.j = next_j

                self.step_count += 1
                self.current_step += 1

                self.draw(screen)
                pygame.time.delay(100)
        return None

    def get_size(self):
        return self.PLAY_SCREEN_SIZE

class MenuScreen:
    def __init__(self):
        self.ROWS = 5
        self.COLS = 5
        self.MENU_SCREEN_SIZE = (600, 600)
        self.font = pygame.font.Font(None, 36)
        self.selected_index = 0
        self.CELL_SIZE = self.MENU_SCREEN_SIZE[0] // self.ROWS
        self.maps = []
        for i in range(1,26):
            self.maps.append(f'Map {i}')


    def draw(self, screen, *other):
        for i in range(self.ROWS ):
            for j in range(self.COLS):
                # Vẽ ô
                rect = pygame.Rect(j * self.CELL_SIZE, i * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)
                # Vẽ chữ
                font = pygame.font.Font(None, 36)
                text = self.font.render(self.maps[i * self.ROWS + j], True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)

    def run_main_py(self):
        with open(f'./input/input-{self.index}.txt', 'r') as file:
            data = file.readlines()
        data_string = ''.join(data)
        result = subprocess.run([sys.executable, "main.py"], input=data_string, text=True, capture_output=True)
        self.result_output = result.stdout.strip() 
        self.running = False

    def handle_event(self, screen):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                row = mouse_y // self.CELL_SIZE
                col = mouse_x // self.CELL_SIZE
                index = row * self.ROWS + col
                self.index = index + 1

                loading_screen = pygame.display.set_mode((600, 400))
                clock = pygame.time.Clock()

                center_x, center_y = loading_screen.get_width() // 2, loading_screen.get_height() // 2
                radius = 50
                angle = 0

                self.running = True
                x = True
                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:   
                            pygame.quit()
                            sys.exit()
                    if self.running == False:
                        break

                    if x == True:
                        x = False
                        threading.Thread(target=self.run_main_py).start()
                    loading_screen.fill((30, 30, 30))
                    x = center_x + radius * math.cos(angle)
                    y = center_y + radius * math.sin(angle)


                    pygame.draw.circle(loading_screen, (255, 255, 255), (int(x), int(y)), 10)


                    angle += 0.1
                    if angle >= 2 * math.pi:
                        angle -= 2 * math.pi

                    pygame.display.flip()
                    clock.tick(60)
                
                with open(f'./output/output-{self.index}.txt', 'w') as file:
                    file.write(self.result_output)

                return 'play_screen'

    def get_size(self):
        return self.MENU_SCREEN_SIZE

    def get_file_name(self):
        return self.index

def main():
    menu_screen = MenuScreen()
    current_screen = menu_screen
    screen = pygame.display.set_mode(current_screen.get_size())
    pygame.display.set_caption('Game Menu')

    while True:
        current_screen.draw(screen)
        pygame.display.update()
        while True:
            result = current_screen.handle_event(screen)
            if result:
                break
        if result == 'main_screen':
            current_screen = MainScreen()
            screen = pygame.display.set_mode(current_screen.get_size())
        elif result == 'play_screen':
            current_screen = PlayScreen(current_screen.get_file_name())
            screen = pygame.display.set_mode(current_screen.get_size())
            pygame.display.set_caption('Play Screen')
        elif result == 'menu_screen':
            current_screen = menu_screen
            screen = pygame.display.set_mode(current_screen.get_size())
            pygame.display.set_caption('Main menu')

if __name__ == "__main__":
    main()