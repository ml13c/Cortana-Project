import pygame
import sys
import socket
import threading
import spritessheet

# Initialize Pygame
pygame.init()

# Creating weather box
weather_box_width = 180
weather_box_height = 200
weather_box_x = 470
weather_box_y = 80
weather_font = pygame.font.Font('freesansbold.ttf', 12)  # Font for weather information

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700
# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Window")

testaction = "still"
weather_info = ""#set weather info as blank initially
weather_activated = weather_info

def wrap_text(text, font, max_width):
    """Wrap text to fit within a given width when rendered."""
    words = text.split(' ')
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word, True, (255, 255, 255))
        word_width, _ = word_surface.get_size()

        # Check if the current word can fit in the current line
        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width + font.size(' ')[0]  # Add a space between words
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width + font.size(' ')[0]

    # Add the last line
    lines.append(' '.join(current_line))
    
    return lines
#handles the weather data received from the other script
def receive_weather():
    global weather_info
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('localhost', 9998))
        while True:
            data, _ = s.recvfrom(1024)
            weather_info = data.decode()
            print(f"Received weather info: {weather_info}")  # Debugging print

def receive_testaction():
    global testaction
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('localhost', 9999))
        while True:
            data, _ = s.recvfrom(1024)
            testaction = data.decode()

sprite_sheet_image = pygame.image.load('Cortanabit-animationframes.png').convert_alpha()#uses the cortana sprite sheet i made(i need to add more animations/frames)
sprite_sheet = spritessheet.SpriteSheet(sprite_sheet_image)
# Start threads to receive testaction and weather updates
action_receiver_thread = threading.Thread(target=receive_testaction, daemon=True)
weather_receiver_thread = threading.Thread(target=receive_weather, daemon=True)
action_receiver_thread.start()
weather_receiver_thread.start()

BG = (50, 50, 50)

# Make a list storing each frame for animations
animation_list = []
# Define the number of frames for each action
animation_frames = {
    'idle': 11,
    'weather': 15,
    'cross': 11,
    'crossstill': 3,  
    'uncross': 9,
    'dismiss': 15,
    'still': 3
}

actions = ['idle', 'weather', 'cross', 'crossstill', 'uncross', 'dismiss', 'still']
step_counter = 0

# Load frames for each action
for action in actions:
    temp_img_list = []
    for i in range(animation_frames[action]):
        image = sprite_sheet.get_image(step_counter, 500, 500, 1.4)
        temp_img_list.append(image)
        step_counter += 1
    animation_list.append(temp_img_list)

action_map = {'idle': 0, 'weather': 1, 'cross': 2, 'crossstill': 3, 'uncross': 4, 'dismiss': 5, 'still': 6}
action = 6
last_update = pygame.time.get_ticks()
animation_cooldown = 150
frame = 0
animation_active = False

def listen_for_input():
    global action, next_action, animation_active, weather_activated, weather_info
    previous_action = None  # Initialize previous action
    while True:
        if weather_info:  # Only update if weather_info is not empty
            weather_activated = weather_info.strip()
        user_input = testaction.strip()
        if user_input != previous_action:  # Check if the current input is different from the previous one
            previous_action = user_input  # Update previous action
            if user_input in action_map:
                if action == action_map['crossstill'] and action_map[user_input] != action_map['uncross']:
                    next_action = action_map[user_input]
                    action = action_map['uncross']
                else:
                    action = action_map[user_input]
                    animation_active = True  # Mark the animation as active

# Start the input listener in a separate thread
input_thread = threading.Thread(target=listen_for_input, daemon=True)
input_thread.start()

# Main loop
running = True
while running:
    # Update background
    screen.fill(BG)
    
    # Update animation
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= animation_cooldown:
        frame += 1
        last_update = current_time
        if frame >= len(animation_list[action]):
            frame = 0
            if action == action_map['cross']:
                action = action_map['crossstill']  # Transition to crossstill after cross completes
            elif action == action_map['crossstill']:
                frame = 0  # Loop back to the start of crossstill
            elif action == action_map['uncross'] and next_action is not None:
                action = next_action
                next_action = None
                animation_active = True  # Mark the animation as active
            elif animation_active:
                action = 6  # Reset action to still after completing the animation
                animation_active = False  # Mark the animation as inactive

    # Show frame image
    screen.blit(animation_list[action][frame], (0, 0))
    if weather_activated:
        # Display weather information inside the box
        pygame.draw.rect(screen, (0, 163, 225), (weather_box_x, weather_box_y, weather_box_width, weather_box_height))
        wrapped_lines = wrap_text(weather_activated, weather_font, weather_box_width - 20)
        for i, line in enumerate(wrapped_lines):
            text_surface = weather_font.render(line, True, (255, 255, 255))  # Render text with white color
            text_rect = text_surface.get_rect()
            text_rect.topleft = (weather_box_x + 10, weather_box_y + 10 + (i * 20))  # Adjust position and spacing
            screen.blit(text_surface, text_rect)
    
    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.update()

# Quit Pygame
pygame.quit()
sys.exit()
