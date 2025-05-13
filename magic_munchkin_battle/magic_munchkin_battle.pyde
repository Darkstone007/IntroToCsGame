# Magic Munchkin Battle
# Single .pyde file for Processing IDE (Python mode)
# Version: 1.4.6 (2025-05-03) - Fixed attack functionality and increased enemy health by 20%
# Combines assets, classes, and game logic
# Uses Minim library for sound support

import random
import os
add_library('minim')  # I added Minim for sound effects to make the game more immersive

# Just a quick print to make sure the right version loads when I run it
print("Loading Magic Munchkin Battle - Version 1.4.6")

# --- Assets ---
# I set up a dictionary to hold all my images - characters, enemies, and UI elements
images = {
    "background": None,
    "finn": None,
    "jake": None,
    "marceline": None,
    "flame_princess": None,
    "ice_king": None,
    "princess_bubblegum": None,
    "bmo": None,
    "lumpy_space_princess": None,
    "banana_guard": None,
    "female_jake": None,
    "gunther": None,
    "female_finn": None,
    "tree_trunks": None,
    "goblin": None,
    "slime": None,
    "troll": None,
    "ogre": None,
    "card_back": None,
    "bin": None
}
# Special Note on Images:
# - **Process**: I started by sourcing images for Adventure Time characters and enemies from online fan art (with permission where needed). I aimed for 80x80 for characters and 100x100 for enemies to keep things consistent. I also needed a card back and bin icon for the UI.
# - **Issues**: Loading images was a nightmare at first - some files were missing, others had weird dimensions (like 0x0), and Processing threw errors if the path was wrong. I added fallbacks (colored rectangles) to handle failures, but resizing was tricky - some images got distorted if not square. I ended up standardizing sizes in the load function.

# Dictionary for sound effects - I wanted a boing for card draws, pow for attacks, etc.
sounds = {
    "boing": None,
    "pow": None,
    "cheer": None,
    "discard": None
}

def load_assets():
    global images, sounds
    print("Starting load_assets")  # Debugging to make sure this runs
    data_path = os.path.join(sketchPath(), "data")  # Path to my data folder where assets live
    print("Data path: %s" % data_path)
    
    # I wrote this helper function to load images safely with fallbacks
    def load_image_safe(key, filename, fallback_color=None, target_width=None, target_height=None):
        try:
            filepath = os.path.join(data_path, filename)
            print("Loading %s from: %s" % (filename, filepath))
            if os.path.exists(filepath):  # Check if the file actually exists
                images[key] = loadImage(filepath)
                print("%s loaded: %s" % (key, images[key] is not None))
                if images[key]:
                    if images[key].width <= 0 or images[key].height <= 0:  # Some images were corrupted or empty
                        print("%s has invalid dimensions (%d x %d), creating fallback" % (key, images[key].width, images[key].height))
                        images[key] = None
                    else:
                        if target_width and target_height:  # Resize to keep things uniform
                            images[key].resize(target_width, target_height)
                            print("%s resized to %dx%d" % (key, target_width, target_height))
            else:
                print("File not found: %s" % filepath)
                if fallback_color:  # If no image, make a colored rectangle as a placeholder
                    fallback = createImage(target_width or 100, target_height or 100, RGB)
                    fallback.loadPixels()
                    for i in range(len(fallback.pixels)):
                        fallback.pixels[i] = fallback_color
                    fallback.updatePixels()
                    images[key] = fallback
                    print("Created fallback image for %s" % key)
        except Exception, e:
            print("Error loading %s: %s" % (filename, str(e)))
            if fallback_color:  # Fallback in case of any other errors
                fallback = createImage(target_width or 100, target_height or 100, RGB)
                fallback.loadPixels()
                for i in range(len(fallback.pixels)):
                    fallback.pixels[i] = fallback_color
                fallback.updatePixels()
                images[key] = fallback
                print("Created fallback image for %s after error" % key)
    
    # Loading the background separately because it’s bigger and needs a gradient fallback
    try:
        bg_filepath = os.path.join(data_path, "ooo_background.png")
        if os.path.exists(bg_filepath):
            images["background"] = loadImage(bg_filepath)
            print("Background loaded: %s" % (images["background"] is not None))
            if images["background"] and images["background"].width > 0 and images["background"].height > 0:
                images["background"].resize(800, 600)  # Make sure it fits the screen
                print("Background resized to 800x600")
            else:
                print("Background has invalid dimensions, creating fallback")
                bg = createImage(800, 600, RGB)
                bg.loadPixels()
                for y in range(600):
                    for x in range(800):
                        r = 0
                        g = 100
                        b = 200 - int(y / 3)  # Gradient from blue to darker blue
                        bg.pixels[y * 800 + x] = color(r, g, b)
                bg.updatePixels()
                images["background"] = bg
                print("Created gradient fallback background")
        else:
            print("Background file not found: %s" % bg_filepath)
            bg = createImage(800, 600, RGB)
            bg.loadPixels()
            for y in range(600):
                for x in range(800):
                    r = 0
                    g = 100
                    b = 200 - int(y / 3)
                    bg.pixels[y * 800 + x] = color(r, g, b)
            bg.updatePixels()
            images["background"] = bg
            print("Created gradient fallback background")
    except Exception, e:
        print("Error loading background: %s" % str(e))
        bg = createImage(800, 600, RGB)
        bg.loadPixels()
        for y in range(600):
            for x in range(800):
                r = 0
                g = 100
                b = 200 - int(y / 3)
                bg.pixels[y * 800 + x] = color(r, g, b)
        bg.updatePixels()
        images["background"] = bg
        print("Created gradient fallback background after error")
    # Special Note on Background:
    # - **Process**: I wanted a whimsical background from the Land of Ooo, so I found a fan-made image (ooo_background.png) that I thought would fit. It needed to be 800x600 to match the canvas size, so I added resizing logic.
    # - **Issues**: The background often failed to load because of path issues or corrupted files. Sometimes Processing would crash if the image dimensions were invalid. I added a gradient fallback (blue to darker blue) to ensure the game wouldn’t look broken if the image failed. Resizing also caused some pixelation, but I decided it was acceptable for now.
    
    # Load all my character and enemy images, with fallbacks in case they don’t load
    load_image_safe("finn", "finn.png", color(30, 144, 255), 80, 80)
    load_image_safe("jake", "jake.png", color(255, 215, 0), 80, 80)
    load_image_safe("marceline", "marceline.png", color(128, 0, 128), 80, 80)
    load_image_safe("flame_princess", "flame_princess.png", color(255, 69, 0), 80, 80)
    load_image_safe("ice_king", "ice_king.png", color(0, 191, 255), 80, 80)
    load_image_safe("princess_bubblegum", "princess_bubblegum.png", color(255, 105, 180), 80, 80)
    load_image_safe("bmo", "bmo.png", color(46, 139, 87), 80, 80)
    load_image_safe("lumpy_space_princess", "lumpy_space_princess.png", color(186, 85, 211), 80, 80)
    load_image_safe("banana_guard", "banana_guard.png", color(255, 255, 0), 80, 80)
    load_image_safe("female_jake", "female_jake.png", color(218, 165, 32), 80, 80)
    load_image_safe("gunther", "gunther.png", color(0, 0, 0), 80, 80)
    load_image_safe("female_finn", "female_finn.png", color(135, 206, 250), 80, 80)
    load_image_safe("tree_trunks", "tree_trunks.png", color(107, 142, 35), 80, 80)
    load_image_safe("goblin", "goblin.png", color(50, 205, 50), 100, 100)
    load_image_safe("slime", "slime.png", color(0, 250, 154), 100, 100)
    load_image_safe("troll", "troll.png", color(165, 42, 42), 100, 100)
    load_image_safe("ogre", "ogre.png", color(139, 69, 19), 100, 100)
    load_image_safe("card_back", "card_back.png", color(25, 25, 112), 80, 80)
    load_image_safe("bin", "bin.png", color(169, 169, 169), 80, 80)
    
    # Helper function to load sounds safely
    def load_sound_safe(key, filename):
        try:
            filepath = os.path.join(data_path, filename)
            print("Loading %s from: %s" % (filename, filepath))
            if os.path.exists(filepath):
                sounds[key] = minim.loadFile(filepath)  # Load sound using Minim
                print("%s sound loaded: %s" % (key, sounds[key] is not None))
            else:
                print("File not found: %s" % filepath)
        except Exception, e:
            print("Error loading %s: %s" % (filename, str(e)))
    
    # Load all my sound effects
    load_sound_safe("boing", "boing.wav")
    load_sound_safe("pow", "pow.wav")
    load_sound_safe("cheer", "cheer.wav")
    load_sound_safe("discard", "discard.wav")
    print("Finished load_assets")

