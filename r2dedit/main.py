import pygame
import PIL
import block
import rsv2
import typing
import assetload
import rsvedit
import math

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/demo_world'

chs = rsv2.readall(f)

ch = chs[(0,-1)]

# im = pygame.Surface((w,h))
# im.blit(tiles,(x,y),(tx,ty,w,h))

def spostowpos(spos, t):
    sx,sy = spos
    tx,ty = t
    x = sx - tx
    y = sy - ty
    x /= 16
    y /= 16
    return x, y

class App:
    clock: pygame.time.Clock
    _running: bool
    _display_surf: pygame.Surface | None
    size: tuple[int, int]
    width: int
    height: int
    t: tuple[int, int]

    def __init__(self, width: int, height: int) -> None:
        # initialize variables
        self.clock = pygame.time.Clock()
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = width, height
        self.t = (0, 0)
 
    def on_init(self) -> bool:
        # start the pygame window
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size)
        self._running = True
        return True
    
    def on_event(self, event: pygame.event.Event) -> None:
        # when something happens
        if event.type == pygame.QUIT:
            # close the window when the x is clicked
            self._running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1 left
            # 2 middle
            # 3 right
            # 4 scroll up
            # 5 scroll down
            if event.button == 1 or event.button == 3:
                x,y = spostowpos(event.pos, self.t)
                x = math.floor(x)
                y = math.floor(y)
                a,b,c,d,e = rsvedit.getblock(chs, x, y)
                b = b & 0b00001111
                rsvedit.setblock(chs, x, y, (a,b,c,d,e))
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[1]:
                dx,dy = event.rel
                self.t = (self.t[0] + dx, self.t[1] + dy)
    
    def on_loop(self) -> None:
        # wait to ensure a uniform framerate
        # don't set this too fast, or the framerate won't be the same all the time
        self.clock.tick(30)
    
    def on_render(self) -> None:
        assert self._display_surf is not None
        # fill the screen with black
        self._display_surf.fill((0, 0, 0))
        sx,sy = spostowpos((0, 0), self.t)
        sxf,sxd = divmod(sx, 1)
        syf,syd = divmod(sy, 1)
        blocks = [
            [
                typing.cast(block.BlockDataIn,{
                    'type':assetload.idtoblock[a],
                    'weld':[
                        block.makeweldside((b >> n & 1) == 1)
                        for n in [4,7,6,5]
                    ]
                })
                for x in range(int(sxf), int(sxf + math.ceil(self.width / 16) + 1))
                for a,b,c,d,e in (rsvedit.getblock(chs,x,y),)
            ]
            for y in range(int(syf), int(syf + math.ceil(self.height / 16) + 1))
        ]
        ims = block.makeimage(blocks,autoweld = False)
        for im,x,y in ims:
            self._display_surf.blit(im, (x - sxd * 16, y - syd * 16))
    
    def on_cleanup(self) -> None:
        # close the pygame window
        pygame.quit()
 
    def on_execute(self) -> None:
        if self.on_init() == False:
            self._running = False
 
        while self._running:
            # do stuff that happens every frame
            self.on_loop()
            # drawing things
            self.on_render()
            # show changes made in on_render()
            pygame.display.update()
            # handle events
            for event in pygame.event.get():
                self.on_event(event)
        # clean up everything that might mess up something later
        self.on_cleanup()

if __name__ == "__main__" :
    theApp = App(16 * 64,16 * 64)
    # start theApp
    theApp.on_execute()
