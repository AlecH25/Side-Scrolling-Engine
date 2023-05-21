import pygame
import sys
import time
import math
import engine
import sprites
import text

# INIT ================>
pygame.init()

pygame.mixer.pre_init(44100, 16, 2, 4096)
pygame.mixer.set_num_channels(32)
pygame.mixer.init()

display = pygame.Surface((384, 216))
window = pygame.display.set_mode((960, 540))
pygame.display.set_caption("Side Scrolling Engine")

pygame.mouse.set_visible(False)

# SPRITES ================>
cursor = sprites.load_sprites('cursor')

player_idle = sprites.load_sprites('player/idle')
player_run = sprites.load_sprites('player/run')

rifle = sprites.load_sprites('weapons/rifle')
shotgun = sprites.load_sprites('weapons/shotgun')
bullet_sprite = sprites.load_sprites('weapons/bullet')

tileset = sprites.load_sprites('tileset')
grass = sprites.load_sprites('nature/grass')
tree = sprites.load_sprites('nature/tree')

# SOUNDS ================>
def load_sound(path, volume=1.0):
    sound = pygame.mixer.Sound('assets/sounds/' + path + '.wav')
    sound.set_volume(volume)

    return sound

# VARIABLES ================>
framerate = 60
fullscreen = False
debug = False

editor = False

engine.camera = engine.Camera((0, 0))
engine.tile_size = 16
engine.chunk_size = 8
engine.chunk_pixels = 128

true_camera = pygame.Vector2(0, 0)
player = engine.Entity((0, -23, 10, 23))
player.velocity_x = 0
player.velocity_y = 0
player.gravity = 0.33
player.max_velocity = 6
player.grounded = True
player.flipped = True
player.frame = 0
player.frame_time = time.time()

weapon = "shotgun"
if weapon == "rifle":
    max_clip = 30
elif weapon == "shotgun":
    max_clip = 2
clip = max_clip
ammo = 999
bullets = []
particles = []

engine.load_level('level')

last_time = time.time()

def main():
    global clock, delta_time, last_time, fullscreen, window, debug, editor, brush_type, brush_index, ammo, clip, keys_pressed, mouse

    clock = pygame.time.Clock()

    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT])
    while True:
        delta_time = (time.time() - last_time) * 60
        last_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_f:
                    if fullscreen:
                        fullscreen = False
                        pygame.display.set_mode((960, 540), pygame.OPENGL | pygame.DOUBLEBUF)
                    else:
                        fullscreen = True
                        pygame.display.set_mode((1920, 1080), pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)
                elif event.key == pygame.K_TAB:
                    if debug:
                        debug = False
                    else:
                        debug = True
                elif event.key == pygame.K_e:
                    if editor:
                        editor = False
                    else:
                        editor = True
                        brush_type = 1
                        brush_index = 1
                if editor:
                    if event.key == pygame.K_t:
                        brush_type = 1
                        brush_index = 1
                    elif event.key == pygame.K_o:
                        brush_type = 2
                        brush_index = 1
                    elif event.key == pygame.K_MINUS:
                        brush_index -= 1
                        if brush_index < 1:
                            if brush_type == 1:
                                brush_index = len(tileset)
                            elif brush_type == 2:
                                brush_index = 7
                    elif event.key == pygame.K_EQUALS:
                        brush_index += 1
                        if brush_type == 1:
                            if brush_index > len(tileset):
                                brush_index = 1
                        elif brush_type == 2:
                            if brush_index > 7:
                                brush_index = 1
                else:
                    if event.key == pygame.K_w and player.grounded:
                        player.velocity_y = -6
                        player.grounded = False
                    elif event.key == pygame.K_r and ammo > 0 and clip < max_clip:
                        ammo -= 1
                        clip += 1
                        x = weapon_x - player.width / 2 - math.sin(weapon_angle) * rifle[0].sprite.get_width() / 2
                        y = weapon_y - rifle[0].sprite.get_height() / 2 - math.cos(weapon_angle) * rifle[0].sprite.get_width() / 2
                        if player.flipped:
                            x += math.sin(weapon_angle) * rifle[0].sprite.get_width() / 4
                        else:
                            x += math.sin(weapon_angle) * rifle[0].sprite.get_width() / 2
                        y += math.cos(weapon_angle) * rifle[0].sprite.get_width() / 4
                        if player.flipped:
                            gravity_x = 0.1
                            rotation_velocity = 5
                        else:
                            gravity_x = -0.1
                            rotation_velocity = -5
                        shell = engine.Particle((x, y, 3, 3), math.sin(weapon_angle) * 3.33, -1, gravity_x, 0.25, 6.66, math.degrees(weapon_angle) + 90, rotation_velocity, time.time(), 3)
                        shell.collidied = False
                        particles.append(shell)
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys_pressed = pygame.key.get_pressed()

        mouse = pygame.Vector2(pygame.mouse.get_pos())
        mouse.x /= window.get_width() / display.get_width()
        mouse.y /= window.get_height() / display.get_height()

        engine.load_chunks(display)
        engine.load_rects()
        if editor:
            tick_editor()
        else:
            move_player()
            animate_player()
            tick_weapon()
            tick_particles()
        move_camera()
        render_display()
        render_window()

        clock.tick(framerate)

