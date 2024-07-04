import pygame
import PIL
import block
import rsv2
import typing
import assetload

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/demo_world'

chs = rsv2.readall(f)

ch = chs[(0,-1)]

# im = pygame.Surface((w,h))
# im.blit(tiles,(x,y),(tx,ty,w,h))

def convertim(im: PIL.Image.Image) -> pygame.Surface:
    return pygame.image.fromstring(im.tobytes(), im.size, typing.cast(typing.Any,im.mode))

class App:
    clock: pygame.time.Clock
    _running: bool
    _display_surf: pygame.Surface | None
    size: tuple[int, int]
    width: int
    height: int

    def __init__(self, width: int, height: int) -> None:
        # initialize variables
        self.clock = pygame.time.Clock()
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = width, height
 
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
                x,y = event.pos
                xi = x // 16
                yi = y // 16
                i = xi + yi * 64
                # clear the appropriate bit
                ch['tiles'][1][i] = ch['tiles'][1][i] & (~ (1 << 4 | 1 << 5 | 1 << 6 | 1 << 7))
    
    def on_loop(self) -> None:
        # wait to ensure a uniform framerate
        # don't set this too fast, or the framerate won't be the same all the time
        self.clock.tick(30)
    
    def on_render(self) -> None:
        assert self._display_surf is not None
        # fill the screen with black
        self._display_surf.fill((0,0,0))
        blocks = [typing.cast(block.BlockDataIn,{'type':assetload.idtoblock[a],'weld':[block.makeweldside((b >> n & 1) == 1) for n in [4,7,6,5]]}) for a,b in zip(ch['tiles'][0],ch['tiles'][1])]
        blocks2 = [blocks[i * 64:(i + 1) * 64] for i in range(64)]
        im = block.makeimage(blocks2,autoweld = False)
        surf = convertim(im)
        self._display_surf.blit(surf,(0,0))
    
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