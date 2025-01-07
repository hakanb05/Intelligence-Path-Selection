# """
# Platformer Game
# """
# import math
# import arcade

# # Constants
# SCREEN_WIDTH = int(1920 * 0.8)
# SCREEN_HEIGHT = int(1080 * 0.8)
# SCREEN_TITLE = "Peter Post: Op avontuur"

# # Constants used to scale our sprites from their original size
# TILE_SIZE = 128
# CHARACTER_SCALING = 0.5
# TILE_SCALING = 0.5
# COIN_SCALING = 0.0

# # Map size (change this to size of the map.tmx)!
# MAP_WIDTH_TILES = 500
# MAP_HEIGHT_TILES = 40
# SCALED_MAP_WIDTH_PIXELS = MAP_WIDTH_TILES * TILE_SIZE * TILE_SCALING
# SCALED_MAP_HEIGHT_PIXELS = MAP_HEIGHT_TILES * TILE_SIZE * TILE_SCALING

# PLAYER_HITBOX = arcade.get_rectangle_points(0, 0, 224, 256)

# # DEFAULT Movement speed of player, in pixels per frame
# PLAYER_MOVEMENT_SPEED = 5
# UPDATES_PER_FRAME = int(PLAYER_MOVEMENT_SPEED * 1.5)
# GRAVITY = 1
# PLAYER_JUMP_SPEED = 15

# # How many pixels to keep as a minimum margin between the character
# # and the edge of the screen.
# LEFT_VIEWPORT_MARGIN = SCREEN_WIDTH / 4
# RIGHT_VIEWPORT_MARGIN = SCREEN_WIDTH - LEFT_VIEWPORT_MARGIN
# BOTTOM_VIEWPORT_MARGIN = SCREEN_HEIGHT / 6
# TOP_VIEWPORT_MARGIN = SCREEN_HEIGHT / 2

# # Index of textures, first element faces left, second faces right
# TEXTURE_LEFT = 0
# TEXTURE_RIGHT = 1

# # Constants used to track if the player is facing left or right
# RIGHT_FACING = 0
# LEFT_FACING = 1

# # Camera constants
# PLAYER_START_X = 10 * TILE_SIZE * TILE_SCALING
# PLAYER_START_Y = (MAP_HEIGHT_TILES - 29) * TILE_SIZE * TILE_SCALING
# CAMERA_START_X = 7 * TILE_SIZE / 2
# CAMERA_START_Y = 13 * TILE_SIZE / 2

# # Locations
# MAILBOX_POS = [31 * TILE_SIZE * TILE_SCALING, 18 * TILE_SIZE * TILE_SCALING]
# FIRST_POSTOFFICE_X = 130 * TILE_SIZE * TILE_SCALING
# A
# SECOND_AIRPORT_X = 371 * TILE_SIZE * TILE_SCALING
# SECOND_POSTOFFICE_X = 445 * TILE_SIZE * TILE_SCALING


# def load_texture_pair(filename):
#     """
#     Load a texture pair, with the second being a mirror image.
#     """
#     return [
#         arcade.load_texture(filename),
#         arcade.load_texture(filename, mirrored=True)
#     ]


# class Player(arcade.Sprite):

#     def __init__(self, name='default', wall_list=None):
#         super().__init__()

#         self.speed = PLAYER_MOVEMENT_SPEED
#         self.jumpspeed = PLAYER_JUMP_SPEED
#         self.allow_jump = True
#         self.gravity = GRAVITY

#         # Used for flipping between image sequences
#         self.cur_texture = 0
#         # Default to face-right
#         self.character_face_direction = RIGHT_FACING
#         main_path = "resources/images"

#         if name == "default" or name == "player":
#             self.name = "player"

#             tex_source = f"{main_path}/{name}_1"

#             # Load textures for idle standing
#             self.idle_texture_pair = load_texture_pair(f"{tex_source}_idle.png")

