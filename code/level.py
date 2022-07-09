import pygame
from support import import_csv_layput, import_cut_graphic
from settings import tile_size, screen_height, screen_width
from tiles import Tile, StaticTile, Crate, Coin, Palm
from enemy import Enemy
from decoration import Sky, Water, Cloud
from player import Player 
from particles import ParticleEffect
from game_data import levels

class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health):
        #general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None
        
        #overworld
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data['unlock']
        
        #player 
        player_layout = import_csv_layput(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal= pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)
        
        #UI
        self.change_coins = change_coins
        
        #dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False
        
        #explosion 
        self.explosion_sprites = pygame.sprite.Group()
        
        #terrain setup
        terrain_layout = import_csv_layput(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        
        #grass setup
        grass_layout = import_csv_layput(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')
        
        #crates
        crate_layout = import_csv_layput(level_data['crates'])
        self.crate_sprites = self.create_tile_group(crate_layout, 'crate')
        
        #coins
        coin_layout = import_csv_layput(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')
        
        #fg palm trees
        fg_palms_layout = import_csv_layput(level_data['fg palms'])
        self.fg_palms_sprites = self.create_tile_group(fg_palms_layout, 'fg palms')
        
        #bg palms 
        bg_palms_layout = import_csv_layput(level_data['bg palms'])
        self.bg_palms_sprites = self.create_tile_group(bg_palms_layout, 'bg palms')
        
        #enemy
        enemy_layout = import_csv_layput(level_data['enemies'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemies')
        
        #coonstrain
        constraint_layout = import_csv_layput(level_data['constraints'])
        self.constraint_sprites = self.create_tile_group(constraint_layout, 'constraints')
        
        #decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 40, level_width)
        self.clouds = Cloud(400, level_width, 30)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()
        
        for row_index,row in enumerate(layout):
                for col_index, val in enumerate(row):
                    if val != '-1':
                        x = col_index * tile_size
                        y = row_index * tile_size
                        
                        if type == 'terrain':
                            terrain_tile_list = import_cut_graphic('graphics/terrain/terrain_tiles.png')
                            tile_surface = terrain_tile_list[int(val)]
                            sprite = StaticTile(tile_size,x,y, tile_surface)
                            
                        if type == 'grass':
                            grass_tile_list = import_cut_graphic('graphics/decoration/grass/grass.png')
                            tile_surface = grass_tile_list[int(val)]
                            sprite = StaticTile(tile_size,x,y, tile_surface)
                        
                        if type == 'crate':
                            sprite = Crate(tile_size,x,y)
                            
                        if type == 'coins':
                            if val == '0':
                                sprite = Coin(tile_size,x,y,'graphics/coins/gold', 5)
                            if val == '1':
                                sprite = Coin(tile_size,x,y,'graphics/coins/silver', 1)
                        
                        if type == 'fg palms':
                            if val == '0': 
                                sprite = Palm(tile_size,x,y,'graphics/terrain/palm_small', 40)
                            if val == '1': 
                                sprite = Palm(tile_size,x,y,'graphics/terrain/palm_large', 72)
                        
                        if type == 'bg palms':
                            sprite = Palm(tile_size,x,y,'graphics/terrain/palm_bg', 62)
                        
                        if type == 'enemies':
                            sprite = Enemy(tile_size,x,y)
                        
                        if type == 'constraints':
                            sprite = Tile(tile_size,x,y)
                        
                        sprite_group.add(sprite)

        return sprite_group
    
    def player_setup(self, layout, change_health):
        for row_index,row in enumerate(layout):
                for col_index, val in enumerate(row):
                    x = col_index * tile_size
                    y = row_index * tile_size
                    if val == '0':
                        sprite = Player((x,y), self.display_surface, self.create_jump_particles, change_health)
                        self.player.add(sprite)
                    if val == '1':
                        hat_surface = pygame.image.load('graphics/character/hat.png').convert_alpha()
                        sprite = StaticTile(tile_size,x,y,hat_surface)
                        self.goal.add(sprite)
    
    def enemy_collision_reversal(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()
    
    def create_jump_particles(self,pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10,5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos,'jump')
        self.dust_sprite.add(jump_particle_sprite)
    
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False
    
    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10,15)
            else:
                offset = pygame.math.Vector2(10,15)
                
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)
    
    def horizontal_movement_collision(self):
        player = self.player.sprite  
        player.collision_rect.x += player.direction.x * player.speed
        collidable = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palms_sprites.sprites()
        
        for sprite in collidable:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
               
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True
                             
    def vertical_movement_collision(self):
        player = self.player.sprite  
        player.apply_gravity()
        collidable = self.terrain_sprites.sprites() + self.crate_sprites.sprites() + self.fg_palms_sprites.sprites()
        
        for sprite in collidable:
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0 
                    player.on_ceiling = True
            
            if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
                player.on_ground = False
    
    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x
        
        if player_x < screen_width // 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - screen_width // 4 and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8
    
    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)
            
    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)
    
    def check_coin_col(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(coin.value)

    def check_enemy_col(self):
        enemy_collision = pygame.sprite.spritecollide(self.player.sprite,self.enemy_sprites, False)

        if enemy_collision:
            for enemy in enemy_collision:
               enemy_center = enemy.rect.centery
               enemy_top = enemy.rect.top 
               player_bottom = self.player.sprite.rect.bottom
               if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                   self.player.sprite.direction.y = -15
                   explosion_sprite = ParticleEffect(enemy.rect.center,'explosion')
                   self.explosion_sprites.add(explosion_sprite)
                   enemy.kill()
               else:
                   self.player.sprite.get_damage()
    
    def run(self):
        #run the entire game / level
        
        #skd
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)
        
        #bg palm
        self.bg_palms_sprites.update(self.world_shift)
        self.bg_palms_sprites.draw(self.display_surface)
        
        #dust shit
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)
        
        #terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        
        #enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reversal()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)
        
        #crate
        self.crate_sprites.update(self.world_shift)
        self.crate_sprites.draw(self.display_surface)
        
        #grass
        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)
        
        # coins
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)
        
        #fg palm
        self.fg_palms_sprites.update(self.world_shift)
        self.fg_palms_sprites.draw(self.display_surface)
        
        
        #player sprite
        self.player.update()
        self.horizontal_movement_collision()
        
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)
        
        self.check_death()
        self.check_win()
        self.check_coin_col()
        self.check_enemy_col()
        
        #camera
        self.scroll_x()
        
        #water 
        self.water.draw(self.display_surface, self.world_shift)
         
        