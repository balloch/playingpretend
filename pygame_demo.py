"""
A pygame script that displays images in the 'images' directory, and shows the option to click 'forward', 'left', or 'right' to change the image. 
"""

import pygame
import os
import time


class Node:
    """
    a class that represents a node in a graph
    """
    def __init__(self, data=None, neighbors=None) -> None:
        self.data = data
        self.neighbors = neighbors

    def __repr__(self) -> str:
        return f"Node({self.data})"


class ImageGraph:
    """
    a class that builds and enables navigation of a graph of images
    """
    def __init__(self, start_image='outerkitchen.jpg', image_directory='images') -> None:
        if not start_image:
            self.current_image = pygame.image.load(os.path.join(image_directory, start_image))
        

    def left(self):
        pass

    def right(self):
        pass

    def forward(self):
        pass

    def back(self):
        pass



def run_game():


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
    run_game()