#             # Load textures for walking
#             self.walk_textures = []
#             for i in range(4):
#                 texture = load_texture_pair(f"{tex_source}_walk_{i}.png")
#                 self.walk_textures.append(texture)

#             self.set_hit_box(PLAYER_HITBOX)
#             # By default, face right.
#             self.texture = self.idle_texture_pair[self.character_face_direction]

#             self.scale = CHARACTER_SCALING


#         elif name == "parcelcar":
#             self.name = "parcelcar"

#             tex_source = f"{main_path}/{name}_1"
#             # Load textures for idle standing
#             print("load", f"{main_path}/{name}_1_left.png")
#             self.idle_texture_pair = [arcade.load_texture(f"{tex_source}_right.png"),
#                                       arcade.load_texture(f"{tex_source}_left.png")]

#             # By default, face right.
#             self.texture = self.idle_texture_pair[self.character_face_direction]

#             self.scale = CHARACTER_SCALING
#             self.speed = PLAYER_MOVEMENT_SPEED * 2
#             self.allow_jump = False


#         elif name == "plane":
#             self.name = "plane"
#             img_source = "resources/images/plane_1.png"
#             self.scale = CHARACTER_SCALING
#             self.textures = []
#             # face left
#             texture = arcade.load_texture(img_source, mirrored=True)
#             self.textures.append(texture)
#             # face right
#             texture = arcade.load_texture(img_source)
#             self.textures.append(texture)

#             # By default, face right.
#             self.texture = texture

#             self.speed = PLAYER_MOVEMENT_SPEED
#             self.jumpspeed = int(PLAYER_JUMP_SPEED * 0.70)
#             self.gravity = GRAVITY * 0.75

#         # Create the 'physics engine'
#         self.physics_engine = arcade.PhysicsEnginePlatformer(self,
#                                                              wall_list,
#                                                              self.gravity)

#     def update_animation(self, delta_time: float = 1 / 60):
#         # Figure out if we need to flip face left or right
#         if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
#             self.character_face_direction = LEFT_FACING
#         elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
#             self.character_face_direction = RIGHT_FACING

#         if self.name == "parcelcar":
#             # animation
#             self.texture = self.idle_texture_pair[self.character_face_direction]
#             return
#         if self.name == "plane":
#             pass
#         elif self.name == "player":
#             # Idle animation
#             if self.change_x == 0 and self.change_y == 0:
#                 self.texture = self.idle_texture_pair[self.character_face_direction]
#                 return

#             # Walking animation
#             self.cur_texture += 1
#             if self.cur_texture >= len(self.walk_textures) * UPDATES_PER_FRAME:
#                 self.cur_texture = 0
#             frame = self.cur_texture // UPDATES_PER_FRAME
#             direction = self.character_face_direction
#             self.texture = self.walk_textures[frame][direction]


# class MyGame(arcade.Window):
#     """
#     Main application class.
#     """

#     def __init__(self):

#         # Call the parent class and set up the window
#         super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

#         # These are 'lists' that keep track of our sprites. Each sprite should
#         # go into a list.
#         self.background_list = None
#         self.wall_list = None
#         self.water_list = None
#         self.tree_list = None
#         self.buildings_list = None
#         self.player_list = None
#         self.dont_touch_list = None
#         # Separate variable that holds the player sprite
#         self.player_sprite = None
#         self.car_sprite = None

#         # # Our physics engine
#         # self.physics_engine = None

#         # Used to keep track of our scrolling
#         self.view_bottom = 0
#         self.view_left = 0

#         # Buidling positions
#         self.building_positions_x = [0, FIRST_POSTOFFICE_X, FIRST_AIRPORT_X, SECOND_AIRPORT_X]

#         self.sprite_name = 'player'
#         self.is_player = True
#         self.is_parcelcar = False
#         self.is_plane = False

#         self.conversations = {}

#         arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

#         self.right_pressed = False
#         self.left_pressed = False
#         self.down_pressed = False
#         self.up_pressed = False
#         self.e_pressed = False

