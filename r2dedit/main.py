import pygame
import PIL
import block
import rsv2
import typing
import assetload
import rsvedit
import math
import time

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/demo_world'

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/wires'

chs = rsv2.readall(f)

# im = pygame.Surface((w,h))
# im.blit(tiles,(x,y),(tx,ty,w,h))

class Timer:
    #start

    def __init__(self, s):
        self.s = s

    def __enter__(self):
        self.start = time.time()
        #print(f'{self.s}: start at {self.start}')

    def __exit__(self, exc_type, exc, exc_tb):
        if exc is not None:
            return False
        t = time.time()
        #print(f'{self.s}: ended at {t}')
        #print(f'{self.s}: {t - self.start} seconds')

def spostowpos(spos: tuple[float,float], t: tuple[float,float]) -> tuple[float,float]:
    sx,sy = spos
    tx,ty = t
    x = sx - tx
    y = sy - ty
    x /= 16
    y /= 16
    return x, y

def intfrac(x: float) -> tuple[int,float]:
    i,f = divmod(x, 1)
    assert i == int(i)
    return int(i), f

class App:
    clock: pygame.time.Clock
    _running: bool
    _display_surf: pygame.Surface | None
    size: tuple[int, int]
    width: int
    height: int
    t: tuple[int, int]
    srect: tuple[int, int, int, int]
    tool: str

    def __init__(self, width: int, height: int) -> None:
        # initialize variables
        self.clock = pygame.time.Clock()
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = width, height
        self.t = (0, 0)
        self.tool = 'select'
        self.srect = 0, 0, 0, 0
 
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
            if self.tool == 'weld':
                if event.button == 1 or event.button == 3:
                    x,y = spostowpos(event.pos, self.t)
                    xi,xf = intfrac(x)
                    yi,yf = intfrac(y)
                    xf -= 0.5
                    yf -= 0.5
                    dxy = [
                        ( 0, -1),
                        ( 1,  0),
                        ( 0,  1),
                        (-1,  0),
                    ]
                    if abs(xf) > abs(yf):
                        if xf > 0:
                            side = 1
                        else:
                            side = 3
                    else:
                        if yf > 0:
                            side = 2
                        else:
                            side = 0
                    a,b,c,d,e = rsvedit.getblock(chs, xi, yi)
                    mask = 1 << (side + 4)
                    b = b & ~mask # clear the weld bit
                    if event.button == 1: # if left mouse (weld)
                        b = b | mask # set the weld bit
                    rsvedit.setblock(chs, xi, yi, (a,b,c,d,e))
                    side2 = (side + 2) % 4
                    a,b,c,d,e = rsvedit.getblock(chs, xi+dxy[side][0], yi+dxy[side][1])
                    mask = 1 << (side2 + 4)
                    b = b & ~mask
                    if event.button == 1:
                        b = b | mask
                    rsvedit.setblock(chs, xi+dxy[side][0], yi+dxy[side][1], (a,b,c,d,e))
            elif self.tool == 'select':
                if event.button == 1: # select is only left mouse
                    x,y = spostowpos(event.pos, self.t)
                    x = math.floor(x)
                    y = math.floor(y)
                    self.srect = (x, y, x, y)
            elif self.tool.startswith('paste-') and event.button in [1, 3]:
                if event.button == 1: # left click to paste
                    x,y = spostowpos(event.pos, self.t)
                    x = math.floor(x)
                    y = math.floor(y)
                    setarea(chs, clipboard, x, y) # paste the clipboard to the world
                self.tool = {'paste-s': 'select', 'paste-w': 'weld'}[self.tool] # go back to the original tool
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[1]: # middle mouse drag to move
                dx,dy = event.rel
                self.t = (self.t[0] + dx, self.t[1] + dy)
            if self.tool == 'select':
                if event.buttons[0]: # left mouse to select
                    x,y = spostowpos(event.pos, self.t)
                    x = math.floor(x)
                    y = math.floor(y)
                    srect = (min(self.srect[0], x), min(self.srect[1], y), max(self.srect[2], x), max(self.srect[3], y))
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: # save
                rsv2.writeall(f, chs)
            if event.key == pygame.K_v: # v
                if event.mod & pygame.KMOD_CTRL: # + ctrl
                    if self.tool in ['select', 'weld']:
                        self.tool = {'select': 'paste-s', 'weld': 'paste-w'}[self.tool] # go to paste mode
            if self.tool == 'weld':
                if event.key == pygame.K_w: # w toggles weld/select
                    self.tool = 'select'
            if self.tool == 'select':
                if event.key == pygame.K_w:
                    self.tool = 'weld'
                if event.key == pygame.K_c: # copy selected area
                    if event.mod & pygame.KMOD_CTRL:
                        clipboard = getarea(chs, srect)

    def on_loop(self) -> None:
        # wait to ensure a uniform framerate
        # don't set this too fast, or the framerate won't be the same all the time
        self.clock.tick(30)
    
    def on_render(self) -> None:
        assert self._display_surf is not None
        # fill the screen with black
        self._display_surf.fill((200, 200, 255))
        sx,sy = spostowpos((0, 0), self.t)
        sxf,sxd = intfrac(sx)
        syf,syd = intfrac(sy)
        with Timer('mkblks'):
            blocks = [
                [
                    typing.cast(block.BlockDataIn,{
                        'type':assetload.idtoblock[a],
                        'weld':[
                            block.makeweldside((b >> n & 1) == 1)
                            for n in [4,7,6,5]
                        ]
                    })
                    for x in range(sxf, sxf + math.ceil(self.width / 16) + 1)
                    for a,b,c,d,e in (rsvedit.getblock(chs,x,y),)
                ]
                for y in range(syf, syf + math.ceil(self.height / 16) + 1)
            ]
        with Timer('mkimg'):
            ims = block.makeimage(blocks,autoweld = False)
        with Timer('blit'):
            for im,x,y in ims:
                self._display_surf.blit(im, (x - sxd * 16, y - syd * 16))
        with Timer('select'):
            x1,y1 = self.srect[0] - sx, self.srect[1] - sy
            x2,y2 = self.srect[2] - sx + 1, self.srect[3] - sy + 1
            pygame.draw.rect(self._display_surf, (230, 255, 230, 100), (x1 * 16, y1 * 16, (x2 - x1) * 16, (y2 - y1) * 16))

        if self.tool.startswith('paste-'):
            blocks = makeblockdata(clipboard)
            # halve the alpha too
            ...
    
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
