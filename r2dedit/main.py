import pygame
import block
import rsv2
import typing
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

def getarea(chs: rsvedit.Chunks, srect: tuple[int, int, int, int]) -> list[list[rsvedit.Block]]:
    x1,y1,x2,y2 = srect
    return [
        [
            rsvedit.getblock(chs, x, y)
            for x in range(x1, x2 + 1)
        ]
        for y in range(y1, y2 + 1)
    ]

def setarea(chs: rsvedit.Chunks, area: list[list[rsvedit.Block]], x: int, y: int) -> None:
    for yi,row in enumerate(area):
        for xi,block in enumerate(row):
            rsvedit.setblock(chs, x + xi, y + yi, block)

class Tool(typing.Protocol):
    def activate(self) -> None:
        return

    def event(self, app: "App", event: pygame.event.Event) -> bool: # did this tool consume the event?
        return False

    def draw(self, app: "App") -> None:
        return

class WeldTool(Tool):
    def event(self, app: "App", event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1 left
            # 2 middle
            # 3 right
            # 4 scroll up
            # 5 scroll down
            if event.button == 1 or event.button == 3:
                x,y = spostowpos(event.pos, app.t)
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
                if not (pygame.key.get_mods() & pygame.KMOD_CTRL): # ctrl to weld/unweld only one side
                    a,b,c,d,e = rsvedit.getblock(chs, xi+dxy[side][0], yi+dxy[side][1])
                    mask = 1 << (side2 + 4)
                    b = b & ~mask
                    if event.button == 1:
                        b = b | mask
                    rsvedit.setblock(chs, xi+dxy[side][0], yi+dxy[side][1], (a,b,c,d,e))
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v: # v
                if event.mod & pygame.KMOD_CTRL: # + ctrl
                    app.activate(app.paste) # the paste tool either overrides this one or deactivates and restores it
                    app.deactivate(self)
                    return True
            if event.key == pygame.K_w: # w toggles weld/select
                app.activate(app.select)
                app.deactivate(self)
                return True
        return False

class SelectTool(Tool):
    srect: tuple[int, int, int, int] | None

    def activate(self) -> None:
        self.srect = None

    def event(self, app: "App", event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1 left
            # 2 middle
            # 3 right
            # 4 scroll up
            # 5 scroll down
            if event.button == 1: # select is only left mouse
                x,y = spostowpos(event.pos, app.t)
                x = math.floor(x)
                y = math.floor(y)
                self.srect = (x, y, x, y)
                return True
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[0]: # left mouse to select
                if self.srect is None:
                    return False
                x,y = spostowpos(event.pos, app.t)
                x = math.floor(x)
                y = math.floor(y)
                self.srect = (min(self.srect[0], x), min(self.srect[1], y), max(self.srect[2], x), max(self.srect[3], y))
                return True
            if event.buttons[2]: # right mouse to cancel
                self.srect = None
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v: # v
                if event.mod & pygame.KMOD_CTRL: # + ctrl
                    app.activate(app.paste) # the paste tool either overrides this one or deactivates and restores it
                    app.paste.prevtool = self
                    app.deactivate(self)
                    return True
            if event.key == pygame.K_w:
                app.activate(app.weld)
                app.deactivate(self)
                return True
            if event.key == pygame.K_c: # copy selected area
                if event.mod & pygame.KMOD_CTRL:
                    if self.srect is not None:
                        app.clipboard = getarea(chs, self.srect)
                    return True
        return False

    def draw(self, app: "App") -> None:
        if self.srect is None:
            return
        sx,sy = spostowpos((0, 0), app.t)
        x1,y1 = self.srect[0] - sx, self.srect[1] - sy
        x2,y2 = self.srect[2] - sx + 1, self.srect[3] - sy + 1
        pygame.draw.rect(app._display_surf, (230, 255, 230), (x1 * 16, y1 * 16, (x2 - x1) * 16, (y2 - y1) * 16), 2)

class PasteTool(Tool):
    prevtool: Tool

    def event(self, app: "App", event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1 left
            # 2 middle
            # 3 right
            # 4 scroll up
            # 5 scroll down
            if event.button in [1, 3]: # right click to cancel
                if event.button == 1: # left click to paste
                    x,y = spostowpos(event.pos, app.t)
                    x = math.floor(x)
                    y = math.floor(y)
                    setarea(chs, app.clipboard, x, y) # paste the clipboard to the world
                app.activate(self.prevtool)
                app.deactivate(self) # go back to the original tool
                return True
        return False

    def draw(self, app: "App") -> None:
            blocks = [
                [
                    typing.cast(block.BlockData,{
                        'id':a,
                        'weld':[
                            block.makeweldside((b >> n & 1) == 1)
                            for n in [4,7,6,5]
                        ],
                        'rotate':[0,3,2,1][c & 3]
                    })
                    for a,b,c,d,e in row
                ]
                for row in app.clipboard
            ]
            ims = block.makeimage(blocks)
            mx,my = pygame.mouse.get_pos()
            for im,x,y in ims:
                app._display_surf.blit(im, (x + mx, y + my))
            # halve the alpha too
            ...

class WindowTool(Tool):
    rect: pygame.Rect
    capture: bool
    capturedrag: bool

    def __init__(self, w, h):
        self.rect = pygame.Rect(0, 0, w, h)
        self.capture = False
        self.capturedrag = False

    def event(self, app: "App", event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.capture = True # other tools can't be used while this one is being used
                if self.windowevent(app, event): # the contents of this window captured the event
                    return True
                if event.button == 1: # start drag (only if something inside the window didn't already capture the event)
                    self.capturedrag = True
                return True
        if event.type == pygame.MOUSEBUTTONUP:
            if self.capture:
                self.windowevent(app, event)
                if event.button == 1:
                    self.capture = False
                    self.capturedrag = False
                return True
            else:
                return False
        if event.type == pygame.MOUSEMOTION:
            if self.capturedrag:
                self.rect.move_ip(event.rel)
                self.rect.clamp_ip(app._display_surf.get_rect())
                return True
            if self.capture:
                self.windowevent(app, event)
                return True
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.windowevent(app, event)
            return True
        if self.outevent(app, event):
            return True
        return False

    def draw(self, app: "App") -> None:
        pygame.draw.rect(app._display_surf, (255, 0, 0), self.rect)
        self.windowdraw(app)

    def outevent(self, app: "App", event: pygame.event.Event) -> bool: # an event not inside the bounds of the window
        return False

    def windowevent(self, app: "App", event: pygame.event.Event) -> bool: # an event inside the bounds of the window
        return False

    def windowdraw(self, app: "App") -> None:
        return

def subpos(base: tuple[int, int], pos: tuple[int, int]) -> tuple[int, int]:
    return pos[0] - base[0], pos[1] - base[1]

class BlockWindowTool(WindowTool):
    def outevent(self, app: "App", event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                x,y = spostowpos(pygame.mouse.get_pos(), app.t)
                xi,xf = intfrac(x)
                yi,yf = intfrac(y)
                print(rsvedit.getblock(chs, xi, yi))
            return True
        return False

    def windowevent(self, app: "App", event: pygame.event.Event) -> bool:
        return False

    def windowdraw(self, app: "App") -> None:
        return

class App:
    clock: pygame.time.Clock
    _running: bool
    _display_surf: pygame.Surface
    size: tuple[int, int]
    width: int
    height: int
    t: tuple[int, int]
    clipboard: list[list[rsvedit.Block]]
    paste: PasteTool
    weld: Tool
    select: Tool
    window: Tool
    tools: list[tuple[bool, Tool]]

    def __init__(self, width: int, height: int) -> None:
        # initialize variables
        self.clock = pygame.time.Clock()
        self._running = True
        self.size = self.width, self.height = width, height
        self.t = (0, 0)
        self.weld = WeldTool()
        self.select = SelectTool()
        self.paste = PasteTool()
        self.window = BlockWindowTool(50, 50)
        self.tools = [(True, self.window), (True, self.weld), (False, self.select), (False, self.paste)]
        self.clipboard = []
 
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
            return
        if event.type == pygame.MOUSEMOTION:
            if event.buttons[1]: # middle mouse drag to move
                dx,dy = event.rel
                self.t = (self.t[0] + dx, self.t[1] + dy)
                return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: # save
                print('Saving!')
                rsv2.writeall(f, chs)
                return
        for active,tool in self.tools:
            if not active:
                continue
            if tool.event(self, event): # captured
                return

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
                    typing.cast(block.BlockData,{
                        'id':a,
                        'weld':[
                            block.makeweldside((b >> n & 1) == 1)
                            for n in [4,7,6,5]
                        ],
                        'rotate':[0,3,2,1][c & 3]
                    })
                    for x in range(sxf, sxf + math.ceil(self.width / 16) + 1)
                    for a,b,c,d,e in (rsvedit.getblock(chs,x,y),)
                ]
                for y in range(syf, syf + math.ceil(self.height / 16) + 1)
            ]
        with Timer('mkimg'):
            ims = block.makeimage(blocks)
        with Timer('blit'):
            for im,x,y in ims:
                self._display_surf.blit(im, (x - sxd * 16, y - syd * 16))
        
        for active,tool in self.tools:
            if not active:
                continue
            tool.draw(self)
    
    def on_cleanup(self) -> None:
        # close the pygame window
        pygame.quit()
 
    def on_execute(self) -> None:
        if not self.on_init():
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

    def activate(self, tool: Tool) -> None:
        for i,(active,t) in enumerate(self.tools):
            if t is tool:
                tool.activate()
                self.tools[i] = True, tool

    def deactivate(self, tool: Tool) -> None:
        for i,(active,t) in enumerate(self.tools):
            if t is tool:
                self.tools[i] = False, tool

if __name__ == "__main__" :
    theApp = App(16 * 64,16 * 64)
    # start theApp
    theApp.on_execute()