#         self.deaths = 0
#         self.spawn_location_x = PLAYER_START_X
#         self.spawn_location_y = PLAYER_START_Y
#         self.block_first = True

#         self.allow_player_movement = True

#     def setup(self):
#         """ Set up the game here. Call this function to restart the game. """

#         # # Testing
#         # self.spawn_location_x = 476 * TILE_SIZE * TILE_SCALING
#         # self.spawn_location_y = (40 - 7) * TILE_SIZE * TILE_SCALING
#         # self.block_first = False
#         # self.is_player = True
#         # self.is_plane = False
#         # self.is_parcelcar = False
#         # self.sprite_name = 'player'

#         # Used to keep track of our scrolling
#         self.view_bottom = CAMERA_START_X
#         self.view_left = CAMERA_START_Y

#         # Set viewport to correct height #TODO
#         arcade.set_viewport(self.view_left,
#                             SCREEN_WIDTH + self.view_left,
#                             self.view_bottom,
#                             SCREEN_HEIGHT + self.view_bottom)

#         # Create the Sprite lists
#         self.player_list = arcade.SpriteList()
#         self.wall_list = arcade.SpriteList()
#         self.water_list = arcade.SpriteList()
#         self.tree_list = arcade.SpriteList()
#         self.buildings_list = arcade.SpriteList()
#         self.background_list = arcade.SpriteList()
#         self.dont_touch_list = arcade.SpriteList()

#         # --- Load in a map from the tiled editor ---

#         # Name of map file to load
#         # map_name = ":resources:tmx_maps/map.tmx"
#         map_name = "avi_map.tmx"
#         # Name of the layer in the file that has our platforms/walls
#         platforms_layer_name = 'Platforms'

#         # Read in the tiled map
#         my_map = arcade.tilemap.read_tmx(map_name)

#         # -- Platforms
#         self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
#                                                       layer_name=platforms_layer_name,
#                                                       scaling=TILE_SCALING,
#                                                       use_spatial_hash=True)

#         # -- Backgrounds
#         self.tree_list = arcade.tilemap.process_layer(my_map, 'Trees', TILE_SCALING)
#         self.buildings_list = arcade.tilemap.process_layer(my_map, 'Buildings', TILE_SCALING)
#         self.water_list = arcade.tilemap.process_layer(my_map, 'Water', TILE_SCALING)

#         # -- Don't Touch Layer
#         self.dont_touch_list = arcade.tilemap.process_layer(my_map, 'DontTouch', TILE_SCALING,
#                                                             use_spatial_hash=True)

#         # -- Background
#         self.background_list = arcade.tilemap.process_layer(my_map, 'Background', TILE_SCALING)

#         # --- Other stuff
#         # Set the background :Wcolor
#         if my_map.background_color:
#             arcade.set_background_color(my_map.background_color)

#         self.get_conversations()
#         self.current_conversation = None
#         print(self.conversations)

#         # Set up the player, specifically placing it at these coordinates.
#         # image_source = ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
#         # self.player_sprite = arcade.Sprite("resources/images/player_1.png", CHARACTER_SCALING*0.5)
#         self.player_sprite = Player(self.sprite_name, self.wall_list)
#         self.player_sprite.center_y = self.spawn_location_y
#         #       self.player_sprite.center_x = 7000
#         self.player_sprite.center_x = self.spawn_location_x
#         self.player_list.append(self.player_sprite)

#     def get_conversations(self):
#         f = open("resources/text/conversations", "r")
#         for line in f:
#             splitted = line.rstrip().split("=")
#             pos = splitted[0].split(";")
#             text_posx = int(float(pos[0]) * TILE_SIZE * TILE_SCALING)
#             text_posy = int(MAP_HEIGHT_TILES - float(pos[1])) * TILE_SIZE * TILE_SCALING
#             print(text_posx, text_posy)
#             # text_position = [(int(x)*TILE_SIZE*TILE_SCALING) for x in splitted[0].split(";")]
#             self.conversations[(text_posx, text_posy)] = splitted[1].split(";")
#         print(self.conversations)