def tick_editor():
    global brush, brush_mode, brush_pressed

    brush = pygame.Vector2()
    brush.x = math.floor((mouse.x + engine.camera.x) / engine.tile_size) * engine.tile_size
    brush.y = math.floor((mouse.y + engine.camera.y) / engine.tile_size) * engine.tile_size

    if pygame.mouse.get_pressed()[0]:
        chunk = pygame.Vector2()
        chunk.x = math.floor((mouse.x + engine.camera.x) / engine.chunk_pixels)
        chunk.y = math.floor((mouse.y + engine.camera.y) / engine.chunk_pixels)

        tile = pygame.Vector2()
        tile.x = math.floor((mouse.x + engine.camera.x) / engine.tile_size) % engine.chunk_size
        tile.y = math.floor((mouse.y + engine.camera.y) / engine.tile_size) % engine.chunk_size

        target_chunk = f'{int(chunk.x)}, {int(chunk.y)}'
        if target_chunk not in engine.level:
            engine.level[target_chunk] = {"chunk": [[0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                                    [0, 0, 0, 0, 0, 0, 0, 0]],
                                          "objects": []
                                          }
        if brush_type == 1:
            if brush_mode == 0:
                if engine.level[target_chunk]['chunk'][int(tile.y)][int(tile.x)] != brush_index:
                    brush_mode = 1
                else:
                    brush_mode = -1
            if brush_mode == 1:
                engine.level[target_chunk]['chunk'][int(tile.y)][int(tile.x)] = brush_index
            elif brush_mode == -1 and brush_index == engine.level[target_chunk]['chunk'][int(tile.y)][int(tile.x)]:
                engine.level[target_chunk]['chunk'][int(tile.y)][int(tile.x)] = 0
        elif brush_type == 2 and not brush_pressed:
            if brush_index in range(1, 7):
                object = "grass"
                type = brush_index - 1
            elif brush_index == 7:
                object = "tree"
                type = 0
            if 'objects' not in engine.level[target_chunk]:
                engine.level[target_chunk]['objects'] = []
            engine.level[target_chunk]['objects'].append({"x": mouse.x + engine.camera.x, "y": mouse.y + engine.camera.y, "object": object, "type": type})
            brush_pressed = True
    else:
        brush_mode = 0
        brush_pressed = False

def move_player():
    player.true_x += player.velocity_x
    player.x = int(player.true_x)
    if keys_pressed[pygame.K_a]:
        player.true_x -= 2.5 * delta_time
        player.x = int(player.true_x)
    while engine.collided(player):
        player.true_x += 1
        player.x = int(player.true_x)
    if keys_pressed[pygame.K_d]:
        player.true_x += 2.5 * delta_time
        player.x = int(player.true_x)
    while engine.collided(player):
        player.true_x -= 1
        player.x = int(player.true_x)

    if not player.grounded:
        player.velocity_y += player.gravity * delta_time
        if player.velocity_y > player.max_velocity:
            player.velocity_y = player.max_velocity
        player.true_y += player.velocity_y * delta_time
        player.y = int(player.true_y)
        if engine.collided(player):
            y = abs(player.velocity_y) / player.velocity_y
            while engine.collided(player):
                player.true_y -= y
                player.y = int(player.true_y)
            player.velocity_x = 0
            player.velocity_y = 0
            player.grounded = True
    else:
        player.y += 1
        if not engine.collided(player):
            player.grounded = False
        player.y -= 1

def animate_player():
    if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_d]:
        player.animation = "run"
    else:
        player.animation = "idle"
        player.frame = 0

    if player.animation == "run":
        player.sprites = player_run
        if player.frame in (0, 2, 3):
            if time.time() - player.frame_time >= 0.016 * 4:
                player.frame += 1
                if player.frame == 4:
                    player.frame = 0
                player.frame_time = time.time()
        elif player.frame == 1:
            if time.time() - player.frame_time >= 0.016 * 6:
                player.frame += 1
                if player.frame == 4:
                    player.frame = 0
                player.frame_time = time.time()

    if player.animation == "idle":
        player.sprites = player_idle

