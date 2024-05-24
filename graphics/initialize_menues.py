# module for adding content to menues
# function names here are only the name of the menu

import copy
import math
from PhoenixGUI.util import sum_two_vectors
from PhoenixGUI import *
import pygame
from data.consts import CELESTIAL_BODY_TYPES_NAMES
from physics.celestial_body import CelestialBody
from physics.gas_giant import GasGiant
from physics.star import Star
from physics.terrestrial_body import TerrestrialBody
from util import round_seconds, round_to_significant_figures

YES_NO = {
    True: "Yes",
    False: "No"
}

def outliner(menu_handler: MenuHandler, 
             cbs: list[CelestialBody], 
             star_id: str, 
             show_moons_in_outliner: bool, 
             font, 
             invoke_command):
    
    BASE_POS = (10, 40)
    BUTTON_SIZE = (180, 40)
    SPACE_BETWEEN = 10

    added_planets = 0
    for cb in cbs:
        if (not show_moons_in_outliner
            and not isinstance(cb, Star)
            and cb.orbital_host != star_id):
            continue

        button_pos = (0, added_planets*(BUTTON_SIZE[1]+SPACE_BETWEEN))
        button = Button(sum_two_vectors(BASE_POS, button_pos),
                        enable_rect=True,
                        rect_length=BUTTON_SIZE[0],
                        rect_height=BUTTON_SIZE[1],
                        rect_color=(0, 0, 0, 0),
                        rect_outline_color=(0, 0, 0, 0),
                        rect_outline_hover_color=(255, 255, 255),
                        rect_outline_click_color=(140, 140, 140),
                        command=(invoke_command, [f"open_cb_menu {cb.id}"], {}))
        
        menu_handler.add_object("outliner", 
                                f"cb_button_{added_planets}", 
                                button)

        cb_icon = cb.visual.get_surface(30)
        image = Image(sum_two_vectors(button.pos, (5, 5)), cb_icon)
        menu_handler.add_object("outliner", 
                                f"cb_icon_{added_planets}", 
                                image)

        title_text = Text(sum_two_vectors(button.pos, (40, 5)), 
                          cb.name, font, 18, anchor="nw")
        
        menu_handler.add_object("outliner", 
                                f"cb_title_{added_planets}", 
                                title_text)

        cb_type_text = Text(sum_two_vectors(button.pos, (40, 35)),
                            CELESTIAL_BODY_TYPES_NAMES[type(cb)],
                            font, 14, anchor="sw")
        
        menu_handler.add_object("outliner", 
                                f"cb_type_{added_planets}", 
                                cb_type_text)

        added_planets += 1