#     def on_draw(self):
#         """ Render the screen. """

#         # Clear the screen to the background color
#         arcade.start_render()

#         # Draw our sprites
#         self.background_list.draw()
#         self.dont_touch_list.draw()
#         self.tree_list.draw()
#         self.wall_list.draw()
#         self.buildings_list.draw()

#         # # Gametitel block
#         # x, y = 13 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (24.5 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_rectangle_filled(x, y, 8 * TILE_SIZE * TILE_SCALING, 5 * TILE_SIZE * TILE_SCALING,
#         #                              arcade.csscolor.OLD_LACE)
#         # arcade.draw_rectangle_outline(x, y, 8 * TILE_SIZE * TILE_SCALING, 5 * TILE_SIZE * TILE_SCALING,
#         #                               arcade.csscolor.BLACK, TILE_SIZE * TILE_SCALING * 0.25)
#         # # Gametitel tekst
#         # x, y = 13 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (23 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_text("PIETER POST", x, y,
#         #                  arcade.csscolor.BLACK, 72, anchor_x="center", anchor_y="center", bold=True)
#         # x, y = 13 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (24 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_text("Op avontuur", x, y,
#         #                  arcade.csscolor.BLACK, 35, anchor_x="center", anchor_y="center", italic=True)
#         # x, y = 13 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (25 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_text("AVI2 - Integratie Onderzoek", x, y,
#         #                  arcade.csscolor.BLACK, 24, anchor_x="center", anchor_y="center", )
#         # x, y = 13 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (26.5 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_text("Gemaakt door: Abdelilah Ahbari, Jakob Kaiser en Rico Ronde", x, y,
#         #                  arcade.csscolor.BLACK, 15, anchor_x="center", anchor_y="center", )

#         # # Gamecontrols block TODO
#         # x, y = 4.5 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (24.5 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_rectangle_filled(x, y, 5 * TILE_SIZE * TILE_SCALING, 5 * TILE_SIZE * TILE_SCALING,
#         #                              arcade.csscolor.OLD_LACE)
#         # arcade.draw_rectangle_outline(x, y, 5 * TILE_SIZE * TILE_SCALING, 5 * TILE_SIZE * TILE_SCALING,
#         #                               arcade.csscolor.BLACK, TILE_SIZE * TILE_SCALING * 0.25)
#         # # Controls tekst
#         # x, y = 13 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (26.5 * TILE_SIZE * TILE_SCALING)
#         # arcade.draw_text("Controls:", x, y,
#         #                  arcade.csscolor.WHITE, 35, anchor_x="center", anchor_y="center", )

#         # Afgrondtekst
#         x, y = 81.5 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (27.5 * TILE_SIZE * TILE_SCALING)
#         arcade.draw_text("Pas op voor de afgrond!", x, y,
#                          arcade.csscolor.WHITE, 24, anchor_x="center", anchor_y="center")
#         # Vliegtuig help tekst
#         x, y = 239 * TILE_SIZE * TILE_SCALING, SCALED_MAP_HEIGHT_PIXELS - (27 * TILE_SIZE * TILE_SCALING)
#         arcade.draw_text("Pas op voor de afgrond! Vlieg omhoog en ontwijk de obstakels!", x, y,
#                          arcade.csscolor.WHITE, 34, anchor_x="left", anchor_y="center")

#         self.player_list.draw()
#         self.water_list.draw()