def tick_weapon():
    global weapon_x, weapon_y, weapon_angle, clip, mouse_pressed

    weapon_x = player.x + player.width / 2
    weapon_y = player.y + player.height / 2
    weapon_angle = math.atan2(weapon_x - mouse.x - engine.camera.x, weapon_y - mouse.y - engine.camera.y)

    if pygame.mouse.get_pressed()[0]:
        if weapon == "shotgun":
            if clip > 0 and not mouse_pressed:
                x = weapon_x - player.width / 2 - math.sin(weapon_angle) * shotgun[0].sprite.get_width() / 2
                y = weapon_y - shotgun[0].sprite.get_height() / 2 - math.cos(weapon_angle) * rifle[0].sprite.get_width() / 2
                bullet = engine.Entity((x, y, 8, 8))
                bullet.angle = weapon_angle + 270
                bullet.spawn_time = time.time()
                bullets.append(bullet)

                bullet = engine.Entity((x, y, 8, 8))
                bullet.angle = weapon_angle
                bullet.spawn_time = time.time()
                bullets.append(bullet)

                bullet = engine.Entity((x, y, 8, 8))
                bullet.angle = weapon_angle - 270
                bullet.spawn_time = time.time()
                bullets.append(bullet)

                clip -= 1

                player.velocity_x = math.sin(bullet.angle) * 2
                player.velocity_y = math.cos(bullet.angle) * 6
                player.grounded = False

                mouse_pressed = True
        elif weapon == "rifle":
            pass
    else:
        mouse_pressed = False

    for bullet in bullets:
        if time.time() - bullet.spawn_time > 3:
            bullets.remove(bullet)
        bullet.x -= math.sin(bullet.angle) * 10 * delta_time
        bullet.y -= math.cos(bullet.angle) * 10 * delta_time
        if engine.collided(bullet):
            bullets.remove(bullet)

def tick_particles():
    for particle in particles:
        if time.time() - particle.spawn_time > particle.lifespan:
            particles.remove(particle)
        if not particle.collidied:
            particle.velocity_x += particle.gravity_x * delta_time
            particle.x += particle.velocity_x * delta_time
            particle.velocity_y += particle.gravity_y * delta_time
            if particle.velocity_y > particle.max_velocity_y:
                particle.velocity_y = particle.max_velocity_y
            particle.y += particle.velocity_y * delta_time
            particle.rotation += particle.rotation_velocity
        if engine.collided(engine.Entity((particle.x, particle.y, particle.width, particle.height))):
            particle.velocity_x = 0
            particle.velocity_y = 0
            particle.rotation = 0
            particle.collidied = True

def move_camera():
    if editor:
        if keys_pressed[pygame.K_w]:
            engine.camera.true_y -= 2.5 * delta_time
        if keys_pressed[pygame.K_a]:
            engine.camera.true_x -= 2.5 * delta_time
        if keys_pressed[pygame.K_s]:
            engine.camera.true_y += 2.5 * delta_time
        if keys_pressed[pygame.K_d]:
            engine.camera.true_x += 2.5 * delta_time

        engine.camera.x = int(engine.camera.true_x)
        engine.camera.y = int(engine.camera.true_y)
    else:
        engine.camera.true_x += (player.x - engine.camera.x - display.get_width() / 2 + int(player.width / 2)) / 16 * delta_time
        engine.camera.true_y += (player.y - engine.camera.y - display.get_height() / 2 + int(player.height / 2)) / 16 * delta_time
        engine.camera.x = int(engine.camera.true_x)
        engine.camera.y = int(engine.camera.true_y)

