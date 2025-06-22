#This program was written by Adel Faruque on November 24, 2021
#This is my culminating game in python
#  explanation of the game:
#  a platformer where you can create new paths by moving certain boxes with the mouse.
import pygame, os, random, time
from pygame.locals import *

# The window
WINDOWWIDTH = 1000
WINDOWHEIGHT = 650

# "Colours"
BLUU = (0, 100, 255)
BROWN = (20, 13, 5)
GREEN = (0, 155, 0)
YELLOW = (80, 80, 80)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# The Framerate
FRAMERATE = 35#35

def load_image(filename, useAlpha):
    """ Load an image from a file. Return the image and corresponding rectangle """
    image = pygame.image.load(filename)
    if useAlpha:
        image = image.convert_alpha()  #Not as fast as .convert(), but works with transparent backgrounds
    else:
        image = image.convert()        #For faster screen updating
    return image

def terminate():
    """closes the game when X button or ESC button is pressed"""
    pygame.quit()
    os._exit(1)

def drawText(text, font, surface, x, y, textcolour, background):
    """blits given text, in a textbox"""
    textobj = font.render(text, 1, textcolour, background)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

class Artifact(pygame.sprite.Sprite):
    """ get this to win"""
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def shift(self, speed, horizontal):
        if horizontal: # going up/down
            self.rect.top += speed
        else:
            self.rect.left += speed

class Exit(pygame.sprite.Sprite):
    """ get here to win"""
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def shift(self, speed, horizontal):
        if horizontal: # going up/down
            self.rect.top += speed
        else:
            self.rect.left += speed

class Decoration(pygame.sprite.Sprite):
    """just things in the background"""
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def shift(self, speed, horizontal):
        if horizontal: # going up/down
            self.rect.top += speed
        else:
            self.rect.left += speed

class Background(pygame.sprite.Sprite):
    """ the main wall only. Other walls will be based on this one. good tile effect sold separately"""
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()

    def shift(self, speed, horizontal):
        if horizontal: # going up/down
            self.rect.top += speed
        else:
            self.rect.left += speed

    def update(self, game):
        """if the player gets to an edge of the image, the images should move so that the player is on the opposite side"""
        # ^^ for example if they walk left and get to the left edge, the
        # images move so that the player is on the right of the image
        # so they can keep going right and have the wall moving effect

        playerRect = game.player.rect # because this could be faster in theory than fetching from game.player.rect each time but I don't really know if it is
        # horizontal tiling
        if (playerRect.right < self.rect.left):
            self.rect.right -= 1000
        elif playerRect.left > self.rect.right:
            self.rect.left += 1000

        # vertical tiling
        if playerRect.bottom < self.rect.top:
            self.rect.bottom -= 650
        elif playerRect.top > self.rect.bottom:
            self.rect.top += 650

class Floor(pygame.sprite.Sprite):
    """ also walls idk why its called like this""" # i also used this for the dirt, just because to save a class
    def __init__(self, image, x, y):
        """x goes from the top, y goes from the bottom"""
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.left = x
        self.rect.bottom = y

    def shift(self, speed, horizontal):
        if horizontal: # going up/down
            self.rect.top += speed
        else:
            self.rect.left += speed

