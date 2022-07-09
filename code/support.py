import pygame
from csv import reader
from settings import tile_size
from os import walk

def import_csv_layput(path):
    terrain_map = []
    with open(path) as map:
        level = reader(map, delimiter= ',')
        for row in level:
            terrain_map.append(list(row))
        return terrain_map

def import_cut_graphic(path):
    surface = pygame.image.load(path).convert_alpha()
    tile_numx = int(surface.get_size()[0] / tile_size)
    tile_numy = int(surface.get_size()[1] / tile_size)

    cut_tiles = []    
    for row in range(tile_numy):
        for col in range(tile_numx):
            x = col * tile_size
            y = row * tile_size
            new_surf = pygame.Surface((tile_size, tile_size), flags = pygame.SRCALPHA)
            new_surf.blit(surface, (0,0), pygame.Rect(x,y,tile_size,tile_size))
            cut_tiles.append(new_surf)
    
    return cut_tiles

def import_folder(path):
    image_surface = []
    for _,__,image_files in walk(path):
        for images in image_files:
            full_path = path + '/' + images
            surfaces = pygame.image.load(full_path).convert_alpha()
            image_surface.append(surfaces)
    
    return image_surface