def render_display():
    display.fill((30, 29, 57))
    direction = math.degrees(weapon_angle) + 90
    if direction > 90:
        weapon_sprite = pygame.transform.flip(shotgun[0].sprite, False, True)
        player.flipped = False
    else:
        weapon_sprite = shotgun[0].sprite
        player.flipped = True
    player_sprite = player.sprites[player.frame]
    display.blit(pygame.transform.flip(player_sprite.sprite, player.flipped, False), (player.x - engine.camera.x + player_sprite.offset_x, player.y - engine.camera.y + player_sprite.offset_y))
    weapon_sprite = pygame.transform.rotate(weapon_sprite, direction)
    x = weapon_x - weapon_sprite.get_width() / 2 - engine.camera.x
    y = weapon_y - weapon_sprite.get_height() / 2 - engine.camera.y
    display.blit(weapon_sprite, (x, y))
    for bullet in bullets:
        display.blit(pygame.transform.rotate(bullet_sprite[0].sprite, math.degrees(bullet.angle) + 90), (bullet.x - engine.camera.x, bullet.y - engine.camera.y))
        if debug:
            bullet.render_rect(display, (255, 255, 0))
    for particle in particles:
        particle_sprite = pygame.transform.rotate(shotgun[1].sprite, particle.rotation)
        display.blit(particle_sprite, (particle.x - engine.camera.x, particle.y - engine.camera.y))
    if debug:
        player.render_rect(display, (0, 255, 0))
        engine.render_level(display, tileset, db_tiles=True, db_chunks=True)
    else:
        engine.render_level(display, tileset)
    render_objects()
    if editor:
        if brush_type == 1:
            tile_sprite = tileset[brush_index - 1]
            display.blit(tile_sprite.sprite, (brush.x - engine.camera.x + tile_sprite.offset_x, brush.y - engine.camera.y + tile_sprite.offset_y))
            pygame.draw.rect(display, (255, 255, 255), pygame.Rect(brush.x - engine.camera.x, brush.y - engine.camera.y, engine.tile_size, engine.tile_size), 1)
        elif brush_type == 2:
            if brush_index in range(1, 7):
                object_sprite = grass[brush_index - 1]
                offset_x = object_sprite.sprite.get_width() / 2 * -1
                offset_y = object_sprite.sprite.get_height() / 2 * -1
            elif brush_index == 7:
                object_sprite = tree[0]
                offset_x = object_sprite.offset_x
                offset_y = object_sprite.offset_y
            display.blit(object_sprite.sprite, (mouse.x + offset_x, mouse.y + offset_y))
    else:
        display.blit(cursor[0].sprite, (mouse.x - cursor[0].offset_x, mouse.y - cursor[0].offset_y))
    text.render(display, (255, 255, 255), f"fps: {round(clock.get_fps())}", 'assets/images/m3x6.ttf', 16, (1, -4))
    text.render(display, (255, 255, 255), f"delta_time: {round(delta_time, 1)}", 'assets/images/m3x6.ttf', 16, (1, 6))
    text.render(display, (255, 255, 255), f"{clip}/{max_clip} | {ammo}", 'assets/images/m3x6.ttf', 16, (1, 203))

def render_objects():
    for object in engine.objects:
        if object['object'] == "grass":
            player_vector = pygame.Vector2(player.x, player.y)
            grass_vector = pygame.Vector2(object['x'], object['y'])
            distance = player_vector.distance_to(grass_vector) - player.height
            relative_x = player.x - object['x'] + player.width / 2
            if distance < player.width / 2:
                if relative_x <= 0:
                    angle = -72 - relative_x * 2.5
                elif relative_x >= 0:
                    angle = 72 - relative_x * 2.5
                else:
                    angle = 0
            else:
                angle = 0
            if 'angle' not in object:
                object['angle'] = 0
            object['angle'] += (angle - object['angle']) / 4 * delta_time
            grass_sprite = pygame.transform.rotate(grass[object['type']].sprite, object['angle'])
            x = object['x'] - engine.camera.x + grass[object['type']].offset_x - grass_sprite.get_width() / 2
            y = object['y'] - engine.camera.y + grass[object['type']].offset_y - grass_sprite.get_height() / 2
            display.blit(grass_sprite, (x, y))
        elif object['object'] == "tree":
            display.blit(tree[0].sprite, (object['x'] - engine.camera.x + tree[0].offset_x, object['y'] - engine.camera.y + tree[0].offset_y))
        if debug:
            pygame.draw.rect(display, (255, 0, 0), pygame.Rect(object['x'] - engine.camera.x - 1, object['y'] - engine.camera.y - 1, 3, 3))

def render_window():
    window.blit(pygame.transform.scale(display, window.get_size()), (0, 0))
    pygame.display.flip()

if __name__ == "__main__":
    start_time = time.time()
    main()