class Cursor(pygame.sprite.Sprite):
    """curse, or..."""
    def __init__(self, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images # a list of images based on which cursor to show
        self.currImage = images[0] # the start cursor always at the front of the list
        self.rect = self.currImage.get_rect()
        self.number = 0

    def update(self, number):
        self.number = number
        self.currImage = self.images[number]

class Enemy(pygame.sprite.Sprite):
    """Little Scrib Creature auhh"""
    def __init__(self, image, x, y, trailLength):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.height = 57
        self.rect.left = x
        self.rect.bottom = y+3
        self.rect.width-=13

        # 4 wandering
        self.trailStart = self.rect.left
        self.trailEnd = self.rect.right + trailLength
        self.dir = True # means going left, False means going right
        self.waitTime = None
        self.goTime = time.time() + random.randrange(1, 5)
        self.going = True

        # for the animation
        self.frame1 = False
        self.frameTimer = 0

    def shift(self, speed, horizontal):
        if horizontal: # moving up/down
            self.rect.top += speed
        else:
            self.rect.left += speed
            self.trailEnd += speed
            self.trailStart += speed

    def update(self, game):
        #print('b')
        timer = time.time()
        if self.going:
            if self.dir: # going left
                self.rect.left -= 1
            else: # going right
                self.rect.left +=1

            platList = pygame.sprite.spritecollide(self, game.movables, False)
            for item in platList:
                if isinstance(item, Box) and (item.dragging or item.invis):
                    platList.remove(item)
            if platList:
                if self.dir:
                    self.rect.left = platList[0].rect.right
                    self.rect.left+=35
                    plats = pygame.sprite.spritecollide(self, game.movables, False)
                    self.rect.left -=35
                else:
                    self.rect.right = platList[0].rect.left
                    self.rect.left-=35
                    plats = pygame.sprite.spritecollide(self, game.movables, False)
                    self.rect.left +=35
                if isinstance(platList[0], Player):
                    platList[0].hit = True
                if not plats:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey(BLACK)
                    self.dir = not self.dir
            else:
                if self.rect.left < self.trailStart:
                    self.rect.left = self.trailStart
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey(BLACK)
                    self.dir = not self.dir
                elif self.rect.right > self.trailEnd:
                    self.rect.right = self.trailEnd
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey(BLACK)
                    self.dir = not self.dir
            if timer >= self.goTime or game.paused:
                self.going = False
                #print('a')
                self.waitTime = time.time() + random.randrange(1,4)

        else:
            if timer>= self.frameTimer:
                self.image = game.enemySpritesheet[1*self.frame1]
                self.frameTimer = timer+game.enemyFrameTimer
                self.frame1 = not self.frame1
                if not self.dir: #going left
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey(BLACK)
            if timer >= self.waitTime:
                self.going = True
                self.goTime = time.time() + random.randrange(3,8)

class Box(pygame.sprite.Sprite):
    """The boxes that can be moved with the mouse"""
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()

        self.picked = False # 4 debug

        # position the box
        self.rect.left = x
        self.rect.top = y

        # gravity variables
        self.grounded = False
        self.gravity = 0

        self.invis = False # if the box is released on the player or an enemy, it wont interact with it until they get out of the way, it's 'invisible'

        # drag variable
        self.dragging = False
        self.offset_x = 0 # from the top and negative
        self.offset_y = 0 # from the left and negative

        self.xblock = None # what???
        self.yblock = None

        # for determining orientation of box after a collision
        self.collisionTop = 0
        self.collisionBottom = 0
        self.collisionBLeft = 0
        self.collisionRight = 0

        self.leftIn = 0
        self.rightIn = 0
        self.topIn = 0
        self.botIn = 0

        self.barrierLeft = None
        self.barrierRight = None
        self.barrierUp = None
        self.barrierDown = None

        self.upLimit = None
        self.downLimit = None
        self.leftLimit = None
        self.rightLimit = None


    def shift(self, speed, horizontal):
        if horizontal and not (self.barrierLeft or self.barrierRight): # going up/down
            self.rect.top += speed
        elif not(self.barrierUp or self.barrierDown):
            self.rect.left += speed

    def update(self, game):
        #game.hittables.remove(self)
        if self.dragging:
            self.picked = True                                                           #remove
            mouse = pygame.mouse.get_pos()
            mouseX, mouseY = mouse[0], mouse[1]
            if not self.barrierLeft and not self.barrierRight:
                difference = mouseX + self.offset_x - self.rect.left
                if difference > 23:
                    mouseX = self.rect.left+23-self.offset_x
                elif difference < -23:
                    mouseX = self.rect.left-23
                self.rect.x = mouseX + self.offset_x
            if not self.barrierUp and not self.barrierDown:
                difference = mouseY + self.offset_y - self.rect.top
                if difference > 23:
                    mouseY = self.rect.top+23 - self.offset_y
                elif difference < -23:
                    mouseY = self.rect.top-23
                self.rect.y = mouseY + self.offset_y

            # check for collide
            if (not self.barrierDown and not self.barrierUp and not self.barrierLeft and not self.barrierRight): #jesus
                platList = pygame.sprite.spritecollide(self, game.hittables, False)
                for platform in platList:
                    if not (isinstance(platform, Player) or isinstance(platform, Enemy)): # use a different group which these aren't in?
                        if self.rect.colliderect(platform.rect):
                            if self.rect.left >= platform.rect.left:
                                for y in range(self.rect.top, self.rect.bottom):
                                    if (y >= platform.rect.top and y<=platform.rect.bottom):
                                        self.leftIn +=1
                            if self.rect.right <= platform.rect.right:
                                for y in range(self.rect.top, self.rect.bottom):
                                    if (y >= platform.rect.top and y<=platform.rect.bottom):
                                        self.rightIn +=1
                            if self.rect.top >= platform.rect.top:
                                for x in range(self.rect.left, self.rect.right):
                                    if (x >= platform.rect.left and x<=platform.rect.right):
                                        self.topIn +=1
                            if self.rect.bottom <= platform.rect.bottom:
                                for x in range(self.rect.left, self.rect.right):
                                    if (x >= platform.rect.left and x<=platform.rect.right):
                                        self.botIn +=1

                            touches = [self.topIn, self.botIn, self.leftIn, self.rightIn]
                            side = touches.index(max(touches))

                            if side ==0: # crate touched the bottom
                                self.rect.top = platform.rect.bottom
                                self.barrierUp = platform.rect.bottom
                                self.leftLimit = platform.rect.left
                                self.rightLimit = platform.rect.right
                            elif side ==1: # crate touched the top
                                self.rect.bottom = platform.rect.top
                                self.barrierDown = platform.rect.top
                                self.leftLimit = platform.rect.left
                                self.rightLimit = platform.rect.right
                            elif side ==2: # crate touched the right
                                self.rect.left = platform.rect.right
                                self.barrierLeft = platform.rect.right
                                self.upLimit = platform.rect.top
                                self.downLimit = platform.rect.bottom
                            else: # crate touched the left
                                self.rect.right = platform.rect.left
                                self.barrierRight = platform.rect.left
                                self.upLimit = platform.rect.top
                                self.downLimit = platform.rect.bottom

                            self.topIn, self.botIn, self.leftIn, self.rightIn = 0, 0, 0, 0
                            
                            
            if self.barrierUp:
                self.rect.top-=1
                #game.hittables.remove(self)
                platList2 = pygame.sprite.spritecollide(self, game.hittables, False)
                self.rect.top+=1
                #game.hittables.add(self)
                if not platList2:
                    self.barrierUp = None
            elif self.barrierLeft:
                self.rect.left-=1
                #game.hittables.remove(self)
                platList2 = pygame.sprite.spritecollide(self, game.hittables, False)
                self.rect.left+=1
                #game.hittables.add(self)
                if not platList2:
                    self.barrierLeft = None
            elif self.barrierRight:
                self.rect.right+=1
                #game.hittables.remove(self)
                platList2 = pygame.sprite.spritecollide(self, game.hittables, False)
                self.rect.right-=1
                #game.hittables.add(self)
                if not platList2:
                    self.barrierRight = None
            elif self.barrierDown:
                self.rect.bottom+=1
                #game.hittables.remove(self)
                platList2 = pygame.sprite.spritecollide(self, game.hittables, False)
                self.rect.bottom-=1
                #game.hittables.add(self)
                if not platList2:
                    self.barrierDown = None
                
        else:
            self.barrierDown, self.barrierUp, self.barrierLeft, self.barrierRight = 0, 0, 0, 0
            
            self.rect.bottom += self.gravity
            platList = pygame.sprite.spritecollide(self, game.invisible, False)
            platList.remove(self)
##            if self.picked:
##                print(platList, self.gravity)
            #if self.picked:
                #print(platList, self.invis) # find out why its going invis then not invis when it shouldnt ok i did that
            self.stopInvis = True
            if platList:
                for item in platList:
                    if not self.invis:
                        self.rect.bottom = item.rect.top
                        self.grounded = True
                        self.gravity = 0
                    elif isinstance(item, Player) or isinstance(item, Enemy):
                        self.stopInvis = False
                        self.grounded = False
                    else:
                        self.rect.bottom = item.rect.top
                        self.grounded = True
                        self.gravity = 0
            else:
                self.grounded = False
##                for item in platList:
##                    if not ((isinstance(item, Player) or isinstance(item, Enemy)) and self.invis):
##                        self.rect.bottom = item.rect.top
##                    elif self.invis and (isinstance(item, Player) or isinstance(item, Enemy)):
##                        stopInvis = False
##                self.grounded = True
##                self.gravity = 0
            if self.stopInvis:
                self.invis = False
                game.hittables.add(self) # this one's good
                #game.hittables.add(self)
##            if self.invis:
##                self.grounded = False
##                if self.picked:
##                    print('not grounded')


        if not game.floor and self.rect.bottom > WINDOWHEIGHT:
            self.rect.bottom = WINDOWHEIGHT+1
            self.grounded = True
            self.gravity = 0
        #game.hittables.add(self)
            

class Platform(pygame.sprite.Sprite):
    """platforms used in the levels"""
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        
        # position the platform
        self.rect.left = x
        self.rect.top = y

    def shift(self, speed, horizontal):
        if horizontal: # going up/down
            self.rect.top += speed
        else:
            self.rect.left += speed


class Player(pygame.sprite.Sprite):
    """ The player controlled by the user """
    def __init__(self, image):  
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect() 

        # Position the player in the "centre" of the screen, just the starting position
        self.rect.left = (WINDOWWIDTH/2) - (self.rect.width/2)
        self.rect.bottom = 620

        # repositioning the hitbox when the sprite turns
        self.rectOffsetY = 20
        
        # set up animation variables
        self.anim = 0 # idle, jump, walk
        self.frame = 0 # the frame in the current animation
        self.lastAnim = 0 # the animtion the last frame was from
        self.lastUpdate = time.time() # the last time the frame was changed
        self.lastStep = self.lastUpdate # the last time the steppy sound played
        self.changeFrame = False # if the frame should be changed this frame
        self.faceLeft = False # if the player should idle facing left
        self.walking = False # for the footstep sound effect

        # set up the sound effects for the player
        self.ei = pygame.mixer.Sound('Assets/audio/jump.mp3')
        self.ei.set_volume(0.1)
        self.ih = pygame.mixer.Sound('Assets/audio/hit.mp3')
        
        # set up movement variables
        self.moveLeft = False
        self.moveRight = False
        self.movespeed = 10
        self.lives = 5
        self.hit = False # was an enemy hit this frame?
        self.godTimer = None # the amount of time after getting hit the player can't get hit again for. death would be too fast otherwise

        # vertical moevement variables
        self.gravity = 0
        self.grounded = True

        # used for vertical scrolling
        self.difference = 0

    def jump(self, game):
        if self.grounded:
            if game.musicPlaying:
                self.ei.play()
            self.gravity = -27#-27#-50#-27#-35#-23
            self.grounded = False

    def updateFrame(self, game):
        """ update the player animation"""

        if self.grounded:
            if self.moveLeft: # move left
                self.rectOffsetY = 35
                if self.lastAnim != 2:
                    frame = 0
                    self.lastAnim = 2
                if time.time() - self.lastUpdate >= game.frameTimer:
                    self.lastUpdate = time.time()
                    self.image = game.animations[2][self.frame]
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey(BLACK)
                self.changeFrame = False

            elif self.moveRight: # move right
                self.rectOffsetY = 20
                if self.lastAnim != 2:
                    frame = 0
                    self.lastAnim = 2
                if time.time() - self.lastUpdate >= game.frameTimer:
                    self.image = game.animations[2][self.frame]
                    self.lastUpdate = time.time()

            else: # Idle
                if self.lastAnim != 0:
                    frame = 0
                    self.lastAnim = 0
                if time.time() - self.lastUpdate >= game.frameTimer2:
                    self.image = game.animations[0][self.frame]
                    self.lastUpdate = time.time()
                    if self.faceLeft:
                        self.image = pygame.transform.flip(self.image, True, False)
                        self.image.set_colorkey(BLACK)
            if self.frame>=len(game.animations[2])-1:
                self.frame = 0
            else:
                self.frame +=1
            self.changeFrame = False


        else: # jump
            if time.time() - self.lastUpdate >= game.frameTimer3:
                if self.lastAnim!=1:
                    self.frame = 0
                self.lastUpdate = time.time()
                self.image = game.animations[1][self.frame]
                if self.gravity<=0 and self.frame in range(0, 2):
                    self.frame+=1
                elif self.gravity>=0 and self.frame in range(8, 15):
                    self.frame+=1
                elif self.gravity<=0:
                    self.frame=8
                self.changeFrame= False
                self.lastAnim = 1
                if self.faceLeft or self.moveLeft:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.image.set_colorkey(BLACK)

        
    def update(self, game):
        if game.musicPlaying:
            if self.walking and self.grounded:
                if time.time() - self.lastStep >= game.soundTimer:
                    self.lastStep = time.time()
                    game.steppy[random.randrange(3)].play()
        if self.moveLeft:
            self.rect.left -= self.movespeed
            platList = pygame.sprite.spritecollide(self, game.hittables, False)
            if platList and not (isinstance(platList[0], Box) and (platList[0].dragging or platList[0].invis)):
                self.rect.left = platList[0].rect.right
                if isinstance(platList[0], Enemy):
                    self.hit = True
                elif isinstance(platList[0], Exit) and game.artifactGot:
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    game.levels[game.currentLevel].remove(platList[0])
            elif self.rect.left < 370:
                self.rect.left = 370

        elif self.moveRight:
            self.rect.left += self.movespeed
            platList = pygame.sprite.spritecollide(self, game.hittables, False)
            if platList and not (isinstance(platList[0], Box) and (platList[0].dragging or platList[0].invis)): # checking if platList contains anything hit
                self.rect.right = platList[0].rect.left
                if isinstance(platList[0], Enemy):
                    self.hit = True
                elif isinstance(platList[0], Exit) and game.artifactGot:
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    game.levels[game.currentLevel].remove(platList[0])
            elif self.rect.right > 650:
                self.rect.right = 650
        game.gravitize(game.player)
        if not game.floor:
            self.rect.bottom += self.gravity
        platList = pygame.sprite.spritecollide(self, game.hittables, False)
        #print(platList)
        if self.grounded:
            self.rect.bottom += 2
            platList = pygame.sprite.spritecollide(self, game.hittables, False)
            self.rect.bottom -= 2
##        for item in platList:
##            if (isinstance(item, Box) and (item.dragging or item.invis)):
##                platList.remove(item)
        if platList:
            for item in platList:
                if self.gravity > 0:
                    self.difference = item.rect.top - self.rect.top
                    self.rect.bottom = item.rect.top
                    self.grounded = True
                    self.gravity = 0
                elif self.gravity < 0:
                    self.rect.top = item.rect.bottom
                    self.gravity *= -1
                else:
                    self.rect.bottom = item.rect.top
                    self.grounded = True
                if isinstance(platList[0], Enemy):
                    self.hit = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    game.levels[game.currentLevel].remove(platList[0])
        else:
            self.grounded = False
            
        if self.rect.bottom > WINDOWHEIGHT: # just in case
            self.rect.bottom = WINDOWHEIGHT+1
            self.gravity = 0
            self.grounded = True
        

    def isHit(self, game):
        """ was ane enemy hit this frame?"""
        if self.hit and not self.godTimer:
            self.lives -=1
            self.godTimer = time.time() + 2
            self.hit = False
            if self.lives>0 and game.musicPlaying:
                game.hitSound.play()
                self.ih.play()
        else:
            self.hit = False

class Game():
    """This class represents an instance of the game. can be used to
        reset the game by creating a new instance of this
        class."""
 
    def __init__(self, WINDOWWIDTH, WINDOWHEIGHT):
        """Constructor. Create all our attributes and initialize
        the game. The stats provided customize the game."""

        #Set to True when the game is now done
        self.game_over = False
        
        # set up the groups. allSprites is not needed since there are differet sprites for different levels. the level groups do basically the same thing

        pimage = load_image("Assets/hitbox.png", True)
        self.player = Player(pimage)
        self.boxes = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.hittables = pygame.sprite.Group() # anything that a box could hit while being dragged, only used for collision detection
        self.enemies = pygame.sprite.Group()
        self.movables = pygame.sprite.Group() # any item whose location can vary like player and boxes
        self.deco = pygame.sprite.Group()
        self.invisible = pygame.sprite.Group() # only used for invis detection as it's a special case
        
        # set up the fonts
        self.MAINFONT = pygame.font.SysFont('kozgopr6nmedium', 20)
        self.BASICFONT = pygame.font.SysFont("Comic Sans MS", 20)
        self.SYLPHSCRIPT = pygame.font.SysFont('sylfaen', 40)
        self.SYLPH2 = pygame.font.SysFont('sylfaen', 25)
        
        # set up the images
        self.pauseoverlay = load_image('Assets/pauseoverlay.png', True)
        self.pausedImage = load_image('Assets/paused.png', True)
        self.platImage = load_image('Assets/okood.jpg', False)
        self.platLong = load_image('Assets/loong.jpg', False)
        self.boxImage = load_image('Assets/cratos.jpg', False)
        self.floorImg = load_image('Assets/floot.jpg', False)
        self.wallImg = load_image('Assets/woll.jpg', False)
        self.roof = load_image('Assets/woof.jpg', False)
        self.block = load_image('Assets/endit.jpg', False)
        self.backgroundImg = load_image('Assets/vvallenstein.jpg', False)
        self.wallpaper = load_image('Assets/wall.png', False)
        self.dirt = load_image('Assets/dort.jpg', False)
        self.dirty = load_image('Assets/dert.jpg', False)
        self.heart = load_image('Assets/hudheartsbigger.png', True)
        self.hearts = [(0, 0, 159, 117), (159, 0, 159, 117), (318, 0, 159, 117)]
        self.lifebar = load_image('Assets/lifebarbigger.png', True)
        self.lifebars = [(0, 0, 245, 67), (0, 67, 245, 67), (0, 134, 245, 67), (0, 201, 245, 67), (0, 268, 245, 67), (0, 335, 245, 67)]
        self.hud = load_image('Assets/huddd.png', True)
        self.torch  = load_image('Assets/new/torchradial.png', True)
        self.exitImg = load_image('Assets/aexit2.png', True)
        self.artImg = load_image('Assets/Adolite.png', True)
        self.artIcon = load_image('Assets/adoliteIcon.png', True)
        self.menuIcon = load_image('Assets/pause.png', True)
        self.mutedIcon = load_image('Assets/muted.png', True)
        self.unmutedIcon = load_image('Assets/unmuted.png', True)
        self.artifactGot = False
        self.ladder = load_image('Assets/llader.png', True)
        self.menuimg = load_image('Assets/menyou.png', False)
        self.cursorImg1 = load_image('Assets/thefinal.png', True)
        self.cursorImg2 = load_image('Assets/cursorrr.png', True)
        self.radial = load_image('Assets/radial.png', True)
        self.smallveins = load_image('Assets/dein.png', True)
        self.largeveins = load_image('Assets/cein.png', True)
        self.blood = load_image('Assets/d.png', True)
        self.cursorStyle = 0 # the index for changing the cursor
        self.cursor = Cursor([self.cursorImg1, self.cursorImg2])

        self.background = Background(self.backgroundImg)

        # for pause button
        self.paused = False # self explanatory
        self.menuRect = self.menuIcon.get_rect()
        self.menuRect.right, self.menuRect.top = WINDOWWIDTH-23, 23
        # for mute/unmute button
        self.muteButtonRect = self.mutedIcon.get_rect()
        self.muted = False
        self.muteButtonRect.right, self.muteButtonRect.top = WINDOWWIDTH-88, 23
        self.muteButton = self.unmutedIcon

        # set up the animations
        self.spritesheets = [load_image('Assets/spritesheets/idle.png', True), load_image('Assets/spritesheets/jump.png', True), load_image('Assets/spritesheets/walk.png', True), load_image('Assets/spritesheets/deadsheet.png', True)]
        self.frames = [8, 8, 8, 6] # the number of frames in a row in the spritesheet
        self.framewidths = [93, 92, 92, 100] # the width of one frame in pixels
        self.frameheights = [100, 100, 100, 100] # the height of one frame in pixels
        self.rows = [2, 2, 2, 2] # the number of rows in the spritesheet
        self.animations = [] # list of all player animation lists
        self.enemySpritesheet = self.get_animation(load_image('Assets/spritesheets/screbsheet.png', True), 2, 74, 68, 1)
        #print(self.enemySpritesheet)

        for sheet in range(len(self.spritesheets)):
            self.animations.append(self.get_animation(self.spritesheets[sheet], self.frames[sheet], self.framewidths[sheet], self.frameheights[sheet], self.rows[sheet]))
        
        self.frameTimer = 0.05 # time between frame changes for walking
        self.frameTimer2 = 0.15 # for idle only
        self.frameTimer3 = 0.005 # for jump only
        self.frameTimer4 = 0.07 # for death only
        self.soundTimer = 0.3 #? for timing step sound effects
        self.enemyFrameTimer = 0.7 # for timing enemy frames

        # set up the levels
        self.currentLevel = 0 # actually the level 1 above this
        self.levels = [
        [Platform(self.platLong, -1026, -473), Floor(self.roof, -800, -1350), Floor(self.wallImg, -500, 650), Floor(self.wallImg, -500, 150), Floor(self.wallImg, -500, -350), Floor(self.wallImg, -500, -850), Floor(self.dirt, 4125, 650), Floor(self.dirt, 4125, 150), Floor(self.dirt, 4125, -500), Floor(self.dirt, 4125, -1150), Floor(self.floorImg, -424, 650), Floor(self.floorImg, 1076, 650), Floor(self.floorImg, 2576, 650), Floor(self.dirt, -787, 650), Floor(self.dirt, -787, 150), Floor(self.dirt, -787, -500), Floor(self.dirt, -787, -1150), Floor(self.wallImg, 4050, 650), Floor(self.wallImg, 4050, 150), Floor(self.wallImg, 4050, -350), Floor(self.wallImg, 4050, -850), Floor(self.roof, 2575, -1350), Floor(self.roof, 1024, -1350), Floor(self.roof, -20, -1350), Decoration(self.torch, 350, 150), Decoration(self.torch, -500, -840), Decoration(self.torch, -445, -1320), Decoration(self.torch, -148, -1320), Decoration(self.torch, 168, -1320), Decoration(self.torch, 1300, 100), Decoration(self.torch, 2100, -140), Decoration(self.torch, 2100, -420), Decoration(self.torch, 2100, -780), Decoration(self.ladder, 3810, -1180), Platform(self.platImage, 900, 420), Platform(self.platImage, 1200, 260), Platform(self.platImage, 1500, 100), Platform(self.platLong, 1850, 275), Platform(self.platLong, 1850, -65), Platform(self.platLong, 1850, -355), Box(self.boxImage, 800, 550), Enemy(self.enemySpritesheet[0], 1950, 274, 600), Box(self.boxImage, 2730, 100), Platform(self.platImage, 3000, -210), Platform(self.platLong, 3050, -520), Enemy(self.enemySpritesheet[0], 3300, -521, 400), Box(self.boxImage, 3820, -530), Platform(self.platImage, 2700, -750), Platform(self.platLong, 3050, -1000), Platform(self.platLong, 1650, -1060), Box(self.boxImage, 3500, -1030), Artifact(self.artImg, 1750, -1135), Platform(self.block, 3675, -1350), Exit(self.exitImg, 3780, -1196), Floor(self.dirty, 2575, -1425), Floor(self.dirty, 625, -1425), Floor(self.dirty, -1000, -1425), Platform(self.platImage, -425, 360), Platform(self.platImage, -150, 160), Platform(self.platImage, -425, -30), Platform(self.platImage, 0, -180), Floor(self.wallImg, 1576, -833), Floor(self.wallImg, 1576, -316), Platform(self.platLong, 576, -373), Platform(self.platLong, 276, -373), Enemy(self.enemySpritesheet[0], 326, -373, 500), Enemy(self.enemySpritesheet[0], 626, -373, 880), Enemy(self.enemySpritesheet[0], 450, -373, 400), Platform(self.platLong, -425, -800), Platform(self.platImage, 700, -600), Enemy(self.enemySpritesheet[0], -325, -800, 650), Enemy(self.enemySpritesheet[0], 27, -800, 400), Box(self.boxImage, 732, -650), Decoration(self.blood, 3650, 300)] # floor 1
        ]
        self.level1 = pygame.sprite.Group() # planned to have this many, but ran out of time.
        self.level2 = pygame.sprite.Group()
        self.level3 = pygame.sprite.Group() # would have been the boss level

        self.levelGroups = [self.level1, self.level2, self.level3]
        self.createLevel(self.levels[self.currentLevel])

        # set up music and sounds
        pygame.mixer.music.load('Assets/audio/soaked in darkness.wav')
        #self.gameOverSound = pygame.mixer.Sound('Assets/sus.wav')
        self.winSound = pygame.mixer.Sound('Assets/audio/open.wav')
        self.hitSound = pygame.mixer.Sound('Assets/audio/slatt.wav')
        self.pickupSound = pygame.mixer.Sound('Assets/audio/itemGet.wav')
        self.clickSound = pygame.mixer.Sound('Assets/audio/menuclick.mp3')
        #self.stepSound = pygame.mixer.Sound('Assets/step.mp3')
        self.steppy = [] # all step sound effects
        for x in range(1, 4):
            item = pygame.mixer.Sound("assets/audio/steppy"+str(x)+".mp3")
            item.set_volume(0.15)
            self.steppy.append(item)
            

        # Play the background music
        self.musicPlaying = True

        # keep track of the "floor". used for vertical scroll.
        self.floor = 0

        self.started = True # only used for the opening animation

    # levels
    def createLevel(self, level):
        """sort given list of level objects"""
        for item in level:
            if isinstance(item, Box):
                self.boxes.add(item)
                self.movables.add(item)
            elif isinstance(item, Enemy):
                self.enemies.add(item)
            else:
                self.deco.add(item)
            if not (isinstance(item, Decoration)):
                self.hittables.add(item)
                self.invisible.add(item)
            self.levelGroups[self.currentLevel].add(item)
        self.movables.add(self.player)
        self.invisible.add(self.player)

    def getPositions(self, mainRect):
        """gives the positions of the grid of background images. always the same place relative to the main rect"""
        positions = [(mainRect.left-WINDOWWIDTH, mainRect.top-WINDOWHEIGHT),(mainRect.left, mainRect.top-WINDOWHEIGHT),(mainRect.left+WINDOWWIDTH, mainRect.top-WINDOWHEIGHT), (mainRect.left-WINDOWWIDTH, mainRect.top),(mainRect.left+WINDOWWIDTH, mainRect.top), (mainRect.left - WINDOWWIDTH, mainRect.top+WINDOWHEIGHT),(mainRect.left, mainRect.top+WINDOWHEIGHT),(mainRect.left + WINDOWWIDTH, mainRect.top+WINDOWHEIGHT), (mainRect.left, mainRect.top)]
        return positions

    def gravitize(self, item):
        """process whether gravity will cause items to fall naturally or rise due to input"""
        if not item.grounded:
            item.gravity += 2
        else:
            item.gravity = 0

    def menu(self, surface, game):
        surface.blit(self.menuimg, (0, 0))
        pygame.display.update()
        pygame.mixer.music.load('Assets/audio/null.mp3')
        pygame.mixer.music.play(1, 0.0)
        going = True
        while going:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.clickSound.play()
                        going = False
        pygame.mixer.music.load('Assets/audio/soaked in darkness.wav')
        return

    def get_image(self, sheet, width, height, frame, row):
        # return cropped surface image
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(sheet, (0, 0), (frame*width, row*height, width, height))
        image.set_colorkey(BLACK)
        return image

    def get_animation(self, spritesheet, frames, framewidth, frameheight, rows):
        # extract frames from a spritesheet and return a list of them
        temp_list = []
        for x in range(rows):
            for frame in range(frames):
                temp_list.append(self.get_image(spritesheet, framewidth, frameheight, frame, x))
        return temp_list
                

    def process_events(self, windowSurface, game):
        """ Process all of the keyboard and mouse events.  """

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if not self.paused:
                if event.type == KEYDOWN:
                    # change the keyboard variables
                    if event.key == K_LEFT or event.key == ord('a'):
                        self.player.moveLeft = True
                        self.player.moveRight = False
                        self.player.faceLeft = True
                        self.player.walking = True
                    elif event.key == K_RIGHT or event.key == ord('d'):
                        self.player.moveRight = True
                        self.player.moveLeft = False
                        self.player.faceLeft = False
                        self.player.walking = True
                    elif event.key == K_UP or event.key == ord('w'):
                        self.player.jump(game)
                elif event.type == KEYUP:
                    self.player.anim = 0
                    if event.key == K_LEFT or event.key == ord('a'):
                        self.player.moveLeft = False
                        self.player.faceLeft = True
                        self.player.walking = False
                    elif event.key == K_RIGHT or event.key == ord('d'):
                        self.player.moveRight = False
                        self.player.faceLeft = False
                        self.player.walking = False
                    if event.key == K_ESCAPE:
                        terminate()
                    elif event.key == ord('m'):
                        # toggles the background music
                        if self.musicPlaying:
                            pygame.mixer.stop()
                            pygame.mixer.music.pause()
                            game.muteButton = game.mutedIcon
                        else:
                            pygame.mixer.music.unpause()
                            game.muteButton = game.unmutedIcon
                        self.musicPlaying = not self.musicPlaying
                elif event.type == MOUSEBUTTONDOWN:
                    #The user clicks to restart the game when it is over
                    if self.game_over: #adel get rid of in favor of win and lose functions
                        #Start a new game
                        self.__init__()
                        if self.musicPlaying:
                            pygame.mixer.music.play(-1, 0.0)
                    elif event.button == 1:
                        if self.menuRect.collidepoint(event.pos):
                            self.paused = True
                            self.player.moveLeft = False
                            self.player.moveRight = False
                        elif self.muteButtonRect.collidepoint(event.pos):
                            if self.musicPlaying:
                                pygame.mixer.music.pause()
                                pygame.mixer.stop()
                                game.muteButton = game.mutedIcon
                            else:
                                pygame.mixer.music.unpause()
                                game.muteButton = game.unmutedIcon
                            #game.muted = not game.muted
                            self.musicPlaying = not self.musicPlaying
                        for box in self.boxes:
                            if box.rect.collidepoint(event.pos):
                                self.cursor.update(1)
                                box.dragging = True
                                box.invis = False
                                self.hittables.remove(box)
                                box.gravity = 0
                                mouse_x, mouse_y = event.pos
                                box.offset_x = box.rect.x - mouse_x
                                box.offset_y = box.rect.y - mouse_y

                elif event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        for box in self.boxes:
                            if box.dragging:
                                box.dragging = False
                                platList = pygame.sprite.spritecollide(box, self.invisible, False)
                                platList.remove(box)
                                #if box.picked:
                                    #print(platList)
                                for item in platList:
                                    if (isinstance(item, Enemy) or isinstance(item, Player)):
                                        box.invis = True
                                if not box.invis:
                                    self.hittables.add(box)
                                if len(platList)>=1:
                                    box.grounded = True
                                else:
                                    box.grounded = False
                        if self.cursor.number != 0:
                            self.cursor.update(0)

                elif event.type == MOUSEMOTION:
                    mouse_x, mouse_y = event.pos
                    
                    for box in self.boxes:
                        if box.dragging:
                            if box.barrierLeft and (mouse_x > box.rect.left-box.offset_x or box.rect.bottom < box.upLimit or box.rect.top > box.downLimit):
                                box.barrierLeft = None
                                box.upLimit = None
                                box.downLimit = None
                            elif box.barrierRight and (mouse_x < box.rect.left+box.offset_x or box.rect.bottom < box.upLimit or box.rect.top > box.downLimit):
                                box.barrierRight = None
                                box.upLimit = None
                                box.downLimit = None
                            elif box.barrierUp and (mouse_y > box.rect.top-box.offset_y or box.rect.left > box.rightLimit or box.rect.right < box.leftLimit):
                                box.barrierUp = None
                                box.leftLimit = None
                                box.rightLimit = None
                            elif box.barrierDown and (mouse_y < box.rect.top-box.offset_y or box.rect.left > box.rightLimit or box.rect.right < box.leftLimit):
                                box.barrierDown = None
                                box.leftLimit = None
                                box.rightLimit = None
            else:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.paused = False

                      
    def run_logic(self, game):
        """ Check for collisions, loss of life and if time to add new food"""
        if self.player.lives ==0:
            self.game_over = True

        elif self.player.godTimer:
            now = time.time()
            if now >= self.player.godTimer:
                self.player.godTimer = None

        pos = pygame.mouse.get_pos()
        self.cursor.rect.x = pos[0]
        self.cursor.rect.y = pos[1]

        for box in game.boxes:
            if not box.dragging:
                game.gravitize(box)
            game.level1.remove(box)
            game.level1.add(self.player)
            box.update(game)
            game.level1.add(box)
            game.level1.remove(self.player)

        #if not game.paused:
        for enemy in game.enemies:
            enemy.update(game)

    def moveBackground(self, game):
        """move the level onto the screen as the player moves"""
        level = game.levelGroups[game.currentLevel] # for shifting
        hittables = game.hittables # for collision

        # for dragged boxes
        pos = pygame.mouse.get_pos()
        box = None
        for x in game.boxes:
            if x.dragging:
                box = x

        # horizontal scroll
        if self.player.moveLeft and self.player.rect.left < 371:
            self.player.rect.left -= 10
            platList = pygame.sprite.spritecollide(self.player, hittables, False)
            self.player.rect.left += 10
            if platList and not (isinstance(platList[0], Box) and (platList[0].dragging or platList[0].invis)):
                difference = self.player.rect.left - platList[0].rect.right
                for item in level:
                    item.shift(difference, False)
                game.background.shift(difference, False)
                if isinstance(platList[0], Enemy):
                    self.player.hit = True
                elif isinstance(platList[0], Exit):
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    level.remove(platList[0])
            else:
                for item in level:
                    item.shift(10, False)
                game.background.shift(10, False)
                if box:
                    if box.barrierRight:
                        box.barrierRight+=10
                        if pos[0]<box.barrierRight:
                            box.barrierRight = None
                    elif box.barrierDown:
                        box.rect.bottom+=1
                        #hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, hittables, False)
                        box.rect.bottom-=1
                        #hittables.add(box)
                        if not platList2:
                            box.barrierDown = None
            
        elif self.player.moveRight and self.player.rect.right > 649:
            self.player.rect.right += 10
            platList = pygame.sprite.spritecollide(self.player, hittables, False)
            self.player.rect.right -= 10
            if platList and not (isinstance(platList[0], Box) and (platList[0].dragging or platList[0].invis)):
                difference = platList[0].rect.left - self.player.rect.right
                for item in level:
                    item.shift(-difference, False)
                game.background.shift(-difference, False)
                if isinstance(platList[0], Enemy):
                    self.player.hit = True
                elif isinstance(platList[0], Exit) and self.artifactGot:
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    level.remove(platList[0])
            else:
                for item in level:
                    item.shift(-10, False)
                game.background.shift(-10, False)
                if box:
                    if box.barrierLeft:
                        box.barrierLeft-=10
                        if pos[0]>box.barrierLeft:
                            box.barrierLeft = None
                    elif box.barrierDown:
                        box.rect.bottom+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.bottom-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierDown = None

        if self.player.gravity < 0 and self.player.rect.top < 225: # player rising
            self.player.rect.top = 224
            self.player.rect.top += self.player.gravity
            platList = pygame.sprite.spritecollide(self.player, hittables, False)
            self.player.rect.top -= self.player.gravity
            if platList and not (isinstance(platList[0], Box) and (platList[0].dragging or platList[0].invis)):
                difference = platList[0].rect.bottom - self.player.rect.top
                for item in level:
                    item.shift(difference, True)
                game.background.shift(difference, True)
                self.floor += difference
                self.player.gravity *= -1
                if isinstance(platList[0], Enemy):
                    self.player.hit = True
                elif isinstance(platList[0], Exit) and self.artifactGot:
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    level.remove(platList[0])
            else:
                for item in level:
                    item.shift(-self.player.gravity, True)
                game.background.shift(-self.player.gravity, True)
                self.floor -= self.player.gravity
                if box:
                    if box.barrierDown:
                        box.barrierDown-=self.player.gravity
                        if pos[1]<box.barrierDown:
                            box.barrierDown = None
                    elif box.barrierLeft:
                        box.rect.left+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.left-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierLeft = None
                    elif box.barrierRight:
                        box.rect.right+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.right-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierRight = None

        elif self.player.gravity > 0 and self.floor > 0: # player falling, above the main screen
            self.player.rect.bottom += self.player.gravity
            platList = pygame.sprite.spritecollide(self.player, hittables, False)
            self.player.rect.bottom -= self.player.gravity
            difference= 0
            if platList and not (isinstance(platList[0], Box) and (platList[0].dragging or platList[0].invis)):
                if isinstance(platList[0], Enemy):
                    self.player.hit = True
                elif isinstance(platList[0], Exit) and self.artifactGot:
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
                    level.remove(platList[0])
                difference = platList[0].rect.top - self.player.rect.bottom
                if difference < self.floor:
                    for item in level:
                        item.shift(-difference, True)
                    game.background.shift(-difference, True)
                    self.floor -= difference
                    if box:
                        if box.barrierUp:
                            box.barrierUp-=difference
                            if pos[1]>box.barrierUp:
                                box.barrierUp = None
                        elif box.barrierLeft:
                            box.rect.left+=1
                            game.hittables.remove(box)
                            platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                            box.rect.left-=1
                            #game.hittables.add(box)
                            if not platList2:
                                box.barrierLeft = None
                        elif box.barrierRight:
                            box.rect.right+=1
                            game.hittables.remove(box)
                            platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                            box.rect.right-=1
                            #game.hittables.add(box)
                            if not platList2:
                                box.barrierRight = None
                else:
                    for item in level:
                        item.shift(-self.floor, True)
                    game.background.shift(-self.floor, True)
                    self.floor = 0
                self.player.gravity = 0
                self.player.grounded = True
                if box:
                    if box.barrierUp:
                        box.barrierUp-=self.floor
                        if pos[1]>box.barrierUp:
                            box.barrierUp = None
                    elif box.barrierLeft:
                        box.rect.left+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.left-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierLeft = None
                    elif box.barrierRight:
                        box.rect.right+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.right-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierRight = None
                
                if isinstance(platList[0], Enemy):
                    self.player.hit = True
                elif isinstance(platList[0], Exit) and self.artifactGot:
                    self.game_over = True
                elif isinstance(platList[0], Artifact):
                    game.pickupSound.play()
                    game.artifactGot = True
                    platList[0].kill()
            elif self.floor > self.player.gravity:
                for item in level:
                    item.shift(-self.player.gravity, True)
                game.background.shift(-self.player.gravity, True)
                if box:
                    if box.barrierUp:
                        box.barrierUp-=self.player.gravity
                        if pos[1]>box.barrierUp:
                            box.barrierUp = None
                    elif box.barrierLeft:
                        box.rect.left+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.left-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierLeft = None
                    elif box.barrierRight:
                        box.rect.right+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.right-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierRight = None
                            
                self.floor -= self.player.gravity
            elif self.floor < self.player.gravity:
                for item in level:
                    item.shift(-self.floor, True)
                game.background.shift(-self.floor, True)
                if box:
                    if box.barrierUp:
                        box.barrierUp-=self.floor
                        if pos[1]>box.barrierUp:
                            box.barrierUp = None
                    elif box.barrierLeft:
                        box.rect.left+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.left-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierLeft = None
                    elif box.barrierRight:
                        box.rect.right+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.right-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierRight = None
                            
                self.floor = 0
            else:
                for item in level:
                    item.shift(-self.player.gravity, True)
                game.background.shift(-self.player.gravity, True)
                self.floor -= self.player.gravity
                if box:
                    if box.barrierUp:
                        box.barrierUp-=self.player.gravity
                        if pos[1]>box.barrierUp:
                            box.barrierUp = None
                    elif box.barrierLeft:
                        box.rect.left+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.left-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierLeft = None
                    elif box.barrierRight:
                        box.rect.right+=1
                        game.hittables.remove(box)
                        platList2 = pygame.sprite.spritecollide(box, game.hittables, False)
                        box.rect.right-=1
                        #game.hittables.add(box)
                        if not platList2:
                            box.barrierRight = None
  
    def display_frame(self, windowSurface):
        """ Display everything to the screen for the game. """
        windowSurface.fill(BROWN)
        
        if self.game_over:
            # The user will click to restart the game
            if self.player.lives > 0:
                if self.musicPlaying:
                    self.winSound.play()
                self.musicPlaying = False
                drawText("The light bathes over your body", self.SYLPHSCRIPT, windowSurface, 220, 270, GREEN, None)
                drawText("you are free from the darkness", self.SYLPHSCRIPT, windowSurface, 250, 320, GREEN, None)
                drawText("Click to Play Again", self.SYLPH2, windowSurface, 400, 400, YELLOW, None)
            else:
                self.lose(windowSurface)
##                if self.musicPlaying:
##                    self.gameOverSound.play()
##                self.musicPlaying=False
##                windowSurface.blit(self.lifebar, (120, 30), self.lifebars[5])
##                windowSurface.blit(self.heart, (15, 15), self.hearts[2])
##                drawText("The darkness weaves through your body", self.SYLPHSCRIPT, windowSurface, 170, 270, GREEN)
##                drawText("you are lost to the void", self.SYLPHSCRIPT, windowSurface, 280, 320, GREEN)
##                drawText("Click to Restart", self.SYLPH2, windowSurface, 400, 400, YELLOW)
        else:
            # draw the background images onto the surface first
            mainRect = self.background.rect
            positions = self.getPositions(mainRect)
            for pos in positions:
                mainRect.left, mainRect.top = pos[0], pos[1]
                windowSurface.blit(self.backgroundImg, mainRect)

            # draw the player and the level onto the surface
            #for x in self.enemies:
                #pygame.draw.rect(windowSurface, GREEN, x.rect)
            self.levelGroups[self.currentLevel].draw(windowSurface)
            windowSurface.blit(self.player.image, (self.player.rect.left-self.player.rectOffsetY, self.player.rect.top-14))
            #print(self.player.rect)
            if self.player.lives <2:
                windowSurface.blit(self.largeveins, (0, 0))
            elif self.player.lives <5:
                windowSurface.blit(self.smallveins, (0, 0))
            windowSurface.blit(self.radial, (-150, -350))
            windowSurface.blit(self.lifebar, (120, 30), self.lifebars[5-self.player.lives])
            windowSurface.blit(self.hud, (15, 33))
            windowSurface.blit(self.heart, (15, 15), self.hearts[0+(1*(self.player.lives<3))])
            if self.artifactGot:
                windowSurface.blit(self.artIcon, (375, 40))
        # draw the window onto the screen
        windowSurface.blit(self.menuIcon, self.menuRect)
        windowSurface.blit(self.muteButton, self.muteButtonRect)
        if self.paused:
            windowSurface.blit(self.pauseoverlay, (0,0))
            windowSurface.blit(self.pausedImage, (0, 0))
        windowSurface.blit(self.cursor.currImage, self.cursor.rect)
        #pygame.draw.rect(windowSurface, GREEN, self.player.rect) # the hitbox for debug
        pygame.display.update()

    def opening(self, surface, windowSurface):
        """sort of like the opening cutscene""" # ok why the fuck didnt i think of this shit in the first place
        time1 = time.time() # the time this sequence started
        current = time1 # the time between frame changes
        x = 11 # the frame to display, goes backwards so the death anim looks like getting up
        alpha = 255
        alpha2 = 255
        while time.time() - time1 < 4:
            #print('here')
            #windowSurface.fill(BLUU)
            windowSurface.blit(surface, (0,0))
            s = pygame.Surface((WINDOWWIDTH,WINDOWHEIGHT))
            s.set_alpha(alpha)
            s.fill(BLACK)
            windowSurface.blit(s, (0,0))
            if time.time() - time1 > 2:
                if time.time() - current > self.frameTimer4:
                    if x!=0:
                        x-=1
                    elif alpha>-1:
                        alpha-= 20
                    else:
                        alpha = 0
                    current = time.time()

            self.player.image = self.animations[3][x]
            windowSurface.blit(self.player.image, (self.player.rect.left-40, self.player.rect.top-14))
            windowSurface.blit(self.radial, (-150, -350))
            pygame.display.update()
                

    def lose(self, windowSurface):
        """when the player loses"""
        #if self.musicPlaying:
        #    self.gameOverSound.play()
        timing = time.time()
        self.player.frame=0
        restart = Rect(390, 393, 180, 36)
        going = True
        while going:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if time.time() - timing >=4.1:
                            if restart.collidepoint(pos):
                                self.__init__(WINDOWWIDTH, WINDOWHEIGHT)
                                going = False
                                if self.musicPlaying:
                                    pygame.mixer.music.play(-1, 0.0)
##                if event.type == MOUSEBUTTONDOWN:
##                    yes = 1
            #self.musicPlaying=False # do we need this now? we dont

            if time.time() - self.player.lastUpdate >= self.frameTimer4:
                self.player.image = self.animations[3][self.player.frame]
                self.player.lastUpdate = time.time()
                if self.player.frame<11:
                    self.player.frame +=1
                if self.player.faceLeft:
                    self.player.image = pygame.transform.flip(self.player.image, True, False)
                self.player.image.set_colorkey(BLACK)
            pos = pygame.mouse.get_pos()
            self.cursor.rect.x = pos[0]
            self.cursor.rect.y = pos[1]
            background = BLACK
            if restart.collidepoint(pos):
                background = (10, 10, 10)
            
            windowSurface.fill(BLACK)
            windowSurface.blit(self.lifebar, (120, 30), self.lifebars[5])
            windowSurface.blit(self.heart, (15, 15), self.hearts[2])
            windowSurface.blit(self.player.image, (self.player.rect.left-self.player.rectOffsetY, self.player.rect.top-14))
            if time.time() - timing >= 2.5:
                drawText("The darkness weaves through your body", self.SYLPHSCRIPT, windowSurface, 170, 270, GREEN, None)
            if time.time() - timing >= 3.3:
                drawText("you are lost to the void", self.SYLPHSCRIPT, windowSurface, 295, 320, GREEN, None)
            if time.time() - timing >= 4.1:
                pygame.draw.rect(windowSurface, background, restart)
                drawText("Click to Restart", self.SYLPH2, windowSurface, 400, 400, YELLOW, None)
            windowSurface.blit(self.cursor.currImage, self.cursor.rect)
            pygame.display.update()

def main():
    """The mainline"""
    pygame.init()
    mainClock = pygame.time.Clock()
    
    windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
    pygame.display.set_caption('Ascend_The_Darkness stable build 0.3.5 KasonCodes Inc. (c) 2004')
    pygame.display.set_icon(load_image('Assets/icon1.png', True))

    loading = load_image('Assets/loading.png', False)
    windowSurface.blit(loading, (0, 0))
    pygame.display.update()
    game = Game(WINDOWWIDTH, WINDOWHEIGHT)

    pygame.mouse.set_visible(False)
    game.menu(windowSurface, game)
    pygame.mixer.music.play(-1, 0.0)
    game.opening(game.wallpaper, windowSurface)
    
    while True: # The game loop
        # Process events (keystrokes, mouse clicks, etc)
        game.process_events(windowSurface, game)

        # check for collisions, loss of life, etc.
        game.run_logic(game)

        # move the player
        game.player.update(game)
        game.player.updateFrame(game)
        game.moveBackground(game)
        game.background.update(game)
        game.player.isHit(game)

        # Draw the current frame
        game.display_frame(windowSurface)

        mainClock.tick(FRAMERATE)
        
main()