#         if self.current_conversation:
#             text, index = self.current_conversation
#             background_color = (0, 0, 0, 200)
#             arcade.draw_rectangle_filled(int(SCREEN_WIDTH / 2 + self.view_left),
#                                          TILE_SIZE * TILE_SCALING * 1.125 + self.view_bottom,
#                                          int(SCREEN_WIDTH / 2 + self.view_left),
#                                          TILE_SIZE * TILE_SCALING * 1.75,
#                                          background_color)
#             arcade.draw_text(text[index], SCREEN_WIDTH / 2 + self.view_left,
#                              TILE_SIZE * TILE_SCALING * 1.5 + self.view_bottom,
#                              arcade.csscolor.WHITE, 25, anchor_x="center", anchor_y="center")
#             arcade.draw_text("(Druk op [E] om door te gaan)", SCREEN_WIDTH / 2 + self.view_left,
#                              TILE_SIZE * TILE_SCALING * 0.75 + self.view_bottom,
#                              arcade.csscolor.WHITE, 25, anchor_x="center", anchor_y="center")

#         # Death Counter
#         deaths_text = f"Deaths: {self.deaths}"
#         arcade.draw_text(deaths_text, 10 + self.view_left,
#                          10 + self.view_bottom, arcade.csscolor.WHITE, 18)

#     def on_key_press(self, key, modifiers):
#         """ Called whenever a key is pressed. """

#         if self.allow_player_movement:
#             if key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
#                 self.up_pressed = True
#                 if self.is_plane:
#                     self.player_sprite.change_y = self.player_sprite.jumpspeed
#                 elif self.player_sprite.physics_engine.can_jump() and self.player_sprite.allow_jump:
#                     self.player_sprite.change_y = self.player_sprite.jumpspeed

#             elif key == arcade.key.LEFT or key == arcade.key.A:
#                 if self.is_plane:
#                     pass
#                 else:
#                     self.left_pressed = True
#                     self.player_sprite.change_x = -self.player_sprite.speed
#             elif key == arcade.key.RIGHT or key == arcade.key.D:
#                 if not (self.player_sprite.center_x >= 4900 and self.block_first):
#                     self.right_pressed = True
#                     self.player_sprite.change_x = self.player_sprite.speed
#         else:
#             self.up_pressed = False
#             self.left_pressed = False
#             self.right_pressed = False
#             self.player_sprite.change_x = 0
#             self.player_sprite.change_y = 0

#         if key == arcade.key.E:
#             self.e_pressed = True
#         if key == arcade.key.BACKSPACE:
#             MyGame.setup(self)

#     def on_key_release(self, key, modifiers):
#         """Called when the user releases a key. """

#         if self.allow_player_movement:
#             if key == arcade.key.LEFT or key == arcade.key.A:
#                 self.left_pressed = False

#                 if self.right_pressed or self.is_plane:
#                     self.player_sprite.change_x = self.player_sprite.speed
#                 else:
#                     self.player_sprite.change_x = 0
#             elif key == arcade.key.RIGHT or key == arcade.key.D:
#                 self.right_pressed = False

#                 if self.is_plane:
#                     self.player_sprite.change_x = self.player_sprite.speed
#                 elif self.left_pressed:
#                     self.player_sprite.change_x = -self.player_sprite.speed
#                 else:
#                     self.player_sprite.change_x = 0
#             elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
#                 self.up_pressed = False

#     def gen_text(self):
#         player_x = int(self.player_sprite.center_x)
#         player_y = int(self.player_sprite.center_y)
#         # print(player_x,player_y)

#         for (x, y) in self.conversations:
#             # print(math.dist([x,y], [player_x,player_y]))
#             # if math.dist([x,y], [player_x,player_y]) < (TILE_SIZE*TILE_SCALING):
#             if math.dist([x], [player_x]) <= TILE_SIZE * TILE_SCALING * 0.5 and player_y >= y:
#                 self.e_pressed = False
#                 self.player_sprite.change_x = 0
#                 self.allow_player_movement = False
#                 self.current_conversation = (self.conversations[(x, y)], 0)
#                 print(x, y, self.conversations[(x, y)])
#                 if x == 31.5 * TILE_SIZE * TILE_SCALING:
#                     self.block_first = False
#                     if ((int(77 * TILE_SIZE * TILE_SCALING),
#                          int((MAP_HEIGHT_TILES - 29) * TILE_SIZE * TILE_SCALING))) in self.conversations:
#                         self.conversations.pop((int(77 * TILE_SIZE * TILE_SCALING),
#                                                 int((MAP_HEIGHT_TILES - 29) * TILE_SIZE * TILE_SCALING)))
#                 self.conversations.pop((x, y))
#                 break
#         # print(f"{self.player_sprite.jumpspeed}      jumpspeed {jumpspeed}")
#         if self.current_conversation and self.e_pressed:
#             name, index = self.current_conversation
#             if index + 1 < len(name):
#                 self.current_conversation = (name, index + 1)
#             else:
#                 self.allow_player_movement = True
#                 self.current_conversation = None
#             self.e_pressed = False

