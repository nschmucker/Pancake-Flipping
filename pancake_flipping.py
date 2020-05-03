"""
pancake_flipping.py
This file runs the Pancake Flipping Game.
Nathaniel Schmucker
"""

# TODO: Add buttons for (1) n pancakes (2) burnt-ness
# TODO: Flip order of image and rect for Button
# TODO: Add text for upper bound
# TODO: Add home screen with directions. Click anywhere to begin
# TODO: Add button to show the "fun stuff" --> Graph theory support

import pygame
import random

# --- Global constants ---
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
LT_BROWN = (236, 162,  77)
DK_BROWN = (180,  83,  38)

SCREEN_WIDTH  = 700
SCREEN_HEIGHT = 500

# --- Classes ---
class Pancake(pygame.sprite.Sprite):
    """ This class represents a side of a Pancake.
        In the game each Pancake has two objects of this class, one that
        is the top side and one that is the bottom side so that we can 
        color appropriately for burned-ness. 
    """
 
    def __init__(self, n, loc, stack_size, side, burnt):
        """ Create the image of the Pancake """

        # Call the parent class (Sprite) constructor
        super().__init__()

        self.n = n     # 1-indexed, may be [-n, ..., -1] or [1, ..., n]
        self.loc = loc # 0-indexed, may be [0, ..., n-1]
        self.stack_size = stack_size
        self.side = side   # Side facing up = 1
        self.burnt = burnt # Does not change during life of Pancake

        # Create an image of the Pancake, and fill it with a color.
        self.image = pygame.Surface([100 + 30 * abs(self.n), 10])
        if not self.burnt:
            self.image.fill(LT_BROWN)
        elif (self.side == 1 and self.n > 0) or (self.side == -1 and self.n < 0):
            self.image.fill(LT_BROWN)
        else:
            self.image.fill(DK_BROWN)

        # Fetch the rectangle object that has the dimensions of the image.
        # Update the position object by setting values of rect_*.x and rect_*.y
        self.rect = self.image.get_rect()
        self.rect.x = (SCREEN_WIDTH // 2) - ((100 + 30 * abs(self.n)) // 2)
        if self.side == 1:
            self.rect.y = (SCREEN_HEIGHT - 50) - (30 * (self.stack_size - self.loc))
        else: 
            self.rect.y = (SCREEN_HEIGHT - 50) - (30 * (self.stack_size - self.loc)) + 10

    def update_n(self):
        """ If Panckes are burned, invert n. """

        if self.burnt:
            self.n = -self.n

    def update_loc(self, n_to_flip):
        """ Reposition Pancake: n <-> 0, n-1 <-> 1, etc. """

        self.loc = n_to_flip - self.loc - 1

    def update_side(self):
        """ If Pancake was the top (1), make bottom (-1) """

        self.side = -self.side
    
    def update_y(self):
        """ Reposition Pancake based on side and location """

        if self.side == 1:
            self.rect.y = (SCREEN_HEIGHT - 50) - (30 * (self.stack_size - self.loc))
        else: 
            self.rect.y = (SCREEN_HEIGHT - 50) - (30 * (self.stack_size - self.loc)) + 10
    
    def update(self, n_to_flip):
        """ Flip Pancake if it is at the top of the stack """

        if self.loc < n_to_flip:
            self.update_n()
            self.update_loc(n_to_flip)
            self.update_side()
            self.update_y()     # Based on new self.loc and self.side

class Button:
    """ This class is for all the buttons on the screen """

    def __init__(self, rect, text, font, function):
        
        # Call the parent class (Sprite) constructor
        super().__init__()
        
        self.rect = pygame.Rect(rect)
        self.image = pygame.Surface(self.rect.size).convert()
        self.image.fill(DK_BROWN)

        self.text = font.render(text, True, WHITE)
        self.text_rect = self.text.get_rect(center=self.rect.center)

        self.function = function ## e.g. reset_stack

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        surf.blit(self.text, self.text_rect)

class Game(object):
    """ This class represents an instance of the game. If we need to
        restart the game, we create a new instance of this class """
 
    def __init__(self, stack_size, burnt, font):
        """ Create all our attributes to initialize the game """

        self.pos = [0,0]
        self.moves = 0
        self.stack_size = stack_size
        self.burnt = burnt
        self.font = font
        self.game_over = False

        # Create lists to track order of stack
        # This is how the order should be when we win
        self.goal_order = list(range(1,self.stack_size+1))
        
        # This is the random starting order
        order = self.goal_order.copy()
        random.shuffle(order)
        if self.burnt:
            signs = random.choices([-1,1], k=self.stack_size)
        else:
            signs = [1]*self.stack_size
        
        self.start_order = []
        for i, j in zip(order, signs):
            self.start_order.append(i*j)

        # Ensure we aren't starting with a winning arrangement
        while self.start_order == self.goal_order:
            random.shuffle(self.start_order)

        # This is the current order (will change with each move)
        self.current_order = self.start_order.copy()

        # Create list for Buttons and sprite list for Pancakes
        self.button_list = []
        self.pancake_list = pygame.sprite.Group()

        # Make our game Buttons
        # Reset button
        button = Button((SCREEN_WIDTH - 120, 10, 110, 30), "Reset stack", font, self.reset_stack)
        self.button_list.append(button)

        # # Burnt-ness button
        # button = Button((SCREEN_WIDTH - 120, 45, 110, 30), "Reset stack", font, self.reset_stack)
        # self.button_list.append(button)

        # # No. Pancakes button
        # button = Button((SCREEN_WIDTH - 120, 80, 110, 30), "Reset stack", font, self.reset_stack)
        # self.button_list.append(button)

        # # Graph theory button
        # button = Button((SCREEN_WIDTH - 120, 115, 110, 30), "Reset stack", font, self.reset_stack)
        # self.button_list.append(button)

        # For each slot in stack, make a Pancake sprite
        # Top half of each Pancake (side = 1)
        for i in range(self.stack_size):
            pancake = Pancake(self.current_order[i], i, self.stack_size, 1, self.burnt)
            self.pancake_list.add(pancake)
        
        # Bottom half of each Pancake (side = -1)
        for i in range(self.stack_size):
            pancake = Pancake(self.current_order[i], i, self.stack_size, -1, self.burnt)
            self.pancake_list.add(pancake)

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Get the current mouse position
                self.pos = pygame.mouse.get_pos()

                if self.game_over:
                    self.__init__(self.stack_size, self.burnt, self.font)
 
        return False
 
    def reset_stack(self):
        """ When reset button is clicked, set moves to zero and
            create a fresh stack of Pancakes using start_order """
        
        # Reset moves to 0
        self.moves = 0
        
        # Remove all the Pancake sprites
        self.pancake_list.empty()

        # Reset current order to reflect start order
        self.current_order = self.start_order.copy()

        # For each slot in stack, make a Pancake sprite
        # Top half of each Pancake (side = 1)
        for i in range(self.stack_size):
            pancake = Pancake(self.current_order[i], i, self.stack_size, 1, self.burnt)
            self.pancake_list.add(pancake)
        
        # Bottom half of each Pancake (side = -1)
        for i in range(self.stack_size):
            pancake = Pancake(self.current_order[i], i, self.stack_size, -1, self.burnt)
            self.pancake_list.add(pancake)   

    def run_logic(self):
        """
        This method is run each time through the frame. It checks for 
        Pancake selections and flips them
        """
        if not self.game_over:
            
            # Check for collisions with a Button and do an action
            for button in self.button_list:
                if button.rect.collidepoint(self.pos):
                    button.function()

            # Check for collisions with a Pancake
            pancakes_to_flip = 0
            for pancake in self.pancake_list:
                if pancake.rect.collidepoint(self.pos):
                    pancakes_to_flip = pancake.loc + 1
                    
                    # Record a move
                    self.moves += 1      

            # Update Pancakes
            self.pancake_list.update(pancakes_to_flip) 
            
            # Refresh the current order tracking list
            for pancake in self.pancake_list:
                self.current_order[pancake.loc] = pancake.n

            # "Unclick"
            self.pos = [0,0]

            # Did we win?
            if self.current_order == self.goal_order:
                self.game_over = True
 
    def display_frame(self, screen, font):
        """ Display everything to the screen for the game """
        screen.fill(BLACK)
        
        for button in self.button_list:
            button.draw(screen)
        self.pancake_list.draw(screen)
      
        text = font.render("Moves: "+str(self.moves), True, WHITE)
        screen.blit(text, [10, 10])

        # text = font.render("Start order: "+str(self.start_order), True, WHITE)
        # screen.blit(text, [10, 35])

        # text = font.render("Goal order: "+str(self.goal_order), True, WHITE)
        # screen.blit(text, [10, 60])

        # text = font.render("Current order: "+str(self.current_order), True, WHITE)
        # screen.blit(text, [10, 85])

        if self.game_over:
            text = font.render("You win! Click to restart", True, WHITE)
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT - 30) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])

        pygame.display.flip()

# --- Main function ---
def main():
    """ Main program function """
    
    # Initialize Pygame and set up the window
    pygame.init()
 
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    font = pygame.font.SysFont("calibri", 20, bold=True)
 
    pygame.display.set_caption("Pancake Flipping")

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Create an instance of the Game class
    game = Game(4, True, font)

    # Loop until player exits window
    done = False

    # Main game loop
    while not done:
 
        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()
 
        # Update object positions
        game.run_logic()
 
        # Draw the current frame
        game.display_frame(screen, font)
 
        # Limit to 60 frames per second
        clock.tick(60)
 
    # Close window and exit
    pygame.quit()

# Call the main function, start up the game
if __name__ == "__main__":
    main()