import pygame
import json

class Sprite:
    def __init__(self, sprite, offset_x, offset_y):
        self.sprite = sprite
        self.offset_x = offset_x
        self.offset_y = offset_y

def load_sprite(path):
    sprite = pygame.image.load(f'assets/images/{path}.png')
    sprite.set_colorkey((0, 0, 0))

    return sprite

def load_sprites(path):
    sprites = pygame.image.load(f'assets/images/{path}.png')
    data = json.load(open(f'assets/images/{path}.json'))
    sprite_list = []
    for sprite_data in data['sprites']:
        sprite = get_sprite(sprites, sprite_data['x'], sprite_data['y'], sprite_data['width'], sprite_data['height'])
        sprite.set_colorkey((0, 0, 0))
        sprite_list.append(Sprite(sprite, sprite_data['offset_x'], sprite_data['offset_y']))

    return sprite_list

def load_font(path):
    sprites = pygame.image.load(f'assets/images/{path}.png')
    data = json.load(open(f'assets/images/{path}.json'))
    character_dict = {}
    for sprite_data in data['sprites']:
        sprite = get_sprite(sprites, sprite_data['x'], sprite_data['y'], sprite_data['width'], sprite_data['height'])
        sprite.set_colorkey((0, 0, 0))
        character_dict[sprite_data['character']] = sprite

    return character_dict

def get_sprite(sprites, x, y, width, height):
    sprite = pygame.Surface((width, height)).convert()
    sprite.blit(sprites, (0, 0), (x, y, width, height))

    return sprite
