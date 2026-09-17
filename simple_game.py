import pygame
import sys
import time 

pygame.init()

current_level = 0

objects : list = []


class Transform:
    position: pygame.math.Vector2
    scale: pygame.math.Vector2
    rotation: float = 0.0

    def __init__(self, position: pygame.math.Vector2, scale: pygame.math.Vector2) -> None:
        self.position = position
        self.scale = scale

class GameObject:
    tag : str 
    surface: pygame.Surface 
    Rect : pygame.Rect
    transform : Transform
    Mass : int = 1
    color : tuple

    def __init__(self , color :tuple[int ,int , int] , transform : Transform , tag) -> None:
        self.tag = tag
        self.transform = transform
        self.color = color
        self.surface = pygame.Surface(self.transform.scale)
        self.surface.fill(self.color)
        self.Rect = pygame.Rect(self.transform.position , self.transform.scale)

    def draw(self, screen: pygame.Surface) -> None:
        self.surface.fill(self.color)
        self.Rect.update(self.transform.position , self.transform.scale)
        screen.blit(self.surface, self.transform.position)

class PLayer(GameObject):
    is_grounded: bool = False
    velocity: pygame.math.Vector2
    speed: float = 3
    gravity: float = 0.1
    jump_strength: float = 4.5

    def __init__(self, color: tuple[int, int, int], transform: Transform) -> None:
        super().__init__(color, transform, "Player")
        self.velocity = pygame.math.Vector2(0, 0)

    def jump(self, keys) -> None:
        if keys[pygame.K_SPACE] and self.is_grounded:
            self.velocity.y = -self.jump_strength
            self.is_grounded = False  
       
    def move(self, keys) -> None:

        self.velocity.x = 0
        if keys[pygame.K_a]:
            self.velocity.x -= self.speed
        if keys[pygame.K_d]:
            self.velocity.x += self.speed

        self.velocity.y += self.gravity

        if self.is_grounded:
            self.jump(keys)

        self.transform.position.x += self.velocity.x 
        self.transform.position.y += self.velocity.y

        self.transform.position.x = max(0, min(self.transform.position.x, WIDTH - self.transform.scale.x))
        self.transform.position.y = min(self.transform.position.y, HEIGHT - self.transform.scale.y)



    def collison(self, obj: GameObject) -> None:
        
        


        if self.Rect.colliderect(obj.Rect):

            # Calculate the overlap on each side
            dx_left = self.Rect.right - obj.Rect.left
            dx_right = obj.Rect.right - self.Rect.left
            dy_top = self.Rect.bottom - obj.Rect.top
            dy_bottom = obj.Rect.bottom - self.Rect.top
           
            # Find the minimum overlap - to find the correct direction to push the player out
            min_dx = min(dx_left, dx_right)
            min_dy = min(dy_top, dy_bottom)

            # Resolve the collision
            if min_dx < min_dy:
                if dx_left < dx_right:
                    self.transform.position.x -= dx_left
                else:
                    self.transform.position.x += dx_right
            else:
                if dy_top < dy_bottom:
                    self.transform.position.y -= dy_top
                    self.velocity.y = -0.1
                else:
                    self.transform.position.y += dy_bottom

            # Update the Rect
            self.Rect.update(self.transform.position.x, self.transform.position.y, self.transform.scale.x, self.transform.scale.y)

            # Check if the player is grounded
            if obj.tag.lower() == "ground" and dy_top <= 1:
                self.is_grounded = True

            if obj.tag.lower() == "Next Level".lower():
                global current_level
                if current_level + 1 < len(levels):
                    current_level += 1
                    global objects
                    objects = levels[current_level]
                    self.transform.position = pygame.math.Vector2(0, 0)
                else:
                    sys.exit()
                             
