"""
A pygame script that displays images in the 'images' directory, and shows the option to click 'forward', 'left', or 'right' to change the image. 
"""

import pygame
import os
import time
from pathlib import Path


DIRECTIONS = ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw']


class Node:
    """
    a class that represents a node in a graph
    """
    def __init__(self, filedata=None, root=False, neighbors=None, envname='kitchen') -> None:
        self.filedata = Path(filedata)
        self.name = self.filedata.stem
        self.directory = self.filedata.parent
        self.neighbors = neighbors
        if self.neighbors is None:
            self.neighbors = [Path(f).stem for f in os.listdir(self.directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.left = None
            self.right = None
            self.back = None
            self.front = None
        else:
            if 'left' in self.neighbors:
                self.left = self.neighbors['left']
            if 'right' in self.neighbors:
                self.right = self.neighbors['right']
            if 'front' in self.neighbors:
                self.front = self.neighbors['front']
            if 'back' in self.neighbors:
                self.back = self.neighbors['back']
            
        if root is False:
            self.position = int(self.name[len(envname)])
            self.direction = DIRECTIONS.index(self.name[len(envname)+1:])
            self.envname = envname
            # self.find_neighbors()
    
    def find_neighbors(self):
        """
        finds the neighbors of a node based on images in the same directory
        """
        
        position_neighborhood = (self.position-1,self.position, self.position+1)
        for neighbor in self.neighbors:
            if self.envname != neighbor[:len(self.envname)]:
                continue
            pos = int(neighbor[len(self.envname)])
            if pos not in position_neighborhood:
                continue
            dir = DIRECTIONS.index(neighbor[len(self.envname)+1:])
            if dir == (self.direction + 1) % len(DIRECTIONS)  and pos == self.position:
                self.right = neighbor
            elif dir == (self.direction + 2) % len(DIRECTIONS) and pos == self.position and self.right is None: 
                self.right = neighbor
            elif dir == (self.direction - 1) % len(DIRECTIONS) and pos == self.position:
                self.left = neighbor
            elif dir == (self.direction - 2) % len(DIRECTIONS) and pos == self.position and self.left is None: 
                self.left = neighbor
            elif dir == self.direction and pos == self.position+1:
                self.front = neighbor
            elif dir == self.direction and pos == self.position-1 :
                self.back = neighbor
            else:
                continue

    def __repr__(self) -> str:
        return f"Node({self.filedata})"



class ImageGraph:
    """
    a class that builds and enables navigation of a graph of images
    """
    def __init__(self, start_image='outerkitchen.jpg', image_directory='images', next_node=None) -> None:
        self.start_node = Node(filedata=os.path.join(image_directory,start_image), root=True)
        self.curr_node = self.start_node
        self.node_list = []
        if next_node is not None:
            self.start_node.left = next_node
            self.start_node.right = next_node
            self.start_node.front = next_node
            self.start_node.back = next_node
            self.node_list.append(next_node)
        self.image_directory = image_directory

    def addnodesfromdir(self, envname='kitchen'):
        image_nodes = [f for f in os.listdir(self.image_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        for image_file in image_nodes:
            if envname != image_file[:len(envname)]:
                continue
            new_node = Node(os.path.join(self.image_directory,image_file))


            ##
            ## This stuff should be in "addnode" below
            ##
            image = new_node.name
            pos = int(image[len(envname)])
            position_imagehood = (pos-1,pos, pos+1)
            dir = DIRECTIONS.index(image[len(envname)+1:])
            for node in self.node_list:
                if node.position not in position_imagehood:
                    continue
                if dir == (node.direction + 1) % len(DIRECTIONS)  and pos == node.position:
                    new_node.right = node
                elif dir == (node.direction + 2) % len(DIRECTIONS) and pos == node.position and new_node.right is None: 
                    new_node.right = node
                elif dir == (node.direction - 1) % len(DIRECTIONS) and pos == node.position:
                    new_node.left = node
                elif dir == (node.direction - 2) % len(DIRECTIONS) and pos == node.position and new_node.left is None: 
                    new_node.left = node
                elif dir == node.direction and pos == node.position+1:
                    new_node.front = node
                elif dir == node.direction and pos == node.position-1 :
                    new_node.back = node
                else:
                    continue
            self.node_list.append(new_node)
            if len(self.node_list) == 2:
                self.start_node.left = new_node
                self.start_node.right = new_node
                self.start_node.front = new_node
                self.start_node.back = new_node

    def addnode(self):
        pass

    def left(self):
        self.curr_node = self.curr_node.left

    def right(self):
        self.curr_node = self.curr_node.right

    def forward(self):
        self.curr_node = self.curr_node.front

    def back(self):
        self.curr_node = self.curr_node.back



def run_game(graph=None):


    # Initialize Pygame
    pygame.init()

    # Set up display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Image Viewer')

    # Load images from the 'images' directory
    image_directory = 'images'
    image_files = [f for f in os.listdir(image_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    current_image_index = 0

    # Load the first image
    if graph:
        current_image = pygame.image.load(graph.start_node.filedata)
    else:  ## For testing only, to be deleted
        current_image = pygame.image.load(os.path.join(image_directory, image_files[current_image_index]))
    current_image = pygame.transform.scale(current_image, (screen_width, screen_height))

    # Load button images
    button_forward = pygame.image.load('forward_button.jpg')  # Provide your button image paths
    button_left = pygame.image.load('left_button.jpg')
    button_right = pygame.image.load('right_button.jpg')

    # Resize button images
    button_width, button_height = 50, 50
    button_forward = pygame.transform.scale(button_forward, (button_width, button_height))
    button_left = pygame.transform.scale(button_left, (button_width, button_height))
    button_right = pygame.transform.scale(button_right, (button_width, button_height))

    # Position buttons
    button_x = (screen_width - button_width) // 2
    button_y = screen_height - button_height - 20
    button_spacing = 20

    # Run the game loop
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if graph:
                    if event.key == pygame.K_LEFT:
                        graph.left()
                    elif event.key == pygame.K_RIGHT:
                        graph.right()
                    elif event.key == pygame.K_UP:
                        graph.forward()
                    current_image = pygame.image.load(graph.curr_node.filedata)

                else: ## For testing only, to be deleted
                    if event.key == pygame.K_LEFT:
                        current_image_index = (current_image_index - 1) % len(image_files)
                    elif event.key == pygame.K_RIGHT:
                        current_image_index = (current_image_index + 1) % len(image_files)
                    elif event.key == pygame.K_UP:
                        current_image_index = (current_image_index + 8) % len(image_files)

                    current_image = pygame.image.load(os.path.join(image_directory, image_files[current_image_index]))
                current_image = pygame.transform.scale(current_image, (screen_width, screen_height))

        # Clear the screen
        screen.fill((0, 0, 0))

        # Draw the current image
        screen.blit(current_image, (0, 0))

        # Draw buttons
        screen.blit(button_forward, (button_x, button_y - button_height - button_spacing))
        screen.blit(button_left, (button_x - button_width - button_spacing, button_y))
        screen.blit(button_right, (button_x + button_width + button_spacing, button_y))

        pygame.display.flip()
        clock.tick(60)

    # Clean up
    pygame.quit()


if __name__ == '__main__':

    test = False
    if test == True:
        # make graph
        graph = ImageGraph()
        sample_node = Node('images/kitchen3s')
        print('name', sample_node.name)
        print('dir', sample_node.directory)
        print('position', sample_node.position)
        print('direction', sample_node.direction)
        # print('position', sample_node.position)
        # print('position', sample_node.position)
        sample_node.find_neighbors()
        print(sample_node.left, sample_node.right, sample_node.front, sample_node.back)

        graph.addnodesfromdir()
        print(graph.node_list)

        run_game(graph)
    run_game()