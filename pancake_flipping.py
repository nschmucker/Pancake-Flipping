"""
pancake_flipping.py
This file runs The Harried Waiter game.
Developed on Python 3.7.6
Nathaniel Schmucker
"""

import pygame
import random

# --- Global constants ---
BLACK    = (  0,   0,   0)
WHITE    = (255, 255, 255)
LT_BROWN = (236, 162,  77)
DK_BROWN = (180,  83,  38)

SCREEN_WIDTH  = 750
SCREEN_HEIGHT = 550

# Regular: https://oeis.org/A058986
# Burned:  https://oeis.org/A078941
DIAMETER = {
    1: {"regular": 0, "burned": 1},
    2: {"regular": 1, "burned": 4},
    3: {"regular": 3, "burned": 6},
    4: {"regular": 4, "burned": 8},
    5: {"regular": 5, "burned": 10},
    6: {"regular": 7, "burned": 12},
    7: {"regular": 8, "burned": 14},
    8: {"regular": 9, "burned": 15},
    9: {"regular": 10, "burned": 17},
    10: {"regular": 11, "burned": 18},
    11: {"regular": 13, "burned": 19},
    12: {"regular": 14, "burned": 21}
}

INFO_TEXT = [
    """
    How to play:
    1. Click on any pancake to flip it and the pancakes above it
    2. In as few moves as possible, try to get the stack in order from smallest to
        largest (smallest at the top) with burnt sides down (when playing with burnt 
        pancakes)
    3. When you win, a fresh stack appears

    Notes:
     - Click the "Reset" button to return the stack to its original order and set 
        the moves counter to 0
     - Click the "Burned?" button to toggle between normal and burned pancake 
        versions of the game
     - Click the "More food" and "Less food" buttons to change the number of 
        pancakes
    """,
    """
    In a 1975 issue of The American Mathematical Monthly, an American Geometer 
    named Jacob Goodman posed an "Elementary Problem" under the pseudonym 
    of Harry Dweighter (read his name aloud...):
    
    "The chef in our place is sloppy, and when he prepares a stack of pancakes they 
    come out all different sizes. Therefore, when I deliver them to a customer, on the
    way to the table I rearrange them (so that the smallest winds up on top, and so 
    on, down to the largest on the bottom) by grabbing several from the top and 
    flipping them over, repeating this (varying the number I flip) as many times as 
    necessary. If there are n pancakes, what is the maximum number of flips (as a 
    function of n) that I will ever have to use to rearrange them?"
    """
    , """
    This question is a variation on the general sorting problem, where the only 
    permissible operation is _prefix reversal_, that is, if we consider the order of the 
    stack a sequence (1, 2, ..., n) the reversal of the elements of some prefix of the 
    sequence. Sequence A058986 describes the maximum number of flips required 
    for stacks of pancakes up to 19.

    Of an interesting historical note, the only academic mathematics paper published 
    by William H. Gates (aka Bill Gates...yes, him.) concerns pancake flipping. In a 
    1979 issue of Discrete Mathematics, he published a paper in conjunction with 
    Christos H. Papadimitriou, which placed an upper bound of (5 * n + 5) / 3, which
    was subsequently improved to (18 / 11) * n by a separate team of researchers. 
    The current estimate is between (15 / 14) * n and (18 / 11) * n, but the exact 
    value is not known.

    Another articulation of the pancake flipping problem involves burnt pancakes, 
    which adds a requirement to the original problem by stipulating that each 
    pancake must end up burnt side down. Sequence A078941 describes the  
    maximum number of flips required for stacks of pancakes up to 12.
    """,
    """
    In the field of graph theory, a graph is a mathematical structure used to model 
    pairwise relations between objects. A graph consists of vertices (or nodes), which 
    are connected by edges. A path is a sequence of edges connecting distinct 
    vertices. The distance between two vertices is the number of edges in the 
    shortest path between them. The diameter of a graph is the longest path 
    between any two vertices.

    A pancake graph, P(n), is a particular type of graph with n! vertices labeled with
    the permutations of (1, 2, ..., n) and whose edges connect vertices that are
    transitive by prefix reversal. Thus a 3 pancake graph would have 3 * 2 * 1 = 6 
    vertices labeled (1, 2, 3), (2, 1, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), and (3, 2, 1); 
    vertex (1, 2, 3), for example, would have edges with vertices (2, 1, 3) and (3, 2, 1).
    """,
    """
    In this arrangement, each vertex represents a particular ordering of a stack of
    pancakes, with the first element in the list at the top of the stack. A properly
    ordered stack would be the identity permutation, (1, 2, ..., n). A path from vertex 
    A to B is a sequence of spatula flips to get from one arrangement of pancakes to 
    another. The pancake flipping problem, which counts the most flips necessary to 
    order a stack of n pancakes, is the same as calculating the diameter of the 
    pancake graph, P(n).

    In the burnt pancake variation, the vertices a signed (+ or -) and with each prefix 
    reversal, the sign of the flipped pancakes changes. This graph has n! * 2^n vertices.
    """,
]