# --- Classes ---
# Attack class to define each attack’s properties
class Attack:
    def __init__(self, name, attack, health, load_time_seconds):
        # Make sure all values are valid with fallbacks
        self.name = str(name) if name else "Unknown Attack"
        self.attack = int(attack) if attack is not None else 0
        self.health = int(health) if health is not None else 0
        self.load_time_seconds = float(load_time_seconds) if load_time_seconds is not None else 0.0
        self.start_load_time = None  # For tracking when the attack starts loading
        self.is_loading = False  # To check if the attack is currently loading

# Card class to represent each character card
class Card:
    def __init__(self, name, attacks, image):
        # Initialize card properties with fallbacks
        self.name = str(name) if name else "Unknown Card"
        self.attacks = attacks if attacks else []
        self.image = image if image else None
        # Animation stuff to make cards wiggle a bit
        self.anim_offset_x = 0
        self.anim_direction = random.choice([-1, 1])
        self.anim_speed = random.uniform(0.5, 1.5)
        # Reset loading state for all attacks
        for attack in self.attacks:
            attack.start_load_time = None
            attack.is_loading = False
    
    # Start loading all attacks on this card
    def start_loading_all(self):
        for attack in self.attacks:
            if not attack.is_loading:
                attack.start_load_time = millis()
                attack.is_loading = True
    
    # Handle the fight logic between two cards
    def fight(self, selected_attack, other, other_attack, game):
        self.start_loading_all()
        
        # Check if the attack is ready based on load time
        elapsed_seconds = (millis() - selected_attack.start_load_time) / 1000.0 if selected_attack.start_load_time else 0
        if elapsed_seconds < selected_attack.load_time_seconds:
            return None, None  # Not ready yet
        
        # Reset loading state after the attack is used
        selected_attack.is_loading = False
        selected_attack.start_load_time = None
        
        # Add a chance for a critical hit
        crit_multiplier = 1
        if random.random() < 0.2:  # 20% chance
            crit_multiplier = 2
            game.message = "Critical Hit! Damage doubled!"
            game.message_timer = 180
        
        effective_attack = selected_attack.attack * crit_multiplier
        
        # Compare attacks to determine winner
        if effective_attack > other_attack.attack:
            return self, other
        elif other_attack.attack > effective_attack:
            return other, self
        else:
            # If attacks are equal, compare health
            if selected_attack.health > other_attack.health:
                return self, other
            elif other_attack.health > selected_attack.health:
                return other, self
        return None, None  # Tie
    
    # Calculate how far along the attack is in loading
    def get_load_progress(self, attack):
        if not attack.is_loading or attack.start_load_time is None:
            return 0.0
        elapsed_seconds = (millis() - attack.start_load_time) / 1000.0
        progress = min(elapsed_seconds / attack.load_time_seconds, 1.0)
        return progress
    
    # Update the card’s wiggle animation
    def update_animation(self):
        self.anim_offset_x += self.anim_speed * self.anim_direction
        if abs(self.anim_offset_x) > 5:
            self.anim_direction *= -1

