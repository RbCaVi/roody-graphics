import pygame

f = '/home/rvail/Desktop/games/Roody2d demo - spark/Roody2d Demo/content/save_templates/demo_world'

chs = rsv2.readall(f)

ch = chs[(0,0)]

im = pygame.Surface((w,h))
im.blit(tiles,(x,y),(tx,ty,w,h))

# displaying only belts
class App:
    def __init__(self, width, height):
        # initialize variables
        self.clock = pygame.time.Clock()
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = width, height
        self.frame=0
 
    def on_init(self):
        # start the pygame window
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size)
        self._running = True
    
    def on_event(self, event):
        # when something happens
        if event.type == pygame.QUIT:
            # close the window when the x is clicked
            self._running = False
    
    def on_loop(self):
        # wait to ensure a uniform framerate
        # don't set this too fast, or the framerate won't be the same all the time
        self.clock.tick(30)
        self.frame+=1
    
    def on_render(self):
        # fill the screen with black
        self._display_surf.fill((0,0,0))
    
    def on_cleanup(self):
        # close the pygame window
        pygame.quit()
 
    def on_execute(self):
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
    theApp = App(300,300)
    # start theApp
    theApp.on_execute()