# --- Classes ---
class Graph:
    """ This class represents a pancake graph, P(n). Since the graph has
        up to n! * 2^n vertices, we don't store the entire set of 
        vertices and edges. Instead, we have methods designed for 
        traversing from vertex A to vertex B using a variation of 
        Breadth First Searching knowns as Dijkstra's Algorithm. We start
        with a single vertex and only track vertices that are discovered
        during the BFS.
        The class has methods for running BFS, seeking which vertices
        have been discovered, and reporting the length of the shortest
        path from A to B, as well as the vertices on the path.
        The class accepts burnt pancakes. Edges are unweighted.
    """

    def __init__(self, start, goal, burnt):
        self.start = start
        self.goal = goal
        self.burnt = burnt
        self.visited = {}
        self.fewest_moves = None
        self.best_path = []

    def flip(self, vertex_name, n_to_flip):
        """ Given a vertex and an index, perform prefix reversal. """
        
        new_vertex_name = []
        if self.burnt:
            b = -1
        else:
            b = 1

        # Loop through the vertex and reverse the order (and possibly 
        # sign) of the first n_to_flip items (0-indexed)
        for i in range(len(vertex_name)):
            if i <= n_to_flip:
                j = n_to_flip - i
                new_vertex_name.append(vertex_name[j]*b)
            else:
                j = i
                new_vertex_name.append(vertex_name[j])
        return new_vertex_name
    
    def make_vertex_key(self, vertex_name):
        """ Translate from [int, int, int] to "str:str:str". """

        return ":".join([str(i) for i in vertex_name])
        
    def make_vertex_name(self, vertex_key):
        """ Translate from "str:str:str" to [int, int, int]. """

        return [int(i) for i in vertex_key.split(":")]
        
    def find_neighbors(self, vertex_key):
        """ Given a vertex_key, provide a list of all neighboring
            vertex_keys, where neighbors are reachable via prefix
            reversal.
        """

        neighbors = []
        
        # Since the algorithm only call this method on visited vertices,
        # we can use the dictionary to get the name.
        vertex_name = self.visited[vertex_key]["name"]

        # Complete all possible prefix reversals and append the 
        # vertex_keys to our list.
        for i in range(len(vertex_name)):
            neighbor = self.flip(vertex_name, i)
            neighbor = self.make_vertex_key(neighbor)
            neighbors.append(neighbor)
        
        return neighbors

    def BFS(self):
        """ We implement a version of Dijkstra's Algorithm,
            (https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm), 
            which modifies the typical Breadth First Search algorithm
            to find the shortest path between two vertices on a graph.
        """
        # Clear the list of visited vertices
        self.visited = {}

        # Create a queue
        queue = []

        # Mark the start vertex as visited and enqueue it 
        start_key = self.make_vertex_key(self.start)
        self.visited[start_key] = {
            "name": self.start,
            "dist": 0,
            "prev": None
        }
        queue.append(start_key) 

        while queue: 
            # Dequeue a vertex from queue
            vertex_key = queue.pop(0)

            # If the vertex is the goal vertex, update our knowledge
            # of the shortest path and the vertices on the path
            if vertex_key == self.make_vertex_key(self.goal):
                self.fewest_moves = self.visited[vertex_key]["dist"]
                self.best_path = self.traceback()
                
            # Get all adjacent vertices of the dequeued vertex. If
            # an adjacent vertex has not been visited, then mark it
            # visited and enqueue it.
            # 
            # If it has already been visited, the new path will be
            # longer. If not, the new path is one more than how we got 
            # to our current location. 
            else:
                for i in self.find_neighbors(vertex_key): 
                    if i not in self.visited:
                        self.visited[i] = {
                            "name": self.make_vertex_name(i),
                            "dist": self.visited[vertex_key]["dist"] + 1,
                            "prev": vertex_key
                        }
                        queue.append(i)
    
    def traceback(self):
        """ Generate a list of vertex_keys on the shortest path from
            start to goal.
        """

        # Starting from the end, work our way from prev to prev until
        # we reach the start
        sequence = []
        i = self.make_vertex_key(self.goal)
        while i is not None:
            sequence.insert(0, i) # Insertion into the front of list
            i = self.visited[i]["prev"]
        
        return sequence