# Player class to manage the player’s state
class Player:
    def __init__(self):
        self.health = 100  # Starting health
        self.full_deck = self.create_full_deck()  # Create the full deck of cards
        self.deck = self.draw_initial_cards()  # Draw initial hand
        self.discard_pile = []  # For discarded cards
    
    # Create a deck with multiple copies of each character
    def create_full_deck(self):
        characters = [
            {"name": "Finn", "attacks": [
                Attack("Quick Attack", 5, 4, 1.0),
                Attack("Normal Attack", 6, 3, 1.5),
                Attack("Build-Up Attack", 8, 2, 2.0),
                Attack("Very Big Attack", 10, 2, 3.0)
            ], "image_key": "finn"},
            {"name": "Jake", "attacks": [
                Attack("Quick Attack", 4, 3, 1.0),
                Attack("Normal Attack", 5, 2, 1.5),
                Attack("Build-Up Attack", 7, 1, 2.0),
                Attack("Very Big Attack", 9, 1, 3.0)
            ], "image_key": "jake"},
            {"name": "Marceline", "attacks": [
                Attack("Quick Attack", 4, 5, 1.0),
                Attack("Normal Attack", 5, 4, 1.5),
                Attack("Build-Up Attack", 7, 3, 2.0),
                Attack("Very Big Attack", 9, 3, 3.0)
            ], "image_key": "marceline"},
            {"name": "Flame Princess", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "flame_princess"},
            {"name": "Ice King", "attacks": [
                Attack("Quick Attack", 3, 3, 1.0),
                Attack("Normal Attack", 4, 2, 1.5),
                Attack("Build-Up Attack", 6, 1, 2.0),
                Attack("Very Big Attack", 8, 1, 3.0)
            ], "image_key": "ice_king"},
            {"name": "Princess Bubblegum", "attacks": [
                Attack("Quick Attack", 3, 5, 1.0),
                Attack("Normal Attack", 4, 4, 1.5),
                Attack("Build-Up Attack", 6, 3, 2.0),
                Attack("Very Big Attack", 8, 3, 3.0)
            ], "image_key": "princess_bubblegum"},
            {"name": "BMO", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "bmo"},
            {"name": "Lumpy Space Princess", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "lumpy_space_princess"},
            {"name": "Banana Guard", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "banana_guard"},
            {"name": "Female Jake", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "female_jake"},
            {"name": "Gunther", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "gunther"},
            {"name": "Female Finn", "attacks": [
                Attack("Quick Attack", 3, 4, 1.0),
                Attack("Normal Attack", 4, 3, 1.5),
                Attack("Build-Up Attack", 6, 2, 2.0),
                Attack("Very Big Attack", 8, 2, 3.0)
            ], "image_key": "female_finn"},
            {"name": "Tree Trunks", "attacks": [
                Attack("Quick Attack", 3, 3, 1.0),
                Attack("Normal Attack", 4, 2, 1.5),
                Attack("Build-Up Attack", 6, 1, 2.0),
                Attack("Very Big Attack", 8, 1, 3.0)
            ], "image_key": "tree_trunks"}
        ]
        
        full_deck = []
        # Add 4 copies of each character to the deck
        for char in characters:
            for _ in range(4):
                full_deck.append(Card(char["name"], char["attacks"][:], images.get(char["image_key"], images.get("finn", None))))
        random.shuffle(full_deck)  # Shuffle the deck to make it random
        return full_deck
    
    # Draw the initial 5 cards for the player’s hand
    def draw_initial_cards(self):
        drawn = self.full_deck[:5]
        self.full_deck = self.full_deck[5:]
        return drawn
    
    # Draw a single card from the deck
    def draw_card(self):
        if not self.full_deck:  # If deck is empty, shuffle discard pile back in
            if self.discard_pile:
                self.full_deck = self.discard_pile[:]
                self.discard_pile = []
                random.shuffle(self.full_deck)
            else:
                return None  # No cards left
        card = self.full_deck.pop(0)
        return card
    
    # Discard a card and draw a new one
    def discard_card(self, card_index):
        if 0 <= card_index < len(self.deck):
            discarded = self.deck.pop(card_index)
            self.discard_pile.append(discarded)
            new_card = self.draw_card()
            if new_card:
                self.deck.append(new_card)
            return True
        return False

# Enemy class to manage enemy properties
class Enemy:
    def __init__(self, name, health, cards, image_key):
        self.name = str(name) if name else "Unknown Enemy"
        self.health = int(health * 1.2) if health is not None else 12  # Increased by 20% as requested
        self.cards = cards if cards else []
        self.image = images.get(image_key, None)
        # Animation for enemies to make them wiggle
        self.anim_offset_x = 0
        self.anim_direction = random.choice([-1, 1])
        self.anim_speed = random.uniform(0.5, 1.5)
    
    # Enemy picks a random card and attack to use
    def choose_card_and_attack(self):
        card = random.choice(self.cards) if self.cards else None
        attack = random.choice(card.attacks) if card and card.attacks else None
        return card, attack
    
    # Update enemy’s wiggle animation
    def update_animation(self):
        self.anim_offset_x += self.anim_speed * self.anim_direction
        if abs(self.anim_offset_x) > 8:
            self.anim_direction *= -1

