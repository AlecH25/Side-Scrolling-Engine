import pygame

pygame.font.init()

def render(surface, color, text, font, size, position):
    loaded_font = pygame.font.Font(font, size)
    rendered_text = loaded_font.render(text, True, pygame.Color(color))
    surface.blit(rendered_text, position)

def render_centered(surface, color, text, font, size, position):
    loaded_font = pygame.font.Font(font, size)
    rendered_text = loaded_font.render(text, True, pygame.Color(color))
    text_rect = rendered_text.get_rect()
    x = position[0] - text_rect.width / 2
    y = position[1] - text_rect.height / 2
    surface.blit(rendered_text, (x, y))