class Pancake(pygame.sprite.Sprite):
    """ This class represents a side of a Pancake.
        In the game each Pancake has two objects of this class, one that
        is the top side and one that is the bottom side so that we can 
        color appropriately for burned-ness.
    """
 
    def __init__(self, n, loc, stack_size, side, burnt):
        """ Create the image of the Pancake. """

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
        elif ((self.side == 1 and self.n > 0) 
            or (self.side == -1 and self.n < 0)):
            self.image.fill(LT_BROWN)
        else:
            self.image.fill(DK_BROWN)

        # Fetch the rectangle object that has the dimensions of the 
        # image. Update the position object by setting values of 
        # rect_*.x and rect_*.y
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
        """ If Pancake was the top (1), make bottom (-1). """

        self.side = -self.side
    
    def update_y(self):
        """ Reposition Pancake based on side and location. """

        if self.side == 1:
            self.rect.y = (SCREEN_HEIGHT - 50) - (30 * (self.stack_size - self.loc))
        else: 
            self.rect.y = (SCREEN_HEIGHT - 50) - (30 * (self.stack_size - self.loc)) + 10
    
    def update(self, n_to_flip):
        """ Flip Pancake if it is at the top of the stack. """

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

        self.function = function    # e.g. reset_stack

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        surf.blit(self.text, self.text_rect)