# Main Game class to manage the game state
class Game:
    def __init__(self):
        print("Initializing Game class")
        self.state = "intro"  # Start at the intro screen
        self.difficulty_multiplier = 1.0  # Difficulty scales as you progress
        self.battle_count = 0  # Track number of battles for difficulty scaling
        self.message = ""  # For displaying messages like "Critical Hit!"
        self.message_timer = 0  # How long to show the message
        self.status_effects = []  # For things like attack boosts
        self.last_click_time = 0  # To prevent rapid clicking
        
        # Initialize the player
        try:
            self.player = Player()
            print("Player initialized successfully")
        except Exception, e:
            print("Error initializing Player: %s" % str(e))
            self.player = type('Player', (), {'health': 100, 'deck': [], 'discard_pile': [], 'full_deck': []})()
            print("Created fallback Player instance")
        
        # Initialize enemies
        try:
            self.enemies = self.create_enemies()
            print("Enemies initialized successfully")
        except Exception, e:
            print("Error initializing enemies: %s" % str(e))
            self.enemies = []
        
        self.current_enemy = 0  # Start with the first enemy
        self.score = 0  # Player’s score
        self.battles_won = 0  # Number of enemies defeated
        self.selected_card = None  # Currently selected card
        self.selected_attack = None  # Currently selected attack
        
        # Set up the background
        try:
            self.background = images.get("background", None)
            if not self.background:
                print("Warning: Background image is None, using fallback")
                self.background = createImage(800, 600, RGB)
                self.background.loadPixels()
                for y in range(600):
                    for x in range(800):
                        self.background.pixels[y * 800 + x] = color(0, 100, 200 - int(y / 3))
                self.background.updatePixels()
        except Exception, e:
            print("Error setting background: %s" % str(e))
            self.background = createImage(800, 600, RGB)
            self.background.loadPixels()
            for y in range(600):
                for x in range(800):
                    self.background.pixels[y * 800 + x] = color(0, 100, 200 - int(y / 3))
            self.background.updatePixels()
        
        # Set up the card back image
        try:
            self.card_back = images.get("card_back", None)
            if not self.card_back:
                print("Warning: Card back image is None, using fallback")
                self.card_back = createImage(80, 80, RGB)
                self.card_back.loadPixels()
                for i in range(len(self.card_back.pixels)):
                    self.card_back.pixels[i] = color(25, 25, 112)
                self.card_back.updatePixels()
        except Exception, e:
            print("Error setting card_back: %s" % str(e))
            self.card_back = createImage(80, 80, RGB)
            self.card_back.loadPixels()
            for i in range(len(self.card_back.pixels)):
                self.card_back.pixels[i] = color(25, 25, 112)
            self.card_back.updatePixels()
        
        # Set up the bin image
        try:
            self.bin_image = images.get("bin", None)
            if not self.bin_image:
                print("Warning: Bin image is None, using fallback")
                self.bin_image = createImage(80, 80, RGB)
                self.bin_image.loadPixels()
                for i in range(len(self.bin_image.pixels)):
                    self.bin_image.pixels[i] = color(169, 169, 169)
                self.bin_image.updatePixels()
        except Exception, e:
            print("Error setting bin_image: %s" % str(e))
            self.bin_image = createImage(80, 80, RGB)
            self.bin_image.loadPixels()
            for i in range(len(self.bin_image.pixels)):
                self.bin_image.pixels[i] = color(169, 169, 169)
            self.bin_image.updatePixels()
        
        # Set up sounds
        try:
            self.boing_sound = sounds.get("boing", None)
            self.pow_sound = sounds.get("pow", None)
            self.cheer_sound = sounds.get("cheer", None)
            self.discard_sound = sounds.get("discard", None)
        except Exception, e:
            print("Error setting sounds: %s" % str(e))
            self.boing_sound = None
            self.pow_sound = None
            self.cheer_sound = None
            self.discard_sound = None
        
        print("Game initialized with difficulty_multiplier:", self.difficulty_multiplier)
    
    # Create the list of enemies to fight
    def create_enemies(self):
        return [
            Enemy("Goblin Munchkin", 10, self.create_enemy_cards(1), "goblin"),
            Enemy("Candy Citizen", 12, self.create_enemy_cards(2), "slime"),
            Enemy("Grumpy Turnip", 14, self.create_enemy_cards(3), "troll"),
            Enemy("Boss Ogre", 18, self.create_enemy_cards(4), "ogre")
        ]
    
    # Create cards for enemies based on difficulty
    def create_enemy_cards(self, difficulty):
        cards = [
            Card("Goblin", [
                Attack("Quick Attack", 2 * 0.8, 2, 1.0),
                Attack("Normal Attack", 3 * 0.8, 1, 1.5),
                Attack("Build-Up Attack", 4 * 0.8, 1, 2.0),
                Attack("Very Big Attack", 5 * 0.8, 1, 3.0)
            ], images.get("goblin", None)),
            Card("Slime", [
                Attack("Quick Attack", 2 * 0.8, 2, 1.0),
                Attack("Normal Attack", 3 * 0.8, 1, 1.5),
                Attack("Build-Up Attack", 4 * 0.8, 1, 2.0),
                Attack("Very Big Attack", 5 * 0.8, 1, 3.0)
            ], images.get("slime", None)),
            Card("Troll", [
                Attack("Quick Attack", 3 * 0.8, 2, 1.0),
                Attack("Normal Attack", 4 * 0.8, 1, 1.5),
                Attack("Build-Up Attack", 5 * 0.8, 1, 2.0),
                Attack("Very Big Attack", 6 * 0.8, 1, 3.0)
            ], images.get("troll", None)),
            Card("Ogre", [
                Attack("Quick Attack", 3 * 0.8, 2, 1.0),
                Attack("Normal Attack", 4 * 0.8, 1, 1.5),
                Attack("Build-Up Attack", 5 * 0.8, 1, 2.0),
                Attack("Very Big Attack", 6 * 0.8, 1, 3.0)
            ], images.get("ogre", None))
        ]
        # Scale enemy stats based on difficulty
        for card in cards:
            for attack in card.attacks:
                attack.attack = int(attack.attack * min(self.difficulty_multiplier, 1.5) + (difficulty - 1))
                attack.health = int(attack.health * min(self.difficulty_multiplier, 1.5) + (difficulty - 1))
        return cards
    
    # Reset the game to start over
    def reset(self):
        print("Resetting game")
        self.state = "intro"
        self.player = Player()
        self.enemies = self.create_enemies()
        self.current_enemy = 0
        self.score = 0
        self.battles_won = 0
        self.selected_card = None
        self.selected_attack = None
        self.difficulty_multiplier = 1.0
        self.battle_count = 0
        self.message = ""
        self.message_timer = 0
        self.status_effects = []
    
    # Update game state each frame
    def update(self):
        # Update card animations
        for card in self.player.deck:
            card.update_animation()
        if self.current_enemy < len(self.enemies):
            self.enemies[self.current_enemy].update_animation()
        # Handle message timing
        if self.message_timer > 0:
            self.message_timer -= 1
        elif self.message:
            self.message = ""
        # Update status effects
        for effect in self.status_effects[:]:
            effect["duration"] -= 1
            if effect["duration"] <= 0:
                self.status_effects.remove(effect)
        # Check for game over conditions
        if self.state == "playing":
            if self.player.health <= 0:
                self.state = "gameover"
                print("Game over: Player health <= 0")
            elif self.current_enemy >= len(self.enemies):
                self.state = "gameover"
                print("Game over: All enemies defeated")
                if self.cheer_sound:
                    self.cheer_sound.rewind()
                    self.cheer_sound.play()
    
    # Handle clicking on cards
    def handle_card_click(self, x, y):
        current_time = millis()
        if current_time - self.last_click_time < 300:  # Prevent rapid clicks
            return
        self.last_click_time = current_time
        
        if self.state == "playing":
            bin_x = width - 100
            bin_y = height - 100
            if bin_x <= x <= bin_x + 80 and bin_y <= y <= bin_y + 80:
                if self.discard_sound:
                    self.discard_sound.rewind()
                    self.discard_sound.play()
                return
            
            # Handle drawing a new card
            draw_x = width - 200
            draw_y = height - 100
            if draw_x <= x <= draw_x + 80 and draw_y <= y <= draw_y + 80 and len(self.player.full_deck) > 0:
                new_card = self.player.draw_card()
                if new_card:
                    if len(self.player.deck) < 5:
                        self.player.deck.append(new_card)
                        print("Card drawn: %s" % new_card.name)
                        if self.boing_sound:
                            self.boing_sound.rewind()
                            self.boing_sound.play()
                        self.message = "Drew " + new_card.name
                        self.message_timer = 180
                    else:
                        # If hand is full, replace a random card
                        random_index = random.randint(0, len(self.player.deck) - 1)
                        discarded = self.player.deck.pop(random_index)
                        self.player.discard_pile.append(discarded)
                        self.player.deck.insert(random_index, new_card)
                        print("Replaced card at index %d: %s with %s" % (random_index, discarded.name, new_card.name))
                        if self.boing_sound:
                            self.boing_sound.rewind()
                            self.boing_sound.play()
                        self.message = "Replaced " + discarded.name + " with " + new_card.name
                        self.message_timer = 180
                        if self.discard_sound:
                            self.discard_sound.rewind()
                            self.discard_sound.play()
                    return
            
            # Check if a card was clicked
            card_width = 80
            card_height = 80
            self.selected_card = None
            for i, card in enumerate(self.player.deck):
                card_x = 50 + i * 110
                card_y = height - 140
                if card_x <= x <= card_x + card_width and card_y <= y <= card_y + card_height:
                    self.selected_card = card
                    card.start_loading_all()
                    self.state = "select_attack"
                    print("Card selected: %s" % card.name)
                    if self.boing_sound:
                        self.boing_sound.rewind()
                        self.boing_sound.play()
                    break
    
    # Handle selecting an attack
    def handle_attack_click(self, x, y, attack_index):
        current_time = millis()
        if current_time - self.last_click_time < 300:
            return False
        self.last_click_time = current_time
        
        if self.state == "select_attack" and self.selected_card:
            card_index = self.player.deck.index(self.selected_card)
            card_x = 50 + card_index * 110
            card_y = height - 140
            attack_y = card_y - (len(self.selected_card.attacks) - 1 - attack_index) * 40
            progress = self.selected_card.get_load_progress(self.selected_card.attacks[attack_index])
            # Check if the attack button was clicked and is ready
            if card_x <= x <= card_x + 150 and attack_y - 20 <= y <= attack_y + 20:
                if progress >= 1.0:
                    self.selected_attack = self.selected_card.attacks[attack_index]
                    self.state = "aim_attack"
                    print("Attack selected: %s" % self.selected_attack.name)
                    return True
        return False
    
    # Handle aiming the attack at the enemy
    def handle_aim_click(self, x, y):
        current_time = millis()
        if current_time - self.last_click_time < 300:
            return False
        self.last_click_time = current_time
        
        if self.state == "aim_attack":
            enemy = self.enemies[self.current_enemy]
            enemy_x = width - 150 + enemy.anim_offset_x
            enemy_y = 150
            enemy_w = 100
            enemy_h = 100
            if enemy_x <= x <= enemy_x + enemy_w and enemy_y <= y <= enemy_y + enemy_h:
                self.play_turn()
                print("Attack aimed at enemy: %s" % enemy.name)
                return True
        return False
    
    # Play out a turn of combat
    def play_turn(self):
        if self.selected_card and self.selected_attack:
            enemy = self.enemies[self.current_enemy]
            enemy_card, enemy_attack = enemy.choose_card_and_attack()
            if enemy_card is None or enemy_attack is None:
                print("Invalid enemy card or attack")
                self.selected_card = None
                self.selected_attack = None
                self.state = "playing"
                self.update()
                return
            
            # Scale enemy attack based on difficulty
            enemy_attack.attack = int(enemy_attack.attack * min(self.difficulty_multiplier, 1.5))
            
            winner, loser = self.selected_card.fight(self.selected_attack, enemy_card, enemy_attack, self)
            
            battle_result = ""
            if winner:
                if self.pow_sound:
                    self.pow_sound.rewind()
                    self.pow_sound.play()
                if winner == self.selected_card:
                    damage = self.selected_attack.attack
                    enemy.health -= damage
                    self.score += 5
                    battle_result = "You won! Deal %d damage!" % damage
                elif winner == enemy_card:
                    damage = self.selected_attack.health
                    self.player.health -= damage
                    battle_result = "You lost! Take %d damage!" % damage
            else:
                battle_result = "Tie! No damage."
            
            self.message = battle_result
            self.message_timer = 180
            
            self.battle_count += 1
            # Increase difficulty every 4 battles
            if self.battle_count % 4 == 0:
                self.difficulty_multiplier = min(self.difficulty_multiplier + 0.1, 1.5)
                print("Difficulty increased to %.1f" % self.difficulty_multiplier)
            
            # Check if enemy was defeated
            if enemy.health <= 0:
                self.battles_won += 1
                self.score += 10
                self.current_enemy += 1
                self.message = "Enemy defeated! +10 points!"
                self.message_timer = 180
                effect = {"name": "Victory Boost", "effect": "attack", "amount": 1, "duration": 3}
                self.status_effects.append(effect)
            
            self.selected_card = None
            self.selected_attack = None
            self.state = "playing"
            self.update()

