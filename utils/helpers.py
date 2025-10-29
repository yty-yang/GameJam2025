import pygame

def draw_rect(screen, color, x, y, width, height):
    pygame.draw.rect(screen, color, pygame.Rect(x, y, width, height))