#     def on_update(self, delta_time):
#         """ Movement and game logic """
#         # Move the player with the physics engine
#         self.player_list.update()
#         self.player_sprite.physics_engine.update()

#         # Update the players animation
#         self.player_list.update_animation()
#         self.gen_text()

#         if self.player_sprite.center_x >= 4900 and self.block_first:
#             self.right_pressed = False
#             self.player_sprite.change_x = 0

#         # CHANGE CHARACTER from player to parcelcar at FIRST_POSTOFFICE_X
#         if FIRST_POSTOFFICE_X + 128 > self.player_sprite.center_x > FIRST_POSTOFFICE_X and self.is_player:
#             print("change player to parcelcar")
#             self.is_player = False
#             self.is_parcelcar = True
#             x = self.player_sprite.center_x
#             y = self.player_sprite.bottom

#             self.car_sprite = Player("parcelcar", self.wall_list)
#             self.car_sprite.center_x = x
#             self.car_sprite.bottom = y
#             self.player_sprite.remove_from_sprite_lists()
#             self.player_list.append(self.car_sprite)
#             self.player_sprite = self.car_sprite
#             self.spawn_location_x = FIRST_POSTOFFICE_X
#             self.spawn_location_y = self.player_sprite.center_y

#             if self.right_pressed:
#                 self.player_sprite.change_x = self.player_sprite.speed

#         # CHANGE CHARACTER from parcelcar to plane at FIRST_AIRPORT_X
#         if FIRST_AIRPORT_X + 128 > self.player_sprite.center_x > FIRST_AIRPORT_X and self.is_parcelcar:
#             print("change player to plane")
#             self.is_parcelcar = False
#             self.is_plane = True
#             x = self.player_sprite.center_x
#             y = self.player_sprite.bottom

#             self.plane_sprite = Player("plane", self.wall_list)
#             self.plane_sprite.center_x = x
#             self.plane_sprite.bottom = y
#             self.player_sprite.remove_from_sprite_lists()
#             self.player_list.append(self.plane_sprite)
#             self.player_sprite = self.plane_sprite
#             self.player_sprite.change_x = self.player_sprite.speed
#             self.spawn_location_x = FIRST_AIRPORT_X + 128
#             self.spawn_location_y = self.player_sprite.center_y

#         # CHANGE CHARACTER from plane to parcelcar at SECOND_AIRPORT_X
#         if SECOND_AIRPORT_X + 128 > self.player_sprite.center_x > SECOND_AIRPORT_X and self.is_plane:
#             print("change plane to parcelcar")
#             self.is_plane = False
#             self.is_parcelcar = True
#             x = self.player_sprite.center_x
#             y = self.player_sprite.bottom

#             self.car_sprite = Player("parcelcar", self.wall_list)
#             self.car_sprite.center_x = x
#             self.car_sprite.bottom = y
#             self.player_sprite.remove_from_sprite_lists()
#             self.player_list.append(self.car_sprite)
#             self.player_sprite = self.car_sprite
#             self.spawn_location_x = SECOND_AIRPORT_X
#             self.spawn_location_y = self.player_sprite.center_y

#         # CHANGE CHARACTER from parcelcar to player at SECOND_POSTOFFICE_X
#         if SECOND_POSTOFFICE_X + 128 > self.player_sprite.center_x > SECOND_POSTOFFICE_X and self.is_parcelcar:
#             print("change parcelcar to player")
#             self.is_parcelcar = False
#             self.isplayer = True
#             x = self.player_sprite.center_x
#             y = self.player_sprite.bottom