# --- Game Logic ---
# Define game states as constants
INTRO, PLAYING, PAUSED, GAMEOVER, SELECT_ATTACK, AIM_ATTACK = "intro", "playing", "paused", "gameover", "select_attack", "aim_attack"

game = None
minim = None
font_regular = None
font_bold = None

def setup():
    global game, minim, font_regular, font_bold
    print("Starting setup")
    size(800, 600)  # Set the window size
    
    # Load fonts, with fallbacks in case Comic Sans isn’t available
    try:
        font_regular = createFont("Comic Sans MS", 14, True)
        print("Loaded font: Comic Sans MS")
    except Exception, e:
        font_regular = createFont("Arial", 14)
        print("Fallback to Arial font: %s" % str(e))
    try:
        font_bold = createFont("Comic Sans MS Bold", 16, True)
        print("Loaded font: Comic Sans MS Bold")
    except Exception, e:
        font_bold = createFont("Arial Bold", 16)
        print("Fallback to Arial Bold font: %s" % str(e))
    
    minim = Minim(this)  # Initialize Minim for sound
    
    load_assets()  # Load all assets
    
    # Create the game instance
    print("Creating Game instance")
    try:
        game = Game()
    except Exception, e:
        print("Error creating Game instance: %s" % str(e))
        game = type('Game', (), {
            'difficulty_multiplier': 1.0,
            'state': 'intro',
            'background': None,
            'player': type('Player', (), {'health': 100, 'deck': [], 'discard_pile': [], 'full_deck': []})(),
            'enemies': [],
            'current_enemy': 0,
            'score': 0,
            'battles_won': 0,
            'selected_card': None,
            'selected_attack': None,
            'battle_count': 0,
            'message': "",
            'message_timer': 0,
            'status_effects': [],
            'last_click_time': 0,
            'update': lambda self: None
        })()
        print("Created fallback Game instance")
    
    # Debug to make sure the game instance is set up correctly
    print("Game instance created with attributes:", dir(game))
    if hasattr(game, 'difficulty_multiplier'):
        print("Confirmed: difficulty_multiplier =", game.difficulty_multiplier)
    else:
        print("Error: Game instance missing difficulty_multiplier")
    
    frameRate(60)  # Set frame rate for smooth animation
    print("Finished setup")