class DissapearingObject(GameObject):
    is_diaspperaing: bool = False
    lifetime: float
    recover_time: float 
    gap : float 

    def __init__(self, color: tuple[int, int, int], transform: Transform, tag , lifetime: float) -> None:
        super().__init__(color, transform, tag)
        self.lifetime: float = lifetime
        self.recover_time: float = 5
        self.gap = 1
       
    def draw(self, screen: pygame.Surface) -> None:
       
        if not self.is_diaspperaing:
            self.surface.fill(BLACK)       
            super().draw(screen)
            if self.Rect.colliderect(player.Rect) and player.Rect.bottom <= self.Rect.top + 1:
                self.start_time = time.time()
                self.is_diaspperaing = True
            return
        
        elapsed = time.time() - self.start_time
        
        if elapsed > self.lifetime:
            if elapsed > self.lifetime + self.recover_time:
                self.can_bedrwn = True
                self.is_diaspperaing = False
                self.gap = 1
                self.start_time = 0
                self.color = BLACK
                return
            else:
                self.Rect.update((-100 , self.transform.position.y), self.transform.scale)
                self.can_bedrwn = False
                return
        
        if int(elapsed * self.gap) % 2 == 0:
                self.color = PURPLE
                self.gap += 0.2
                super().draw(screen)
        else:
            self.color = BLACK
            super().draw(screen)
        
class Anchor(GameObject):
    
    def __init__(self, color: tuple[int, int, int], transform: Transform , tag: str) -> None:
        super().__init__(color, transform , tag)

class Portal(GameObject):
    can_teleport : bool 
    start_time : float
    cooldown : float 
    anchor_tag : str
    anchor : Anchor

    def __init__(self, color: tuple[int, int, int], transform: Transform, tag: str , cooldown : float) -> None:
        super().__init__(color, transform, tag )
        self.can_teleport = True
        self.cooldown = cooldown
        self.anchor_tag = self.tag.lower()

        
        
    def find_anchor(self):
        global objects
        for obj in objects:
            if obj.tag.lower() == self.anchor_tag and isinstance(obj , Anchor):
                self.anchor = obj
                break
            else:
                self.anchor = default_anchor

    def teleport(self , player : PLayer):
        if self.Rect.colliderect(player.Rect) and self.can_teleport:
            self.find_anchor()
            player.transform = Transform(pygame.math.Vector2(self.anchor.transform.position.x , self.anchor.transform.position.y) 
                                        ,player.transform.scale)
            self.can_teleport = False
            self.start_time = time.time()

    
    def draw(self, screen: pygame.Surface) -> None:
    
        super().draw(screen)

        if self.can_teleport:
            self.teleport(player)
            return

        if time.time() - self.start_time > self.cooldown:
            self.can_teleport = True
            self.color = GRAY
        else:
            self.color = BLACK
        
                 
WIDTH: int = 1600
HEIGHT: int = 900
FPS: int = 100


WHITE =   (255, 255, 255)
BLACK =   (  0,   0,   0)
RED =     (255,   0,   0)
GREEN =   (  0, 255,   0)
BLUE  =   (  0,   0, 255)
PURPLE=   (160,  32, 240)
MAGENTA = (255,   0, 255) 
GRAY =    (200, 200, 200)
LIGHT_RED=(255, 180, 180)


screen = pygame.display.set_mode((WIDTH, HEIGHT) , pygame.FULLSCREEN)

pygame.display.set_caption("Pygame")

player = PLayer(RED , Transform(pygame.math.Vector2(0 , 0) , pygame.math.Vector2(50 , 50)))

default_anchor = Anchor(LIGHT_RED , Transform(pygame.math.Vector2(0 ,   0)  ,pygame.math.Vector2(50  , 50)), "default_anchor")

