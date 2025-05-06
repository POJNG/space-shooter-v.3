import pygame 
from os.path import join
from random import randint, uniform

class BaseSprite(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # cooldown 
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 200

        # health system
        self.health = 3
        self.max_health = 3
        self.invincible = False
        self.invincible_time = 0
        self.invincible_duration = 1000

        # mask 
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time >= self.invincible_duration:
                self.invincible = False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])  
        self.direction = self.direction.normalize() if self.direction else self.direction 
        
        # Update position with screen boundaries
        new_pos = self.rect.center + self.direction * self.speed * dt
        new_pos.x = max(0, min(new_pos.x, WINDOW_WIDTH))
        new_pos.y = max(0, min(new_pos.y, WINDOW_HEIGHT))
        self.rect.center = new_pos

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites)) 
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()
        self.invincibility_timer()

class Star(BaseSprite):
    def __init__(self, surf, groups):
        pos = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT))
        super().__init__(surf, pos, groups)

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(BaseSprite):
    def __init__(self, surf, pos, groups):
        super().__init__(surf, pos, groups)
        self.speed = randint(200, 300)
        self.rotation_speed = randint(20, 40)
        self.rotation = 0
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        # Only kill when meteor goes below the screen
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class GameOver:
    def __init__(self, score):
        self.score = score
        self.font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
        self.small_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 30)
        self.alpha = 0
        self.fade_speed = 2
        
        # Load high score
        try:
            with open('highscore.txt', 'r') as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0
        
        # Update high score if needed
        if self.score > self.high_score:
            self.high_score = self.score
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        
    def update(self):
        if self.alpha < 255:
            self.alpha += self.fade_speed
            
    def draw(self, surface):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill('#3a2e3f')
        overlay.set_alpha(self.alpha)
        surface.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, (240, 240, 240))
        game_over_rect = game_over_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        surface.blit(game_over_text, game_over_rect)
        
        # Score text
        score_text = self.font.render(f"Score: {self.score}", True, (240, 240, 240))
        score_rect = score_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
        surface.blit(score_text, score_rect)
        
        # High Score text
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, (240, 240, 240))
        high_score_rect = high_score_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        surface.blit(high_score_text, high_score_rect)
        
        # Restart instruction
        restart_text = self.small_font.render("Press R to Restart", True, (200, 200, 200))
        restart_rect = restart_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 160))
        surface.blit(restart_text, restart_rect)

def collisions():
    global running, game_over, game_over_screen

    if not player.invincible:
        collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, False, pygame.sprite.collide_mask)
        if collision_sprites:
            player.health -= 1
            player.invincible = True
            player.invincible_time = pygame.time.get_ticks()
            for meteor in collision_sprites:
                meteor.kill()
                AnimatedExplosion(explosion_frames, meteor.rect.center, all_sprites)
            if player.health <= 0:
                game_over = True
                final_score = (pygame.time.get_ticks() - start_time) // 100
                game_over_screen = GameOver(final_score)
    
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

def display_pause_menu():
    pause_text = font.render("PAUSED", True, (240, 240, 240))
    pause_rect = pause_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
    resume_text = font.render("Press ESC to Resume", True, (200, 200, 200))
    resume_rect = resume_text.get_frect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
    display_surface.blit(pause_text, pause_rect)
    display_surface.blit(resume_text, resume_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), pause_rect.inflate(40, 20), 5, 10)

def display_score():
    if paused:
        current_time = pause_time
    elif game_over:
        current_time = game_over_screen.score
    else:
        current_time = (pygame.time.get_ticks() - start_time) // 100
    text_surf = font.render(str(current_time), True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def display_health():
    for i in range(player.max_health):
        color = (240, 240, 240) if i < player.health else (100, 100, 100)
        pygame.draw.circle(display_surface, color, (30 + i * 40, 30), 15)

# general setup 
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space shooter')
running = True
paused = False
game_over = False
game_over_screen = None
pause_time = 0
start_time = pygame.time.get_ticks()
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.1)
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.01)
game_music.play()

# sprites 
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(star_surf, all_sprites) 
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:
    dt = clock.tick() / 1000
    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not game_over:
                paused = not paused
                if paused:
                    pause_time = (pygame.time.get_ticks() - start_time) // 100
                    game_music.stop()
                else:
                    game_music.play(-1)
            if event.key == pygame.K_r and game_over:
                # Reset game state
                game_over = False
                game_over_screen = None
                player.health = player.max_health
                start_time = pygame.time.get_ticks()  # Reset the start time
                pause_time = 0
                for sprite in all_sprites:
                    if sprite != player:
                        sprite.kill()
                for i in range(20):
                    Star(star_surf, all_sprites)
                game_music.play(-1)
        if not paused and not game_over and event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
    
    # update
    if not paused and not game_over:
        all_sprites.update(dt)
        collisions()
    elif game_over and game_over_screen:
        game_over_screen.update()
        game_music.stop()

    # draw the game
    display_surface.fill('#3a2e3f')
    if not game_over:
        display_score()
    display_health()
    all_sprites.draw(display_surface)
    
    if paused:
        display_pause_menu()
    elif game_over and game_over_screen:
        game_over_screen.draw(display_surface)

    pygame.display.update()

pygame.quit()