def draw():
    background(0)  # Clear the screen
    
    # Draw the background
    try:
        if game.background:
            image(game.background, 0, 0, width, height)
            print("Rendering background")
        else:
            print("Warning: Background image is None, using fallback")
            bg = createImage(800, 600, RGB)
            bg.loadPixels()
            for y in range(600):
                for x in range(800):
                    bg.pixels[y * 800 + x] = color(0, 100, 200 - int(y / 3))
            bg.updatePixels()
            image(bg, 0, 0, width, height)
            print("Rendered gradient fallback background")
    except Exception, e:
        print("Error rendering background: %s" % str(e))
        bg = createImage(800, 600, RGB)
        bg.loadPixels()
        for y in range(600):
            for x in range(800):
                bg.pixels[y * 800 + x] = color(0, 100, 200 - int(y / 3))
        bg.updatePixels()
        image(bg, 0, 0, width, height)
        print("Rendered gradient fallback background after error")
    
    game.update()  # Update game state
    
    textFont(font_regular)  # Set default font
    
    # Draw the appropriate screen based on game state
    if game.state == INTRO:
        draw_intro_screen()
    elif game.state in [PLAYING, PAUSED, SELECT_ATTACK, AIM_ATTACK]:
        draw_game_screen()
        if game.state == PAUSED:
            draw_pause_overlay()
        elif game.state == SELECT_ATTACK:
            draw_attack_selection()
        elif game.state == AIM_ATTACK:
            draw_aim_indicator()
    elif game.state == GAMEOVER:
        draw_gameover_screen()

def draw_intro_screen():
    try:
        textFont(font_bold)
        textAlign(CENTER, CENTER)
        fill(0)
        textSize(32)
        text("Magic Munchkin Battle", width/2 + 2, height/2 - 98)
        fill(255)
        text("Magic Munchkin Battle", width/2, height/2 - 100)
        textSize(20)
        fill(0)
        text("Click a card, select an attack, aim at the enemy!", width/2 + 1, height/2 - 49)
        fill(255)
        text("Click a card, select an attack, aim at the enemy!", width/2, height/2 - 50)
        fill(0)
        text("Press S to Start, R to Restart, P to Pause", width/2 + 1, height/2 + 1)
        fill(255)
        text("Press S to Start, R to Restart, P to Pause", width/2, height/2)
        
        # Show Finn and Jake on the intro screen
        if images.get("finn"):
            image(images["finn"], width/2 - 100, height/2 + 50, 80, 80)
        if images.get("jake"):
            image(images["jake"], width/2 + 20, height/2 + 50, 80, 80)
        print("Rendering intro screen")
    except Exception, e:
        print("Error rendering intro images: %s" % str(e))