#             self.character_sprite = Player("player", self.wall_list)
#             self.character_sprite.center_x = x
#             self.character_sprite.bottom = y
#             self.player_sprite.remove_from_sprite_lists()
#             self.player_list.append(self.character_sprite)
#             self.player_sprite = self.character_sprite
#             self.player_sprite.change_x = self.player_sprite.speed
#             self.spawn_location_x = SECOND_POSTOFFICE_X
#             self.spawn_location_y = self.player_sprite.center_y

#         # --- Manage Scrolling ---

#         # Track if we need to change the viewport

#         changed = False

#         # Scroll left
#         left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
#         if self.player_sprite.center_x < left_boundary:
#             self.view_left -= left_boundary - self.player_sprite.center_x
#             changed = True

#         # Scroll right
#         right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
#         if self.player_sprite.center_x > right_boundary:
#             self.view_left += self.player_sprite.center_x - right_boundary
#             changed = True

#         # Scroll alleen als je niet in de flappy plane minigame zit.
#         if not FIRST_AIRPORT_X < self.player_sprite.center_x < SECOND_AIRPORT_X:
#             # Scroll up
#             top_boundary = self.view_bottom + SCREEN_HEIGHT - 0.3 * TOP_VIEWPORT_MARGIN
#             if self.player_sprite.top > top_boundary:
#                 self.view_bottom += self.player_sprite.top - top_boundary
#                 changed = True

#             # Scroll down
#             bottom_boundary = self.view_bottom + 1.3 * BOTTOM_VIEWPORT_MARGIN
#             if self.player_sprite.bottom < bottom_boundary:
#                 self.view_bottom -= bottom_boundary - self.player_sprite.bottom
#                 changed = True

#         if changed:
#             # Only scroll to integers. Otherwise we end up with pixels that
#             # don't line up on the screen

#             self.view_bottom = int(self.view_bottom)
#             self.view_left = int(self.view_left)

#             # Do the scrolling
#             arcade.set_viewport(self.view_left,
#                                 SCREEN_WIDTH + self.view_left,
#                                 self.view_bottom,
#                                 SCREEN_HEIGHT + self.view_bottom)

#         # --- Sprite change Check ---

#         # if self.player_sprite.center_x > self.building_positions_x[1]:
#         #     self.player_sprite.
#         #     self.player_sprite = arcade.Sprite('resources/images/parcelcar_1.png', CHARACTER_SCALING)

#         # self.player_sprite.center_x = self.player_sprite.center_x
#         # self.player_sprite.center_y = self.player_sprite.center_y + 128

#         # Did the player touch something they should not?
#         if arcade.check_for_collision_with_list(self.player_sprite, self.dont_touch_list):
#             # self.is_plane = False
#             # self.is_parcelcar = False
#             # self.is_player = True
#             # self.player_sprite = Player("player", self.wall_list)
#             # self.player_list.append(self.player_sprite)

#             self.deaths += 1
#             self.player_sprite.change_y = 0
#             self.player_sprite.center_x = self.spawn_location_x
#             self.player_sprite.center_y = self.spawn_location_y

#             # Set the camera to the start
#             self.view_bottom = CAMERA_START_X
#             self.view_left = CAMERA_START_Y
#             changed_viewport = True
#         print(self.player_sprite.center_x, self.player_sprite.center_y)
#         if self.player_sprite.center_x > 539 * TILE_SIZE * TILE_SCALING and self.player_sprite.center_y < (
#                 MAP_HEIGHT_TILES - 18) * TILE_SIZE * TILE_SCALING:
#             arcade.window_commands.close_window()


# def main():
#     """ Main method """
#     window = MyGame()
#     window.setup()
#     arcade.run()


# if __name__ == "__main__":
#     main()
#     print("GAME ENDED")
