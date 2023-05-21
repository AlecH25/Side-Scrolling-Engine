import math
import json
import pygame.draw

def init_camera(p_camera):
    global camera

    camera = p_camera

class Camera:
    def __init__(self, position):
        self.x, self.y = position
        self.true_x, self.true_y = int(self.x), int(self.y)

class Entity:
    def __init__(self, rect):
        self.x, self.y, self.width, self.height = rect
        self.true_x, self.true_y = int(self.x), int(self.y)

    def render_rect(self, surface, color):
        rect = pygame.Rect(self.x - camera.x, self.y - camera.y, self.width, self.height)
        pygame.draw.rect(surface, color, rect, 1)

class Particle:
    def __init__(self, rect, velocity_x, velocity_y, gravity_x, gravity_y, max_velocity_y, rotation, rotation_velocity, spawn_time, lifespan):
        self.x, self.y, self.width, self.height = rect
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.gravity_x = gravity_x
        self.gravity_y = gravity_y
        self.max_velocity_y = max_velocity_y
        self.rotation = rotation
        self.rotation_velocity = rotation_velocity
        self.spawn_time = spawn_time
        self.lifespan = lifespan

class Chunk:
    def __init__(self, position, chunk):
        self.x, self.y = position
        self.chunk = chunk

def load_level(path):
    global level

    level = json.load(open('levels/' + path + '.json'))

def render_level(surface, tileset, db_tiles=False, db_chunks=False):
    for chunk in chunks:
        chunk_x = int(chunk.x) * chunk_pixels
        chunk_y = int(chunk.y) * chunk_pixels
        y = chunk_y
        for row in chunk.chunk['chunk']:
            x = chunk_x
            for tile in row:
                if tile > 0:
                    tile_sprite = tileset[tile - 1]
                    tile_x = x - camera.x
                    tile_y = y - camera.y
                    surface.blit(tile_sprite.sprite, (tile_x + tile_sprite.offset_x, tile_y + tile_sprite.offset_y))
                    if db_tiles:
                        pygame.draw.rect(surface, (255, 255, 255), pygame.Rect(tile_x, tile_y, tile_size, tile_size), 1)
                x += tile_size
            y += tile_size
        if db_chunks:
            pygame.draw.rect(surface, (0, 0, 255), pygame.Rect(chunk_x - camera.x, chunk_y - camera.y, chunk_pixels, chunk_pixels), 1)

def load_chunks(surface):
    global chunks, objects

    chunks = []
    objects = []
    for y in range(math.ceil(surface.get_height() / chunk_pixels) + 1):
        for x in range(math.ceil(surface.get_width() / chunk_pixels) + 1):
            chunk_x = x - 1 + math.ceil(camera.x / chunk_pixels)
            chunk_y = y - 1 + math.ceil(camera.y / chunk_pixels)
            chunk = f'{chunk_x}, {chunk_y}'
            if chunk in level:
                chunks.append(Chunk((chunk_x, chunk_y), level[chunk]))
                if 'objects' in level[chunk]:
                    for object in level[chunk]['objects']:
                        objects.append(object)

def load_rects():
    global rects

    rects = []
    for chunk in chunks:
        y = int(chunk.y) * chunk_pixels
        for row in chunk.chunk['chunk']:
            x = int(chunk.x) * chunk_pixels
            for tile in row:
                if tile > 0:
                    rects.append(pygame.Rect(x, y, tile_size, tile_size))
                x += 16
            y += 16

def collided(entity):
    for rect in rects:
        entity_rect = pygame.Rect(entity.x, entity.y, entity.width, entity.height)
        if entity_rect.colliderect(rect):
            return True
    return False