def draw_game_screen():
    textFont(font_bold)
    textAlign(LEFT)
    fill(0)
    textSize(16)
    try:
        # Draw player stats
        text("Player Health: %d" % game.player.health, 22, 32)
        fill(255)
        text("Player Health: %d" % game.player.health, 20, 30)
        stroke(0)
        strokeWeight(2)
        fill(255, 0, 0)
        rect(20, 40, 100, 10)
        fill(0, 255, 0)
        health_width = (game.player.health / 100.0) * 100
        rect(20, 40, health_width, 10)
        strokeWeight(1)
        
        text("Score: %d" % game.score, 22, 72)
        text("Battles Won: %d/%d" % (game.battles_won, len(game.enemies)), 22, 92)
        text("Difficulty: %.1f" % game.difficulty_multiplier, 22, 112)
        fill(255)
        text("Score: %d" % game.score, 20, 70)
        text("Battles Won: %d/%d" % (game.battles_won, len(game.enemies)), 20, 90)
        text("Difficulty: %.1f" % game.difficulty_multiplier, 20, 110)
        print("Rendering game stats")
    except Exception, e:
        print("Error rendering game stats: %s" % str(e))
    
    # Draw the current enemy
    if game.current_enemy < len(game.enemies):
        enemy = game.enemies[game.current_enemy]
        textAlign(CENTER)
        textFont(font_regular)
        fill(0)
        textSize(14)
        try:
            text("%s Health: %d" % (enemy.name, enemy.health), width - 148, 82)
            fill(0, 255, 0)
            text("%s Health: %d" % (enemy.name, enemy.health), width - 150, 80)
            stroke(0)
            strokeWeight(2)
            fill(255, 0, 0)
            rect(width - 200, 90, 100, 10)
            fill(0, 255, 0)
            enemy_health_width = (enemy.health / (enemy.health + 10)) * 100
            rect(width - 200, 90, enemy_health_width, 10)
            strokeWeight(1)
            
            enemy_x = width - 150 + enemy.anim_offset_x
            enemy_y = 150
            if enemy.image:
                stroke(0)
                strokeWeight(2)
                if game.state == AIM_ATTACK:
                    stroke(255, 0, 0)
                    strokeWeight(4)
                    rect(enemy_x - 5, enemy_y - 5, 110, 110)
                    strokeWeight(1)
                    stroke(0)
                image(enemy.image, enemy_x, enemy_y, 100, 100)
                strokeWeight(1)
            else:
                stroke(0)
                strokeWeight(2)
                fill(50, 205, 50)
                rect(enemy_x, enemy_y, 100, 100)
                strokeWeight(1)
            print("Rendering enemy: %s" % enemy.name)
        except Exception, e:
            print("Error rendering enemy: %s" % str(e))
    
    # Draw the player’s cards
    card_width = 80
    card_height = 80
    try:
        for i, card in enumerate(game.player.deck):
            card_x = 50 + i * 110
            card_y = height - 140
            if game.selected_card == card:
                stroke(255, 255, 0)
                strokeWeight(4)
                rect(card_x - 5, card_y - 5, card_width + 10, card_height + 10)
                strokeWeight(1)
                stroke(0)
            if card.image:
                stroke(0)
                strokeWeight(2)
                image(card.image, card_x + card.anim_offset_x, card_y, card_width, card_height)
                strokeWeight(1)
            else:
                stroke(0)
                strokeWeight(2)
                fill(100)
                rect(card_x + card.anim_offset_x, card_y, card_width, card_height)
                strokeWeight(1)
            textFont(font_regular)
            textAlign(CENTER)
            fill(0)
            textSize(12)
            text(card.name, card_x + card_width/2 + card.anim_offset_x + 1, card_y - 9)
            fill(255)
            text(card.name, card_x + card_width/2 + card.anim_offset_x, card_y - 10)
            
            # Show attack progress bar if an attack is selected
            if game.selected_card == card and game.selected_attack:
                attack_idx = card.attacks.index(game.selected_attack)
                progress = card.get_load_progress(game.selected_attack)
                fill(255, 0, 0)
                rect(card_x, card_y + card_height + 5, card_width, 5)
                fill(0, 255, 0)
                rect(card_x, card_y + card_height + 5, card_width * progress, 5)
        print("Rendering %d player cards" % len(game.player.deck))
    except Exception, e:
        print("Error rendering cards: %s" % str(e))
    
    # Draw the draw and discard piles
    try:
        if game.card_back:
            stroke(0)
            strokeWeight(2)
            image(game.card_back, width - 200, height - 100, 80, 80)
            strokeWeight(1)
            textAlign(CENTER)
            textSize(12)
            fill(0)
            text("Draw (%d)" % len(game.player.full_deck), width - 160, height - 60)
            fill(255)
            text("Draw (%d)" % len(game.player.full_deck), width - 160, height - 62)
        else:
            stroke(0)
            strokeWeight(2)
            fill(25, 25, 112)
            rect(width - 200, height - 100, 80, 80)
            strokeWeight(1)
            textAlign(CENTER)
            textSize(12)
            fill(0)
            text("Draw (%d)" % len(game.player.full_deck), width - 160, height - 60)
            fill(255)
            text("Draw (%d)" % len(game.player.full_deck), width - 160, height - 62)
        
        if game.bin_image:
            stroke(0)
            strokeWeight(2)
            image(game.bin_image, width - 100, height - 100, 80, 80)
            strokeWeight(1)
            textAlign(CENTER)
            textSize(12)
            fill(0)
            text("Discard (%d)" % len(game.player.discard_pile), width - 60, height - 60)
            fill(255)
            text("Discard (%d)" % len(game.player.discard_pile), width - 60, height - 62)
        else:
            stroke(0)
            strokeWeight(2)
            fill(169, 169, 169)
            rect(width - 100, height - 100, 80, 80)
            strokeWeight(1)
            textAlign(CENTER)
            textSize(12)
            fill(0)
            text("Discard (%d)" % len(game.player.discard_pile), width - 60, height - 60)
            fill(255)
            text("Discard (%d)" % len(game.player.discard_pile), width - 60, height - 62)
        print("Rendering draw pile (%d cards) and discard pile (%d cards)" % (len(game.player.full_deck), len(game.player.discard_pile)))
    except Exception, e:
        print("Error rendering draw/discard piles: %s" % str(e))
    
    # Draw status effects
    try:
        textFont(font_regular)
        textAlign(LEFT)
        textSize(12)
        for i, effect in enumerate(game.status_effects):
            fill(0)
            text("%s: %d turns" % (effect["name"], effect["duration"]), 22, 142 + i * 20)
            fill(255)
            text("%s: %d turns" % (effect["name"], effect["duration"]), 20, 140 + i * 20)
        print("Rendering %d status effects" % len(game.status_effects))
    except Exception, e:
        print("Error rendering status effects: %s" % str(e))
    
    # Draw any messages (like "Critical Hit!")
    try:
        if game.message:
            textFont(font_bold)
            textAlign(CENTER)
            fill(0)
            textSize(20)
            text(game.message, width/2 + 2, height/2 + 2)
            fill(255, 255, 0)
            text(game.message, width/2, height/2)
        print("Rendering message: %s" % game.message)
    except Exception, e:
        print("Error rendering message: %s" % str(e))