def cb_menu(menu_handler: MenuHandler,
            cb: CelestialBody,
            host_cb: CelestialBody,
            cbs: list[CelestialBody],
            font: str,
            climate_images: dict[str, pygame.Surface],
            invoke_command):
    
    cb_menu = menu_handler.menues["cb_menu"]
    
    cb_menu.objects["title_text"].change_property("text", cb.name)

    SIZE = [900, 600]

    cb_menu.size = SIZE
    cb_menu.objects["top_bar"].size = [SIZE[0], 30]

    INFO_SIZE = [250, 500]
    cb_menu.objects["info_bg"].size = INFO_SIZE

    INFO_POS = [SIZE[0]-10, 40]
    cb_menu.objects["info_bg"].pos = INFO_POS
    cb_menu.objects["info_bg_title"].pos = \
        [INFO_POS[0]-INFO_SIZE[0]/2, INFO_POS[1]+10]
    
    properties = [["Size", round_to_significant_figures(cb.size, 3)]]
    
    for key in copy.copy(cb_menu.objects).keys():
        if key[:15] == "property_title_" or key[:9] == "property_":
            del cb_menu.objects[key]

    if isinstance(cb, TerrestrialBody):
        orbital_velocity = round_to_significant_figures(cb.orbital_velocity/1000,
                                                        3, make_int=True)

        properties.extend([
            ["Orbital host", host_cb.name],
            ["Tidally locked", YES_NO[cb.is_tidally_locked]],
            ["Orbital Velocity", f"{orbital_velocity} km/s"],
            ["Day length", round_seconds(cb.day_length)],
            ["Gravity", f"{cb.gravity} N"],
            ["SMA", cb.sma]
        ])

        # Remove day length if tidally locked, because it is not interesting.
        if cb.is_tidally_locked:
            del properties[4]

    ROW_HEIGHT = 40
    for i, (name, property) in enumerate(properties):
        pos = [INFO_POS[0]-INFO_SIZE[0]+10, (i+1)*INFO_POS[1]+ROW_HEIGHT]
        text = Text(pos, name, font, 18, anchor="w")
        menu_handler.add_object("cb_menu", f"property_title_{i}", text)

        pos = [INFO_POS[0]-10, (i+1)*INFO_POS[1]+ROW_HEIGHT]
        text = Text(pos, str(property), font, 18, anchor="e")
        menu_handler.add_object("cb_menu", f"property_{i}", text)

    object_ids = [
        "atmosphere_bg",
        "atmosphere_title",
        "thickness_text",
        "thickness_text_2",
        "moons_bg",
        "moons_title",
        "districts_bg",
        "districts_title"
    ]
    object_ids_startswith = [
        "atmosphere_name_text_",
        "atmosphere_share_text_",
        "cb_button_",
        "cb_icon_",
        "cb_title_",
        "district_picture_",
        "district_button_"
    ]
    menu_handler.delete_multiple_objects("cb_menu", object_ids, 
                                         object_ids_startswith)

    if isinstance(cb, TerrestrialBody):
        _init_districts(menu_handler, cb, font, climate_images)
        _init_atmosphere(menu_handler, cb, font)

    _init_moons(menu_handler, font, cb, cbs, invoke_command)

def _init_districts(menu_handler: MenuHandler, cb, font, climate_images):
    OFFSET = [10, 40]
    DISTANCE_BETWEEN = 10
    SIZE = list(climate_images.values())[0].get_size()[0]

    BG_SIZE = 4*SIZE + 5*DISTANCE_BETWEEN
    menu_shape = Shape(OFFSET,
                       (BG_SIZE, BG_SIZE+20),
                       (30, 35, 140),
                       "rect",
                       outline_width=1,
                       outline_color=(0, 0, 0))
    menu_handler.add_object("cb_menu", "districts_bg", menu_shape)

    pos = (OFFSET[0]+BG_SIZE/2, OFFSET[1]+17)
    text = Text(pos, "Districts", font, 20, anchor="c")
    menu_handler.add_object("cb_menu", "districts_title", text)

    OFFSET = sum_two_vectors(OFFSET, (10, 30))

    for i, district in enumerate(cb.districts):
        x, y = i % 4, math.floor(i / 4)
        pos = sum_two_vectors(OFFSET, ((SIZE+DISTANCE_BETWEEN)*x, 
                                       (SIZE+DISTANCE_BETWEEN)*y))

        image = climate_images[district.climate.image]
        menu_image = Image(pos, image)
        menu_handler.add_object("cb_menu", f"district_picture_{i}", menu_image)

        button = Button(pos,
                        enable_rect=True,
                        rect_length=SIZE,
                        rect_height=SIZE,
                        rect_color=(0, 0, 0, 0),
                        rect_outline_color=(0, 0, 0),
                        rect_outline_hover_color=(255, 255, 255),
                        rect_outline_click_color=(140, 140, 140),
                        rect_outline_width=2)
        menu_handler.add_object("cb_menu", f"district_button_{i}", button)