demo : list[GameObject] = [     Portal(GRAY      , Transform(pygame.math.Vector2(1450,  800) , pygame.math.Vector2(50  , 50)) , "one" , 5)
                              , Anchor(LIGHT_RED , Transform(pygame.math.Vector2(1000 ,   0) , pygame.math.Vector2(50  , 50)) , "one")   
                              , GameObject(GREEN , Transform(pygame.math.Vector2(0   ,  850) , pygame.math.Vector2(1600, 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(200 ,  450) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(400 ,  350) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(600 ,  250) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(200 ,  250) , pygame.math.Vector2(100 , 50)) , "Ground") 
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(400 ,  550) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(200 ,  650) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(600 ,  650) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(400 ,  750) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(600 ,  450) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(BLUE  , Transform(pygame.math.Vector2(1000,  600) , pygame.math.Vector2(100 , 50)) , "Ground")
                              , GameObject(MAGENTA,Transform(pygame.math.Vector2(800 ,  150) , pygame.math.Vector2(100 , 50)) , "Next Level")                                                       
                      , DissapearingObject(BLACK , Transform(pygame.math.Vector2(400 ,  150) , pygame.math.Vector2(100 , 50)) , "Ground", 1.5)
                            ]

level_1: list[GameObject] = [   GameObject(GREEN   , Transform(pygame.math.Vector2(0    ,  850) , pygame.math.Vector2(1600 , 50)) , "Ground")
                            ,   GameObject(BLUE    , Transform(pygame.math.Vector2(200  ,  750) , pygame.math.Vector2(100  , 50)) , "Ground")
                            ,   GameObject(BLUE    , Transform(pygame.math.Vector2(400  ,  650) , pygame.math.Vector2(100  , 50)) , "Ground")
                            ,   GameObject(BLUE    , Transform(pygame.math.Vector2(600  ,  550) , pygame.math.Vector2(100  , 50)) , "Ground")
                            ,   GameObject(BLUE    , Transform(pygame.math.Vector2(800  ,  450) , pygame.math.Vector2(100  , 50)) , "Ground")
                            ,   GameObject(BLUE    , Transform(pygame.math.Vector2(1000 ,  350) , pygame.math.Vector2(100  , 50)) , "Ground")
                            ,   GameObject(BLUE    , Transform(pygame.math.Vector2(1200 ,  250) , pygame.math.Vector2(100  , 50)) , "Ground")
                            ,   GameObject(MAGENTA , Transform(pygame.math.Vector2(1400 ,  150) , pygame.math.Vector2(100  , 50)) , "Next Level")
                            ]       

level_2: list[GameObject] = [            Portal(GRAY      , Transform(pygame.math.Vector2(0   ,  850) , pygame.math.Vector2(1600, 50)) , "ANCHOR_1" , 0)
                            ,            Anchor(LIGHT_RED , Transform(pygame.math.Vector2(0   ,    0) , pygame.math.Vector2(50  , 50)) , "ANCHOR_1") 
                            ,        GameObject(BLUE      , Transform(pygame.math.Vector2(0   ,  450) , pygame.math.Vector2(100 , 50)) , "Ground")
                            ,DissapearingObject(BLACK     , Transform(pygame.math.Vector2(300 ,  450) , pygame.math.Vector2(100 , 50)) , "Ground", 0)
                            ,DissapearingObject(BLACK     , Transform(pygame.math.Vector2(600 ,  450) , pygame.math.Vector2(100 , 50)) , "Ground", 0)
                            ,DissapearingObject(BLACK     , Transform(pygame.math.Vector2(900 ,  450) , pygame.math.Vector2(100 , 50)) , "Ground", 0)   
                            ,DissapearingObject(BLACK     , Transform(pygame.math.Vector2(1200,  450) , pygame.math.Vector2(100 , 50)) , "Ground", 0)      
                            ,        GameObject(MAGENTA   , Transform(pygame.math.Vector2(1500,  450) , pygame.math.Vector2(100 , 50)) , "Next Level") 
                                
                            ]

levels : list[list[GameObject]] = [level_1 , level_2 , demo]

objects = levels[current_level]

clock = pygame.time.Clock()

    
def draw_grid() -> None:
    gap = 50
    for x in range(0, WIDTH, gap):
        pygame.draw.line(screen, LIGHT_RED, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, gap):
        pygame.draw.line(screen, LIGHT_RED, (0, y), (WIDTH, y), 1)

def ofsett_grid() -> None:
    gap = 50
    for x in range(-25 , WIDTH , gap):
        pygame.draw.line(screen , GRAY , (x,0) , (x , HEIGHT) , 1)
    for y in range(-25 , HEIGHT , gap):
        pygame.draw.line(screen , GRAY , (0,y) , (WIDTH , y) , 1)

def frame_rate() -> None:
    font = pygame.font.SysFont(None, 24)
    fps_text = font.render(f'FPS: {int(clock.get_fps())}', True, BLACK)
    screen.blit(fps_text, (20, 20))

def main() -> None:
    
    running: bool = True
    fullscreen: bool = False

    while running:
        keys = pygame.key.get_pressed()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Toggle fullscreen 

        if keys[pygame.K_F11] :
            if fullscreen:
                fullscreen = False
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            else:
                fullscreen = True
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

        # Game logic heres
        
        player.move(keys)

        for obj in objects:
            player.collison(obj)
        

        # Draw things here
        
        screen.fill(WHITE)
        draw_grid()
        ofsett_grid()
        
        player.draw(screen)

        for obj in objects:
            obj.draw(screen)

        frame_rate()
            
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()