def draw_attack_selection():
    try:
        if game.selected_card:
            card_index = game.player.deck.index(game.selected_card)
            card_x = 50 + card_index * 110
            card_y = height - 140
            # Draw attack options for the selected card
            for j, attack in enumerate(game.selected_card.attacks):
                attack_y = card_y - (len(game.selected_card.attacks) - 1 - j) * 40
                progress = game.selected_card.get_load_progress(attack)
                # Highlight the attack if hovered and ready
                if card_x <= mouseX <= card_x + 150 and attack_y - 20 <= mouseY <= attack_y + 20 and progress >= 1.0:
                    fill(0, 255, 0)
                    stroke(0, 255, 0)
                    strokeWeight(3)
                elif card_x <= mouseX <= card_x + 150 and attack_y - 20 <= mouseY <= attack_y + 20:
                    fill(255, 255, 0)
                    stroke(255, 255, 0)
                    strokeWeight(3)
                else:
                    fill(200)
                    stroke(0)
                    strokeWeight(2)
                rect(card_x, attack_y - 20, 150, 40, 5)
                strokeWeight(1)
                stroke(0)
                textFont(font_regular)
                textAlign(LEFT)
                fill(0)
                textSize(12)
                text("%s: ATK %d, HP %d, %.1fs" % (
                    attack.name, attack.attack, attack.health, attack.load_time_seconds
                ), card_x + 5, attack_y + 5)
                fill(255, 0, 0)
                rect(card_x + 100, attack_y - 15, 40, 5)
                fill(0, 255, 0)
                rect(card_x + 100, attack_y - 15, 40 * progress, 5)
            print("Rendering attack options for %s" % game.selected_card.name)
    except Exception, e:
        print("Error rendering attack selection: %s" % str(e))

def draw_aim_indicator():
    try:
        if game.current_enemy < len(game.enemies):
            textAlign(CENTER)
            textFont(font_bold)
            fill(0)
            textSize(14)
            text("Click enemy to attack!", width/2 + 1, height/2 - 49)
            fill(255)
            text("Click enemy to attack!", width/2, height/2 - 50)
        print("Rendering aim indicator")
    except Exception, e:
        print("Error rendering aim indicator: %s" % str(e))

def draw_pause_overlay():
    try:
        fill(0, 0, 0, 150)
        rect(0, 0, width, height)
        textFont(font_bold)
        textAlign(CENTER, CENTER)
        fill(0)
        textSize(32)
        text("Paused", width/2 + 2, height/2 - 48)
        fill(255)
        text("Paused", width/2, height/2 - 50)
        textSize(20)
        fill(0)
        text("Press P to Resume", width/2 + 1, height/2 + 51)
        fill(255)
        text("Press P to Resume", width/2, height/2 + 50)
        print("Rendering pause overlay")
    except Exception, e:
        print("Error rendering pause overlay: %s" % str(e))

def draw_gameover_screen():
    try:
        textFont(font_bold)
        textAlign(CENTER, CENTER)
        fill(0)
        textSize(32)
        if game.player.health <= 0:
            text("Game Over - You Lost!", width/2 + 2, height/2 - 48)
            fill(255)
            text("Game Over - You Lost!", width/2, height/2 - 50)
        else:
            text("Victory! All Enemies Defeated!", width/2 + 2, height/2 - 48)
            fill(255)
            text("Victory! All Enemies Defeated!", width/2, height/2 - 50)
        textSize(20)
        fill(0)
        text("Score: %d" % game.score, width/2 + 1, height/2 + 1)
        text("Battles Won: %d/%d" % (game.battles_won, len(game.enemies)), width/2 + 1, height/2 + 31)
        text("Press R to Restart", width/2 + 1, height/2 + 61)
        fill(255)
        text("Score: %d" % game.score, width/2, height/2)
        text("Battles Won: %d/%d" % (game.battles_won, len(game.enemies)), width/2, height/2 + 30)
        text("Press R to Restart", width/2, height/2 + 60)
        print("Rendering gameover screen")
    except Exception, e:
        print("Error rendering gameover screen: %s" % str(e))

def mousePressed():
    try:
        print("Mouse pressed at: (%s, %s) State: %s" % (mouseX, mouseY, game.state))
        if game.state == PLAYING:
            game.handle_card_click(mouseX, mouseY)
        elif game.state == SELECT_ATTACK:
            if game.selected_card:
                for i in range(len(game.selected_card.attacks)):
                    if game.handle_attack_click(mouseX, mouseY, i):
                        break
        elif game.state == AIM_ATTACK:
            game.handle_aim_click(mouseX, mouseY)
    except Exception, e:
        print("Error handling mouse press: %s" % str(e))

def keyPressed():
    try:
        print("Key pressed: %s State: %s" % (str(key), game.state))
        if key == 's' or key == 'S':
            if game.state == INTRO:
                game.state = PLAYING
                print("Starting game")
        elif key == 'p' or key == 'P':
            if game.state in [PLAYING, SELECT_ATTACK, AIM_ATTACK]:
                game.state = PAUSED
                print("Game paused")
            elif game.state == PAUSED:
                game.state = PLAYING
                print("Game resumed")
        elif key == 'r' or key == 'R':
            game.reset()
            print("Game reset")
    except Exception, e:
        print("Error handling key press: %s" % str(e))