class Game(object):
    """ This class represents an instance of the game. If we need to
        restart the game, we create a new instance of this class.
    """
 
    def __init__(self, stack_size, burnt, font):
        """ Create all our attributes to initialize the game. """

        self.pos = [-1,-1]
        self.show_info = False
        self.info_item = -1
        self.moves = 0
        self.stack_size = stack_size
        self.burnt = burnt
        self.font = font
        self.game_over = False

        # Create lists to track order of stack
        # This is how the order should be when we win
        self.goal_order = list(range(1, self.stack_size+1))
        
        # This is the random starting order
        # Ensure we aren't starting with a winning arrangement
        self.start_order = self.goal_order.copy()
        while self.start_order == self.goal_order:
            # Get a random ordering of pancakes
            order = self.goal_order.copy()
            random.shuffle(order)
            
            # Get a random ordering of burntness
            if self.burnt:
                signs = random.choices([-1,1], k=self.stack_size)
            else:
                signs = [1]*self.stack_size
            
            # Use the two to create the random starting order
            self.start_order = []
            for i, j in zip(order, signs):
                self.start_order.append(i*j)

        # This is the current order (will change with each move)
        self.current_order = self.start_order.copy()

        # Generate the pancake_graph and run BFS if it won't take long
        self.pancake_graph = Graph(self.start_order, self.goal_order, self.burnt)
        if self.BFS_eligible():
            self.pancake_graph.BFS()

        # Buttons for controling gameplay
        button_dict = {
            "b1": { # Reset to original Pancake order
                "rect": (SCREEN_WIDTH-120, 10, 110, 30),
                "text": "Reset stack",
                "font": font,
                "function": self.reset_stack
            },
            "b2": { # Toggle between regular/burned versions
                "rect": (SCREEN_WIDTH-120, 45, 110, 30),
                "text": "Burned?",
                "font": font,
                "function": self.toggle_burntness
            },
            "b3": {
                "rect": (SCREEN_WIDTH-120, 80, 110, 30),
                "text": "More food",
                "font": font,
                "function": self.add_pancake
            },
            "b4": {
                "rect": (SCREEN_WIDTH-120, 115, 110, 30),
                "text": "Less food",
                "font": font,
                "function": self.remove_pancake
            },
            "b5": { # Show screen with info about the game
                "rect": (SCREEN_WIDTH-120, SCREEN_HEIGHT-45, 110, 30),
                "text": "Teach me",
                "font": font,
                "function": self.display_info
            },
        }

        # Buttons for controling what info text we display
        info_button_dict = {
            "b1": {
                "rect": (SCREEN_WIDTH-120, SCREEN_HEIGHT-45, 110, 30),
                "text": "Close",
                "font": font,
                "function": self.close_info
            },
            "b2": {
                "rect": (SCREEN_WIDTH-240, SCREEN_HEIGHT-45, 110, 30),
                "text": "Next",
                "font": font,
                "function": self.next_info
            },
            "b3": {
                "rect": (SCREEN_WIDTH-360, SCREEN_HEIGHT-45, 110, 30),
                "text": "Back",
                "font": font,
                "function": self.previous_info
            },
        }

        # Create lists for Buttons and sprite list for Pancakes
        self.button_list = []
        self.info_button_list = []
        self.pancake_list = pygame.sprite.Group()

        # Generate all Buttons and Pancakes; add to appropriate lists
        self.make_buttons(button_dict=button_dict)
        self.make_info_buttons(button_dict=info_button_dict)
        self.make_pancake_stack()

    def BFS_eligible(self):
        """ Return True if it won't take too long to run the BFS. """
        
        return (not self.burnt and self.stack_size < 8
            or self.burnt and self.stack_size < 6)

    def make_buttons(self, button_dict):
        """ For each item in dictionary, make a Button (gameplay). """

        for key in button_dict:
            button = Button(**button_dict[key])
            self.button_list.append(button)

    def make_info_buttons(self, button_dict):
        """ For each item in dictionary, make a Button (info). """

        for key in button_dict:
            button = Button(**button_dict[key])
            self.info_button_list.append(button)

    def make_pancake_stack(self):
        """ For each slot in stack, make a Pancake sprite. """

        # Top half of each Pancake (side = 1)
        for i in range(self.stack_size):
            pancake = Pancake(
                self.current_order[i], i,
                self.stack_size, 1, self.burnt
            )
            self.pancake_list.add(pancake)
        
        # Bottom half of each Pancake (side = -1)
        for i in range(self.stack_size):
            pancake = Pancake(
                self.current_order[i], i,
                self.stack_size, -1, self.burnt
            )
            self.pancake_list.add(pancake)  

    def reset_stack(self):
        """ When reset button is clicked, set moves to zero and
            create a fresh stack of Pancakes using start_order.
        """
        
        self.moves = 0
        self.pancake_list.empty()
        self.current_order = self.start_order.copy()
        self.make_pancake_stack() 

    def toggle_burntness(self):
        """ When burntness button is clicked, toggle between burned 
            Pancake and unburned Pancake versions of game. Generate a 
            fresh stack.
        """

        # Generate new instance of w/ opposite burntness
        # We always want 2+ since min size of unburned stack is 2
        self.__init__(max(self.stack_size, 2), not self.burnt, self.font)

    def add_pancake(self):
        """ When button is clicked, generate a fresh stack with 
            n+1 Pancakes.
        """

        # Diamater of pancake graph known for burnt flipping up to n=12
        # Higher for unburned, but we will limit to 12, as that's a lot
        # For reference, see https://oeis.org/A078941
        self.__init__(min(self.stack_size + 1, 12), self.burnt, self.font)

    def remove_pancake(self):
        """ When button is clicked, generate a fresh stack with 
            n-1 Pancakes.
        """

        # Generate a new instance of the game
        # Unburned needs at least 2 Pancakes
        if self.burnt:
            self.__init__(max(self.stack_size-1, 1), self.burnt, self.font)
        else:
            self.__init__(max(self.stack_size-1, 2), self.burnt, self.font)

    def display_info(self):
        """ Open the info screen, starting at the first screen. """
        
        self.info_item =  0
        self.show_info = True

    def close_info(self):
        """ Close the info screens to return to game. """

        self.show_info = False

    def next_info(self):
        """ Advance to the next screen, close if we run out. """
        
        self.info_item += 1
        if self.info_item == len(INFO_TEXT):
            self.close_info()

    def previous_info(self):
        """ Return to the prior screen, close if we run out. """
        
        self.info_item += -1
        if self.info_item == -1:
            self.close_info()

    def draw_long_text(self, screen, font, long_text, xy):
        """ Helper function for bitting multi-line text """
        
        lines = long_text.splitlines()
        for i, l in enumerate(lines):
            text = font.render(l, True, WHITE)
            screen.blit(text, (xy[0], xy[1] + font.get_linesize()*i))
    
    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Get the current mouse position
                self.pos = pygame.mouse.get_pos()

                # After winning, restart on click
                if self.game_over:
                    self.__init__(self.stack_size, self.burnt, self.font)
 
        return False

    def run_logic(self):
        """ This method is run each time through the frame. It checks 
            for Pancake selections and flips them.
        """
            
        if not self.show_info:
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

            # Did we win?
            if self.current_order == self.goal_order:
                self.game_over = True
        
        else:
            # Check for collisions with an info Button and do an action
            for info_button in self.info_button_list:
                if info_button.rect.collidepoint(self.pos):
                    info_button.function()
        
        # "Unclick"
        self.pos = [-1,-1]
 
    def display_frame(self, screen, font):
        """ Display everything to the screen for the game. """
        
        screen.fill(BLACK)
        
        if not self.show_info:
            if not self.game_over:
                for button in self.button_list:
                    button.draw(screen)
            else: 
                text = font.render("You win! Click to restart", True, WHITE)
                center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
                center_y = (SCREEN_HEIGHT - 30) - (text.get_height() // 2)
                screen.blit(text, [center_x, center_y])
        
            if self.BFS_eligible():
                text = font.render(
                    "(Fewest possible moves: "+str(self.pancake_graph.fewest_moves)+")",
                    True, WHITE
                )
                screen.blit(text, [175, 10])
            elif self.burnt:
                text = font.render(
                    "(Possible in "+str(DIAMETER[self.stack_size]["burned"])+" moves or fewer)",
                    True, WHITE
                )
                screen.blit(text, [175, 10])
            else:
                text = font.render(
                    "(Possible in "+str(DIAMETER[self.stack_size]["regular"])+" moves or fewer)",
                    True, WHITE)
                screen.blit(text, [175, 10])

            text = font.render("Current moves: "+str(self.moves), True, WHITE)
            screen.blit(text, [10, 10])

            text = font.render("Start order: "+str(self.start_order), True, WHITE)
            screen.blit(text, [10, 35])

            text = font.render("Current order: "+str(self.current_order), True, WHITE)
            screen.blit(text, [10, 60])

            text = font.render("Goal order: "+str(self.goal_order), True, WHITE)
            screen.blit(text, [10, 85])

            self.pancake_list.draw(screen)

        else:
            for info_button in self.info_button_list:
                info_button.draw(screen)
            
            self.draw_long_text(screen, font, INFO_TEXT[self.info_item], [10, 10])

        pygame.display.flip()


# --- Main function ---
def main():
    """ Main program function """
    
    # Initialize Pygame and set up the window
    pygame.init()
 
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    font = pygame.font.SysFont("calibri", 20, bold=True)
 
    pygame.display.set_caption("The Harried Waiter")

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # Create an instance of the Game class
    game = Game(stack_size=4, burnt=True, font=font)

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