def _init_moons(menu_handler: MenuHandler, 
                font, 
                this_cb: CelestialBody, 
                cbs: list[CelestialBody],
                invoke_command):
    
    BASE_POS = [350, 40]
    SIZE = [200, 250]

    menu_shape = Shape(BASE_POS,
                       SIZE,
                       (30, 35, 140),
                       "rect",
                       outline_width=1,
                       outline_color=(0, 0, 0))
    menu_handler.add_object("cb_menu", "moons_bg", menu_shape)

    text = "Moons"
    if isinstance(this_cb, Star):
        text = "Planets"

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+17)
    menu_text = Text(pos, text, font, 20, anchor="c")
    menu_handler.add_object("cb_menu", "moons_title", menu_text)

    BUTTON_SIZE = (180, 40)
    SPACE_BETWEEN = 10
    BUTTONS_OFFSET = 30

    added_cbs = 0
    for cb in cbs:
        if not isinstance(cb, Star) and cb.orbital_host == this_cb.id:

            button_pos = (10, added_cbs * (BUTTON_SIZE[1] + SPACE_BETWEEN)
                              + BUTTONS_OFFSET)
            
            button = Button(sum_two_vectors(BASE_POS, button_pos),
                            enable_rect=True,
                            rect_length=BUTTON_SIZE[0],
                            rect_height=BUTTON_SIZE[1],
                            rect_color=(0, 0, 0, 0),
                            rect_outline_color=(0, 0, 0, 0),
                            rect_outline_hover_color=(255, 255, 255),
                            rect_outline_click_color=(140, 140, 140),
                            command=(invoke_command, [f"open_cb_menu {cb.id}"], {}))
            
            menu_handler.add_object("cb_menu", 
                                    f"cb_button_{added_cbs}", 
                                    button)

            cb_icon = cb.visual.get_surface(30)
            image = Image(sum_two_vectors(button.pos, (5, 5)), cb_icon)
            menu_handler.add_object("cb_menu", 
                                    f"cb_icon_{added_cbs}", 
                                    image)

            title_text = Text(sum_two_vectors(button.pos, (40, BUTTON_SIZE[1]/2)),
                              cb.name, font, 18, anchor="w")

            menu_handler.add_object("cb_menu", 
                                    f"cb_title_{added_cbs}", 
                                    title_text)
            
            added_cbs += 1

def _init_atmosphere(menu_handler: MenuHandler, tb: TerrestrialBody, font):
    BASE_POS = (350, 300)
    SIZE = (200, 250)

    menu_shape = Shape(BASE_POS,
                       SIZE,
                       (30, 35, 140),
                       "rect",
                       outline_width=1,
                       outline_color=(0, 0, 0))
    menu_handler.add_object("cb_menu", "atmosphere_bg", menu_shape)

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+17)
    menu_text = Text(pos, "Atmosphere", font, 20, anchor="c")
    menu_handler.add_object("cb_menu", "atmosphere_title", menu_text)

    menu_text = Text(sum_two_vectors(BASE_POS, (10, 40)), 
                     "Thickness:", font, 18, anchor="w")
    menu_handler.add_object("cb_menu", "thickness_text", menu_text)

    text = str(round(tb.atmosphere.get_thickness(tb.size)))
    menu_text = Text(sum_two_vectors(BASE_POS, (SIZE[0]-10, 40)), 
                     text, font, 18, anchor="e")
    menu_handler.add_object("cb_menu", "thickness_text_2", menu_text)

    Y_COMPONENT_OFFSET = 70
    Y_SHARE_OFFSET = 30
    shares = tb.atmosphere.get_composition_shares()
    for i, (name, share) in enumerate(shares.items()):
        pos = sum_two_vectors(BASE_POS, 
                              (10, Y_SHARE_OFFSET*i+Y_COMPONENT_OFFSET))
        
        menu_text = Text(pos, name, font, 18, anchor="w")
        menu_handler.add_object("cb_menu",
                                f"atmosphere_name_text_{i}",
                                menu_text)
        
        pos = sum_two_vectors(BASE_POS, 
                              (SIZE[0]-10, Y_SHARE_OFFSET*i+Y_COMPONENT_OFFSET))
        
        menu_text = Text(pos, f"{round(100*share, 2)} %", font, 18, anchor="e")
        menu_handler.add_object("cb_menu", 
                                f"atmosphere_share_text_{i}", 
                                menu_text)
