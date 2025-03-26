# module for adding content to menues
# function names here are only the name of the menu

import copy
import math
from PhoenixGUI.util import sum_two_vectors, sum_multiple_vectors
from PhoenixGUI import *
import pygame
from data.consts import CELESTIAL_BODY_TYPES_NAMES
from physics.atmosphere import GASES, GASES_NAMES
from physics.atmosphere_calculator import AtmosphereCalculator
from physics.celestial_body import CelestialBody
from physics.planetary_body import PlanetaryBody
from physics.star import Star
from physics.star_system import StarSystem
from physics.terraformprojects import PROJECTS, PROPERTY_UNITS
from physics.terrestrial_body import TerrestrialBody
from society.civ import Civ
from society.species import CHARACTERISTICS, CHARACTERISTICS_NAMES, ENVIRONMENTS_NAMES, HABITAT_PREFERENCES_NAMES, Species
from util import orbital_vel_to_orbital_period, round_and_add_suffix, round_seconds, round_to_significant_figures

YES_NO = {
    True: "Yes",
    False: "No"
}

def outliner(menu_handler: MenuHandler, 
             cbs: list[CelestialBody], 
             star_id: str, 
             show_moons_in_outliner: bool, 
             font, 
             open_cb_menu_command):
    
    object_ids = []
    object_ids_startswith = ["cb_button_", "cb_icon_", "cb_title_", "cb_type_"]
    menu_handler.delete_multiple_objects("outliner_scroll", 
                                         object_ids, 
                                         object_ids_startswith)
    
    BASE_POS = (10, 0)
    BUTTON_SIZE = (180, 40)
    SPACE_BETWEEN = 10

    added_planets = 0
    for cb in cbs:
        if (not show_moons_in_outliner
            and isinstance(cb, PlanetaryBody)
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
                        command=lambda arg=f"open_cb_menu {cb.id}": open_cb_menu_command(arg))
        
        menu_handler.add_object("outliner_scroll", 
                                f"cb_button_{added_planets}", 
                                button)

        cb_icon = cb.visual.get_surface(30)
        image = Image(sum_two_vectors(button.pos, (5, 5)), cb_icon)
        menu_handler.add_object("outliner_scroll", 
                                f"cb_icon_{added_planets}", 
                                image)

        title_text = Text(sum_two_vectors(button.pos, (40, 5)), 
                          cb.name, font, 18, anchor="nw")
        
        menu_handler.add_object("outliner_scroll", 
                                f"cb_title_{added_planets}", 
                                title_text)

        cb_type_text = Text(sum_two_vectors(button.pos, (40, 35)),
                            CELESTIAL_BODY_TYPES_NAMES[cb.type],
                            font, 14, anchor="sw")
        
        menu_handler.add_object("outliner_scroll", 
                                f"cb_type_{added_planets}", 
                                cb_type_text)

        added_planets += 1

def cb_menu(menu_handler: MenuHandler,
            cb: CelestialBody,
            host_cb: CelestialBody,
            cbs: list[CelestialBody],
            font: str,
            climate_images: dict[str, pygame.Surface],
            building_images: dict[str, pygame.Surface],
            invoke_command,
            settings,
            menu_settings,
            images: dict[str, pygame.Surface],
            switch_atm_mode_command,
            species: dict[str, Species],
            player_civ: Civ,
            district_id: int):

    object_ids = [
        "thickness_text",
        "thickness_text_2",
        "switch_atm_mode_button"
    ]

    object_ids_startswith = [
        "property_",
        "property_title_",
        "atmosphere_name_text_",
        "atmosphere_share_text_",
        "district_picture_",
        "district_button_",
        "project_icon_",
        "project_text_",
        "population_text1_",
        "population_text2_",
        "habitability_text1_",
        "habitability_text2_",
        "building_button_",
        "building_picture_"
    ]

    menu_handler.delete_multiple_objects("cb_menu", object_ids, 
                                         object_ids_startswith)
    
    menu_handler.delete_multiple_objects("cb_submenu_moons", 
                                        [], ["cb_button_",
                                        "cb_icon_",
                                        "cb_title_"])
    
    menu_handler.menues["cb_submenu_moons"].deactivate()
    menu_handler.menues["cb_submenu_active_terraforming"].deactivate()
    menu_handler.menues["cb_submenu_available_terraforming"].deactivate()
    menu_handler.menues["cb_submenu_all_buildings"].deactivate()

    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["title_text"].change_property("text", cb.name)

    SIZE = [900, 600]

    cb_menu.size = SIZE
    cb_menu.objects["top_bar"].size = [SIZE[0], 30]

    to_deactivate = [
        "info_bg",
        "info_bg_title",
        "moons_bg",
        "moons_title",
        "atmosphere_bg",
        "atmosphere_title",
        "atmosphere_calculator_button",
        "districts_bg",
        "districts_title",
        "active_terraforming_bg",
        "active_terraforming_title",
        "available_terraforming_bg",
        "available_terraforming_title",
        "population_bg",
        "population_title",
        "habitability_bg",
        "habitability_title",
        "buildings_bg",
        "buildings_title",
        "all_buildings_bg",
        "all_buildings_title"
    ]

    for object_id in to_deactivate:
        cb_menu.objects[object_id].deactivate()

    cb_menu.objects["population_button"].activate()
    if not isinstance(cb, TerrestrialBody):
        cb_menu.objects["population_button"].deactivate()

    if isinstance(cb, TerrestrialBody) and menu_settings["cb_menu_mode"] == "overview":
        _init_atmosphere(menu_handler, cb, font, menu_settings["atmosphere_menu_mode"], 
                         images, switch_atm_mode_command)
        _init_districts(menu_handler, cb, climate_images, invoke_command)

    if menu_settings["cb_menu_mode"] == "overview":
        _init_properties(menu_handler, cb, host_cb, font, settings, SIZE)
        _init_moons(menu_handler, font, cb, cbs, invoke_command)

    elif menu_settings["cb_menu_mode"] == "terraforming":
        _init_terraforming(menu_handler, cb, font, images)

    elif menu_settings["cb_menu_mode"] == "population":
        _init_population(menu_handler, cb, font, species)
        _init_habitabilities(menu_handler, cb, font, species, player_civ)

    elif menu_settings["cb_menu_mode"] == "district":
        _init_population(menu_handler, cb, font, species, in_district=True, district_id=district_id)
        _init_habitabilities(menu_handler, cb, font, species, player_civ, in_district=True, district_id=district_id)
        _init_buildings(menu_handler, font, cb, district_id, building_images)

    elif menu_settings["cb_menu_mode"] == "all_buildings":
        _init_all_buildings(menu_handler, cb, building_images, font)

def _init_terraforming(menu_handler: MenuHandler, cb: CelestialBody, font, images):
    object_ids_startswith = [
        "project_button_",
        "project_icon_",
        "project_text_"
    ]
    menu_handler.delete_multiple_objects("cb_submenu_available_terraforming", [], object_ids_startswith)
    menu_handler.delete_multiple_objects("cb_submenu_active_terraforming", [], object_ids_startswith)

    menu_handler.menues["cb_submenu_active_terraforming"].activate()
    menu_handler.menues["cb_submenu_available_terraforming"].activate()

    cb_menu = menu_handler.menues["cb_menu"]
    active_menu = menu_handler.menues["cb_submenu_active_terraforming"]
    available_menu = menu_handler.menues["cb_submenu_available_terraforming"]

    cb_menu.objects["active_terraforming_bg"].activate()
    cb_menu.objects["active_terraforming_title"].activate()
    cb_menu.objects["available_terraforming_bg"].activate()
    cb_menu.objects["available_terraforming_title"].activate()

    ACTIVE_PROJECT_BASE_POS = (10, 40)  # relative to cb_menu's pos
    BG_SIZE = (400, 500)
    TERRAFORMINGPROJECT_ITEM_SIZE = (380, 80)
    SPACE_BETWEEN_ITEMS = 10
    SUBMENU_SIZE = (BG_SIZE[0]-20, BG_SIZE[1]-50)
    ICON_SIZE = 2 * (TERRAFORMINGPROJECT_ITEM_SIZE[1]-10,)
    ICON_X_OFFSET = 5

    cb_menu.objects["active_terraforming_bg"].change_property("pos", ACTIVE_PROJECT_BASE_POS)
    cb_menu.objects["active_terraforming_bg"].change_property("size", BG_SIZE)

    pos = (ACTIVE_PROJECT_BASE_POS[0]+BG_SIZE[0]/2, ACTIVE_PROJECT_BASE_POS[1]+17)
    cb_menu.objects["active_terraforming_title"].change_property("pos", pos)

    active_menu.pos = sum_multiple_vectors(cb_menu.pos, ACTIVE_PROJECT_BASE_POS, (10, 40))
    active_menu.size = SUBMENU_SIZE
    active_menu.calculate_hitbox()
    active_menu.objects["scroll_slidebar"].change_property("pos", (SUBMENU_SIZE[0], 0))
    active_menu.objects["scroll_slidebar"].change_property("length", SUBMENU_SIZE[1])

    AVAILABE_PROJECTS_BASE_POS = (420, 40)  # relative to cb_menu's pos
    cb_menu.objects["available_terraforming_bg"].change_property("pos", AVAILABE_PROJECTS_BASE_POS)
    cb_menu.objects["available_terraforming_bg"].change_property("size", BG_SIZE)

    pos = (AVAILABE_PROJECTS_BASE_POS[0]+BG_SIZE[0]/2, AVAILABE_PROJECTS_BASE_POS[1]+17)
    cb_menu.objects["available_terraforming_title"].change_property("pos", pos)

    available_menu.pos = sum_multiple_vectors(cb_menu.pos, AVAILABE_PROJECTS_BASE_POS, (10, 40))
    available_menu.size = (BG_SIZE[0]-20, BG_SIZE[1]-50)
    available_menu.calculate_hitbox()
    available_menu.objects["scroll_slidebar"].change_property("pos", (SUBMENU_SIZE[0], 0))
    available_menu.objects["scroll_slidebar"].change_property("length", SUBMENU_SIZE[1])

    for i, (key, project) in enumerate(PROJECTS.items()):
        base_pos = (0, i*(TERRAFORMINGPROJECT_ITEM_SIZE[1]+SPACE_BETWEEN_ITEMS))

        command_lambda = lambda menu_handler=menu_handler, project=project, font=font, cb=cb, images=images: \
            add_terraformproject(menu_handler, project, font, cb, images)

        button = Button(base_pos, 
                        enable_rect=True, 
                        rect_length=TERRAFORMINGPROJECT_ITEM_SIZE[0], 
                        rect_height=TERRAFORMINGPROJECT_ITEM_SIZE[1], 
                        rect_color=(0, 0, 0, 120),
                        rect_hover_color=(255, 255, 255, 60),
                        rect_click_color=(0, 0, 0, 60),
                        command=command_lambda)
        menu_handler.add_object("cb_submenu_available_terraforming", f"project_button_{i}", button)

        icon_image = images[f"terraform_project_icons/{project['icon']}"]
        icon_image = pygame.transform.scale(icon_image, ICON_SIZE)
        pos = sum_two_vectors(base_pos, (ICON_X_OFFSET, TERRAFORMINGPROJECT_ITEM_SIZE[1]/2))
        icon = Image(pos, icon_image, anchor="w")
        menu_handler.add_object("cb_submenu_available_terraforming", f"project_icon_{i}", icon)

        pos = sum_two_vectors(base_pos, (ICON_SIZE[0] + 3*ICON_X_OFFSET, TERRAFORMINGPROJECT_ITEM_SIZE[1]/2))
        text = Text(pos, project["name"], font, 18, anchor="w")
        menu_handler.add_object("cb_submenu_available_terraforming", f"project_text_{i}", text)

    for i, project in enumerate(cb.terraform_projects):
        base_pos = (0, i*(TERRAFORMINGPROJECT_ITEM_SIZE[1]+SPACE_BETWEEN_ITEMS))

        _init_terraforming_lambda = lambda menu_handler=menu_handler, cb=cb, font=font, images=images: \
            _init_terraforming(menu_handler, cb, font, images)

        button = Button(base_pos, 
                        enable_rect=True, 
                        rect_length=TERRAFORMINGPROJECT_ITEM_SIZE[0], 
                        rect_height=TERRAFORMINGPROJECT_ITEM_SIZE[1], 
                        rect_color=(0, 0, 0, 120),
                        rect_hover_color=(255, 255, 255, 60),
                        rect_click_color=(0, 0, 0, 60),
                        command=lambda index=i, func=_init_terraforming_lambda: cb.delete_terraformproject(index, func))
        menu_handler.add_object("cb_submenu_active_terraforming", f"project_button_{i}", button)

        icon_image = images[f"terraform_project_icons/{project.icon}"]
        icon_image = pygame.transform.scale(icon_image, ICON_SIZE)
        pos = sum_two_vectors(base_pos, (ICON_X_OFFSET, TERRAFORMINGPROJECT_ITEM_SIZE[1]/2))
        icon = Image(pos, icon_image, anchor="w")
        menu_handler.add_object("cb_submenu_active_terraforming", f"project_icon_{i}", icon)

        pos = sum_two_vectors(base_pos, (ICON_SIZE[0] + 3*ICON_X_OFFSET, TERRAFORMINGPROJECT_ITEM_SIZE[1]/2))
        text = Text(pos, project.get_info_text(), font, 16, anchor="w")
        menu_handler.add_object("cb_submenu_active_terraforming", f"project_text_{i}", text)

def _init_properties(menu_handler: MenuHandler, cb: CelestialBody, host_cb: CelestialBody, font, settings, cb_menu_size):
    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["info_bg"].activate()
    cb_menu.objects["info_bg_title"].activate()

    INFO_SIZE = [250, 500]
    cb_menu.objects["info_bg"].size = INFO_SIZE

    INFO_POS = [cb_menu_size[0]-10, 40]
    cb_menu.objects["info_bg"].pos = INFO_POS
    cb_menu.objects["info_bg_title"].pos = \
        [INFO_POS[0]-INFO_SIZE[0]/2, INFO_POS[1]+10]
    
    properties = [["Size", round_to_significant_figures(cb.size, 3)]]

    if isinstance(cb, PlanetaryBody):
        properties.extend([
            ["Orbital host", host_cb.name],
            ["SMA", f"{round_to_significant_figures(cb.sma, 3)} AU"]
        ])

        if settings["cb_menu"]["show_orbital_velocity"]:
            orbital_velocity_text = \
                round_to_significant_figures(cb.orbital_velocity/1000, 
                                             3, make_int=True)

            properties.append(["Orbital Velocity", 
                               f"{orbital_velocity_text} km/s"])

        if settings["cb_menu"]["show_orbital_period"]:
            period = orbital_vel_to_orbital_period(cb.orbital_velocity, cb.sma)
            properties.append(["Orbital Period Length", round_seconds(period)])

    if isinstance(cb, TerrestrialBody):

        properties.extend([
            ["Tidally locked", YES_NO[cb.is_tidally_locked]],
            ["Gravity", f"{cb.gravity} N"],
        ])

        # Day length is only interesting if not tidally locked.
        if not cb.is_tidally_locked:
            properties.append(["Day length", round_seconds(cb.day_length)])

    ROW_HEIGHT = 40
    for i, (name, property) in enumerate(properties):
        pos = [INFO_POS[0]-INFO_SIZE[0]+10, (i+1)*INFO_POS[1]+ROW_HEIGHT]
        text = Text(pos, name, font, 18, anchor="w")
        menu_handler.add_object("cb_menu", f"property_title_{i}", text)

        pos = [INFO_POS[0]-10, (i+1)*INFO_POS[1]+ROW_HEIGHT]
        text = Text(pos, str(property), font, 18, anchor="e")
        menu_handler.add_object("cb_menu", f"property_{i}", text)

def _init_districts(menu_handler: MenuHandler, cb, climate_images, invoke_command):
    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["districts_bg"].activate()
    cb_menu.objects["districts_title"].activate()

    OFFSET = [10, 40]
    DISTANCE_BETWEEN = 10
    SIZE = list(climate_images.values())[0].get_size()[0]

    BG_SIZE = 4*SIZE + 5*DISTANCE_BETWEEN
    cb_menu.objects["districts_bg"].change_property("pos", OFFSET)
    cb_menu.objects["districts_bg"].change_property("size", (BG_SIZE, BG_SIZE+20))

    pos = (OFFSET[0]+BG_SIZE/2, OFFSET[1]+17)
    cb_menu.objects["districts_title"].change_property("pos", pos)

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
                        rect_outline_width=2,
                        command=lambda district_id=i: invoke_command(f"set_cb_menu_mode district {district_id}"))
        menu_handler.add_object("cb_menu", f"district_button_{i}", button)

def _init_moons(menu_handler: MenuHandler, 
                font, 
                this_cb: CelestialBody, 
                cbs: list[CelestialBody],
                invoke_command):

    menu_handler.menues["cb_submenu_moons"].reset_scroll()
    menu_handler.menues["cb_submenu_moons"].activate()
    
    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["moons_bg"].activate()
    cb_menu.objects["moons_title"].activate()

    BASE_POS = [350, 40]
    SIZE = [200, 250]

    cb_menu.objects["moons_bg"].change_property("pos", BASE_POS)
    cb_menu.objects["moons_bg"].change_property("size", SIZE)

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+17)
    text = "Moons"
    if isinstance(this_cb, Star):
        text = "Planets"

    cb_menu.objects["moons_title"].change_property("pos", pos)
    cb_menu.objects["moons_title"].change_property("text", text)

    BUTTON_SIZE = (180, 40)
    SPACE_BETWEEN = 10

    added_cbs = 0
    for cb in cbs:
        if isinstance(cb, PlanetaryBody) and cb.orbital_host == this_cb.id:

            button_pos = (10, added_cbs * (BUTTON_SIZE[1] + SPACE_BETWEEN))
            
            button = Button(button_pos,
                            enable_rect=True,
                            rect_length=BUTTON_SIZE[0],
                            rect_height=BUTTON_SIZE[1],
                            rect_color=(0, 0, 0, 0),
                            rect_outline_color=(0, 0, 0, 0),
                            rect_outline_hover_color=(255, 255, 255),
                            rect_outline_click_color=(140, 140, 140),
                            command=lambda arg=f"open_cb_menu {cb.id}": invoke_command(arg))
            
            menu_handler.add_object("cb_submenu_moons", 
                                    f"cb_button_{added_cbs}", 
                                    button)

            cb_icon = cb.visual.get_surface(30)
            image = Image(sum_two_vectors(button.pos, (5, 5)), cb_icon)
            menu_handler.add_object("cb_submenu_moons", 
                                    f"cb_icon_{added_cbs}", 
                                    image)

            title_text = Text(sum_two_vectors(button.pos, (40, BUTTON_SIZE[1]/2)),
                              cb.name, font, 18, anchor="w")

            menu_handler.add_object("cb_submenu_moons", 
                                    f"cb_title_{added_cbs}", 
                                    title_text)
            
            added_cbs += 1

def _init_atmosphere(menu_handler: MenuHandler, tb: TerrestrialBody, 
                     font, menu_mode: str, images: dict[str, pygame.Surface],
                     switch_atm_mode_command: callable):

    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["atmosphere_bg"].activate()
    cb_menu.objects["atmosphere_title"].activate()
    cb_menu.objects["atmosphere_calculator_button"].activate()

    BASE_POS = (350, 300)
    SIZE = (200, 250)

    cb_menu.objects["atmosphere_bg"].change_property("pos", BASE_POS)
    cb_menu.objects["atmosphere_bg"].change_property("size", SIZE)

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+17)
    cb_menu.objects["atmosphere_title"].change_property("pos", pos)

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+SIZE[1]-10)
    cb_menu.objects["atmosphere_calculator_button"].change_property("pos", pos)

    menu_text = Text(sum_two_vectors(BASE_POS, (10, 50)),
                     "Thickness:", font, 16, anchor="w")
    menu_handler.add_object("cb_menu", "thickness_text", menu_text)

    text = str(round(tb.atmosphere.get_thickness())) + " kPa"
    menu_text = Text(sum_two_vectors(BASE_POS, (SIZE[0]-10, 50)), 
                     text, font, 16, anchor="e")
    menu_handler.add_object("cb_menu", "thickness_text_2", menu_text)

    switch_button = Button(sum_two_vectors(BASE_POS, (SIZE[0]-5, 5)), 
                           anchor="ne",
                           image=images["buttons/24x24_change.png"],
                           hover_image=images["buttons/24x24_change_hover.png"],
                           click_image=images["buttons/24x24_change_click.png"],
                           command=switch_atm_mode_command)
    menu_handler.add_object("cb_menu", "switch_atm_mode_button", switch_button)

    texts = []
    if menu_mode == "percentage":
        shares = tb.atmosphere.get_composition_shares()
        texts = [f"{round(100*share, 2)} %" for share in shares.values()]

    else:
        texts = [str(value) + " u" for value in tb.atmosphere.composition.values()]

    Y_COMPONENT_OFFSET = 80
    Y_SHARE_OFFSET = 30
    names = [GASES_NAMES[gas] for gas in tb.atmosphere.composition.keys()]

    for i, (name, text) in enumerate(zip(names, texts)):
        pos = sum_two_vectors(BASE_POS, 
                              (10, Y_SHARE_OFFSET*i+Y_COMPONENT_OFFSET))

        menu_handler.add_object("cb_menu",
                                f"atmosphere_name_text_{i}",
                                Text(pos, name, font, 16, anchor="w"))
        
        pos = sum_two_vectors(BASE_POS, 
                              (SIZE[0]-10, Y_SHARE_OFFSET*i+Y_COMPONENT_OFFSET))
        
        menu_handler.add_object("cb_menu", 
                                f"atmosphere_share_text_{i}", 
                                Text(pos, text, font, 16, anchor="e"))

def small_planet_menu(menu_handler: MenuHandler, 
                      id: str, star_system: StarSystem):
    
    cb = star_system.get_all_cbs_dict()[id]
    menu_handler.menues["small_planet_menu"].objects["title_text"] \
        .change_property("text", cb.name)

    text = f"{CELESTIAL_BODY_TYPES_NAMES[cb.type]}\n"

    if cb.type == "star":
        text += f"{cb.star_class}-class"
    else:
        host = star_system.get_all_cbs_dict()[cb.orbital_host]

        # get the index of this cb.
        child_cbs = star_system.get_child_pbs(host.id)
        index = next((index for (index, cb) in enumerate(child_cbs) 
                    if cb.id == id), None)

        type_text = "planet" if host.type == "star" else "moon"

        number_endings = ["st", "nd", "rd", "th"]
        text += f"{index+1}{number_endings[min(index, 3)]} {type_text} of {host.name}"

    menu_handler.menues["small_planet_menu"].objects["info_text"] \
        .change_property("text", text)

def atmosphere_calculator(menu_handler: MenuHandler, 
                          font: str, 
                          atmosphere_calculator: AtmosphereCalculator, 
                          tb_size: float, 
                          star_system_id: str, cb_id: str, cb_name: str):

    atm_menu = menu_handler.menues["atmosphere_calculator"]
    atm_menu.objects["title_text"].change_property("text", f"Atmosphere Calculator - {cb_name}")

    command = lambda: atmosphere_calculator.update_menu(menu_handler, tb_size, star_system_id, cb_id)
    atm_menu.objects["thickness_input"].change_property("command", command)

    COLUMN_1_BASE_POS = (10, 140)
    COLUMN_2_BASE_POS = (150, 140)
    COLUMN_3_BASE_POS = (290, 140)

    INPUT_SIZE = (50, 25)
    ROW_HEIGHT = 30

    for i, gas in enumerate(GASES):
        # COLUMN 1
        gas_text = Text(sum_two_vectors(COLUMN_1_BASE_POS, (0, ROW_HEIGHT*i)),
                        GASES_NAMES[gas], font, 16, anchor="w")
        menu_handler.add_object("atmosphere_calculator", 
                                f"gas_text_{gas}", gas_text)

        # COLUMN 2
        input_bg = Shape(sum_two_vectors(COLUMN_2_BASE_POS, (0, ROW_HEIGHT*i)), 
                         INPUT_SIZE, (39, 48, 148), "rect", anchor="w",
                         outline_width=1, outline_color=(0, 0, 0))
        menu_handler.add_object("atmosphere_calculator", 
                                f"input_bg_{gas}", 
                                input_bg)

        percentage_input = TextInput(sum_two_vectors(COLUMN_2_BASE_POS, (5, ROW_HEIGHT*i)), 
                                     INPUT_SIZE[0]-10, font, 16, anchor="w",
                                     command=command,
                                     validity_check=text_input.validity_check.POSITIVE_NUMBERS_DOTS_COMMAS)
        menu_handler.add_object("atmosphere_calculator", 
                                f"percentage_input_{gas}", 
                                percentage_input)

        percentage_text = Text(sum_two_vectors(COLUMN_2_BASE_POS, (60, ROW_HEIGHT*i)),
                                 "%", font, 18, anchor="w")
        menu_handler.add_object("atmosphere_calculator",
                                f"percentage_text_{gas}",
                                percentage_text)

        # COLUMN 3
        units_text = Text(sum_two_vectors(COLUMN_3_BASE_POS, (0, ROW_HEIGHT*i)),
                          "0 u", font, 16, anchor="w")
        menu_handler.add_object("atmosphere_calculator",
                                f"units_text_{gas}", units_text)

    atmosphere_calculator.load_data(star_system_id, cb_id, menu_handler)
    atmosphere_calculator.update_menu(menu_handler, tb_size, star_system_id, cb_id)

def add_terraformproject(menu_handler: MenuHandler, 
                         project: dict, font: str, cb: CelestialBody, images):
    menu = menu_handler.menues["add_terraformproject"]
    menu.activate()
    command = lambda: add_terraformproject(menu_handler, project, font, cb, images)
    menu.objects["amount_input"].change_property("command", command)
    menu.objects["title_text"].change_property("text", f"{project['name']} - {cb.name}")

    object_ids = ["gas_text", "gas_dropdown", "info_text"]
    menu_handler.delete_multiple_objects("add_terraformproject", object_ids, [])

    pos = [10, 100]

    if project["window"] == "change_gas":
        gas_text = Text(pos[:], "Gas:", font, 18, anchor="w")
        menu_handler.add_object("add_terraformproject", "gas_text", gas_text)

        gas_dropdown = Dropdown((pos[0]+70, pos[1]-15), (200, 30), font, 16, 
                                list(GASES_NAMES.values()), 
                                list(GASES_NAMES.values())[0],
                                anchor="nw",
                                box_bg_color=(39, 48, 148),
                                box_bg_hover_color=(64, 74, 204),
                                box_bg_click_color=(30, 35, 140),
                                box_outline_color=(255, 255, 255),
                                box_outline_hover_color=(255, 255, 255),
                                box_outline_click_color=(255, 255, 255))
        menu_handler.add_object("add_terraformproject", "gas_dropdown", gas_dropdown)

        pos[1] += 50

    unit_text = ""
    if project["window"] == "change_gas":
        unit_text = "units"
    elif project["window"] == "change_property":
        unit_text = PROPERTY_UNITS[project["property"]]
    
    menu.objects["unit_text"].change_property("text", unit_text)

    amount_input: TextInput = menu.objects["amount_input"]
    amount_input_text = amount_input.get_text()
    if amount_input_text == "" or not amount_input.get_validity():
        menu.objects["add_button"].change_property("command", None)
        return

    weekly_amount = 1
    total_amount = float(amount_input_text.replace(",", "."))
    total_time = total_amount / weekly_amount

    info_texts = []

    info_texts.append(f"Total amount: {total_amount} {unit_text}")
    info_texts.append(f"Amount per week: {weekly_amount} {unit_text}/week")
    info_texts.append(f"Total time: {total_time} weeks")
    text_sum = "\n".join(info_texts)

    info_text = Text(pos, text_sum, font, 16, anchor="nw")
    menu_handler.add_object("add_terraformproject", "info_text", info_text)
    
    _init_terraforming_lambda = lambda menu_handler=menu_handler, cb=cb, font=font, images=images: \
        _init_terraforming(menu_handler, cb, font, images)

    add_terraformproject_lambda = lambda menu_handler=menu_handler, project=project, \
        weekly_amount=weekly_amount, total_time=total_time, _init_terraforming_lambda=_init_terraforming_lambda: \
        cb.add_terraformproject(menu_handler, project, weekly_amount, total_time, _init_terraforming_lambda)

    if project["window"] == "change_gas":  # override add_terraformproject_lambda
        reverse_dict = {value: key for key, value in GASES_NAMES.items()}
        gas = reverse_dict[gas_dropdown.get_selected_option()]
        
        add_terraformproject_lambda = lambda menu_handler=menu_handler, project=project, \
            weekly_amount=weekly_amount, total_time=total_time, _init_terraforming_lambda=_init_terraforming_lambda, gas=gas: \
            cb.add_terraformproject(menu_handler, project, weekly_amount, total_time, _init_terraforming_lambda, gas)

    menu.objects["add_button"].change_property("command", add_terraformproject_lambda)

def view_species_menu(menu_handler: MenuHandler, species: Species, font: str):
    menu = menu_handler.menues["view_species_menu"]
    menu.objects["title_text"].change_property("text", f"Species - {species.name}")

    species_image = pygame.transform.scale(species.portrait, (128, 128))
    species_menu_image = Image((10, 40), species_image)
    menu_handler.add_object("view_species_menu", "species_image", species_menu_image)

    ROW_HEIGHT = 30
    COLUMN_1_BASE_POS = (150, 40)
    COLUMN_2_BASE_POS = (300, 40)

    HABITAT_PREFERENCES_TEXTS = [
        species.habitat_preferences["main_fluid"].capitalize(),
        species.habitat_preferences["temperature"].capitalize(),
        f"{round(species.habitat_preferences['atmospheric_pressure'])} kPa"
    ]

    GASES_REQUIREMENTS_TEXTS_1 = []
    GASES_REQUIREMENTS_TEXTS_2 = []
    for gas, amount in species.habitat_preferences["atmospheric_composition"].items():
        min_or_max, gas = gas.split("_")
        GASES_REQUIREMENTS_TEXTS_1.append(f"{min_or_max.capitalize()} {GASES_NAMES[gas]}")
        GASES_REQUIREMENTS_TEXTS_2.append(f"{round_to_significant_figures(100 * amount, 3, make_int=True)} %")

    column_1_texts = ["Name", 
                      "Environment", 
                      *CHARACTERISTICS_NAMES.values(), 
                      *HABITAT_PREFERENCES_NAMES.values(),
                      *GASES_REQUIREMENTS_TEXTS_1]

    column_2_texts = [species.name, 
                      ENVIRONMENTS_NAMES[species.environment], 
                      *[str(c) for c in species.characteristics.values()],
                      *HABITAT_PREFERENCES_TEXTS,
                      *GASES_REQUIREMENTS_TEXTS_2]

    for i, (text1, text2) in enumerate(zip(column_1_texts, column_2_texts)):
        pos = sum_two_vectors(COLUMN_1_BASE_POS, (0, ROW_HEIGHT*i))
        text = Text(pos, f"{text1}:", font, 18, anchor="nw")
        menu_handler.add_object("view_species_menu", f"row1_text_{i}", text)

        pos = sum_two_vectors(COLUMN_2_BASE_POS, (0, ROW_HEIGHT*i))
        text = Text(pos, text2, font, 18, anchor="nw")
        menu_handler.add_object("view_species_menu", f"row_2_text_{i}", text)

def _init_population(menu_handler: MenuHandler, tb: TerrestrialBody, font: str, species: dict[str, Species], in_district=False, district_id=0):
    menu = menu_handler.menues["cb_menu"]
    menu.objects["population_bg"].activate()
    menu.objects["population_title"].activate()

    BASE_POS = [350, 40]
    SIZE = [200, 250]

    menu.objects["population_bg"].change_property("pos", BASE_POS)
    menu.objects["population_bg"].change_property("size", SIZE)

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+17)
    menu.objects["population_title"].change_property("pos", pos)

    ROW_HEIGHT = 30
    COLUMN_1_BASE_POS = (10, 50)
    COLUMN_2_BASE_POS = (190, 50)

    if not in_district:
        population_dict = tb.population.get_total_population_dict()
        column1_texts = ["Total:", *[f"{species[species_id].name}:" for species_id in population_dict.keys()]]
        column2_texts = [round_and_add_suffix(tb.population.get_total_population(), 3),
                        *[round_and_add_suffix(p, 3) for p in population_dict.values()]]

    else:
        population_dict = tb.population.sub_populations[district_id].get_population_dict()
        column1_texts = ["Total:", *[f"{species[species_id].name}:" for species_id in population_dict.keys()]]
        column2_texts = [round_and_add_suffix(tb.population.sub_populations[district_id].get_total_population(), 3),
                        *[round_and_add_suffix(p, 3) for p in population_dict.values()]]

    for i, (text1, text2) in enumerate(zip(column1_texts, column2_texts)):
        text_ = Text(sum_multiple_vectors(BASE_POS, COLUMN_1_BASE_POS, (0, i*ROW_HEIGHT)),
                     text1, font, 16, anchor="w")
        menu_handler.add_object("cb_menu", f"population_text1_{i}", text_)

        text_ = Text(sum_multiple_vectors(BASE_POS, COLUMN_2_BASE_POS, (0, i*ROW_HEIGHT)),
                     text2, font, 16, anchor="e")
        menu_handler.add_object("cb_menu", f"population_text2_{i}", text_)

def _init_habitabilities(menu_handler: MenuHandler, tb: TerrestrialBody, font: str, species: dict[str, Species], player_civ: Civ, in_district=False, district_id=0):
    menu = menu_handler.menues["cb_menu"]
    menu.objects["habitability_bg"].activate()
    menu.objects["habitability_title"].activate()

    BASE_POS = [560, 40]
    SIZE = [200, 250]

    menu.objects["habitability_bg"].change_property("pos", BASE_POS)
    menu.objects["habitability_bg"].change_property("size", SIZE)

    pos = (BASE_POS[0]+SIZE[0]/2, BASE_POS[1]+17)
    menu.objects["habitability_title"].change_property("pos", pos)

    if not in_district:
        menu.objects["habitability_title"].change_property("text", "Average Habitabilities")
        population_dict = tb.population.get_total_population_dict()

        average_habitabilities = [player_civ.get_average_species_tb_habitability(tb.star_system_id, tb.id, species_id) for species_id in population_dict.keys()]
        total_average = player_civ.get_total_average_species_tb_habitability(tb.star_system_id, tb.id)

        column1_texts = ["Total Average:", *[f"{species[species_id].name}:" for species_id in population_dict.keys()]]
        column2_texts = [total_average, *average_habitabilities]

    else:
        menu.objects["habitability_title"].change_property("text", "Habitabilities")
        population_dict = tb.population.sub_populations[district_id].get_population_dict()

        habitabilities = [player_civ.get_species_district_habitability(tb.star_system_id, tb.id, district_id, species_id) for species_id in population_dict.keys()]
        average = player_civ.get_average_species_district_habitability(tb.star_system_id, tb.id, district_id)

        column1_texts = ["Average:", *[f"{species[species_id].name}:" for species_id in population_dict.keys()]]
        column2_texts = [average, *habitabilities]

    column2_texts = [str(round(100*h, 1))+"%" for h in column2_texts]

    ROW_HEIGHT = 30
    COLUMN_1_BASE_POS = (10, 50)
    COLUMN_2_BASE_POS = (190, 50)

    for i, (text1, text2) in enumerate(zip(column1_texts, column2_texts)):
        text_ = Text(sum_multiple_vectors(BASE_POS, COLUMN_1_BASE_POS, (0, i*ROW_HEIGHT)),
                     text1, font, 16, anchor="w")
        menu_handler.add_object("cb_menu", f"habitability_text1_{i}", text_)

        text_ = Text(sum_multiple_vectors(BASE_POS, COLUMN_2_BASE_POS, (0, i*ROW_HEIGHT)),
                     text2, font, 16, anchor="e")
        menu_handler.add_object("cb_menu", f"habitability_text2_{i}", text_)

def top_bar(menu_handler: MenuHandler, font: str, frame_width: int):
    menu = menu_handler.menues["top_bar"]
    HEIGHT = 30

    menu.change_property("size", [frame_width-200, HEIGHT])

    menu.objects["unity_text"].change_property("text", "Unity: 100%")
    menu.objects["unity_text"].change_property("pos", [3, HEIGHT/2])

def _init_buildings(menu_handler: MenuHandler, font: str, tb: TerrestrialBody, district_id: int, building_images: dict[str, pygame.Surface]):
    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["buildings_bg"].activate()
    cb_menu.objects["buildings_title"].activate()

    OFFSET = [10, 40]
    DISTANCE_BETWEEN = 10
    SIZE = 70

    BG_SIZE = 4*SIZE + 5*DISTANCE_BETWEEN
    cb_menu.objects["buildings_bg"].change_property("pos", OFFSET)
    cb_menu.objects["buildings_bg"].change_property("size", (BG_SIZE, BG_SIZE+20))

    pos = (OFFSET[0]+BG_SIZE/2, OFFSET[1]+17)
    cb_menu.objects["buildings_title"].change_property("pos", pos)

    OFFSET = sum_two_vectors(OFFSET, (10, 30))

    for i, building in enumerate(tb.districts[district_id].buildings):
        x, y = i % 4, math.floor(i / 4)
        pos = sum_two_vectors(OFFSET, ((SIZE+DISTANCE_BETWEEN)*x,
                                       (SIZE+DISTANCE_BETWEEN)*y))

        image = building_images[building.image_id]
        menu_image = Image(pos, image)
        menu_handler.add_object("cb_menu", f"building_picture_{i}", menu_image)

        button = Button(pos,
                        enable_rect=True,
                        rect_length=SIZE,
                        rect_height=SIZE,
                        rect_color=(0, 0, 0, 0),
                        rect_outline_color=(0, 0, 0),
                        rect_outline_hover_color=(255, 255, 255),
                        rect_outline_click_color=(140, 140, 140),
                        rect_outline_width=2)
        menu_handler.add_object("cb_menu", f"building_button_{i}", button)

def _init_all_buildings(menu_handler: MenuHandler, tb: TerrestrialBody, building_images, font):
    cb_menu = menu_handler.menues["cb_menu"]

    cb_menu.objects["all_buildings_bg"].activate()
    cb_menu.objects["all_buildings_title"].activate()

    CB_MENU_OFFSET = [10, 40]
    DISTANCE_BETWEEN = 10
    BUILDING_ICON_SIZE = 70

    BG_SIZE = (330, 510)
    cb_menu.objects["all_buildings_bg"].change_property("pos", CB_MENU_OFFSET)
    cb_menu.objects["all_buildings_bg"].change_property("size", BG_SIZE)

    pos = (CB_MENU_OFFSET[0]+BG_SIZE[0]/2, CB_MENU_OFFSET[1]+17)
    cb_menu.objects["all_buildings_title"].change_property("pos", pos)

    object_ids_startswith = [
        "icon_image_",
        "text_"
    ]

    menu_handler.delete_multiple_objects("cb_submenu_all_buildings", [], object_ids_startswith)
    all_buildings_menu = menu_handler.menues["cb_submenu_all_buildings"]
    all_buildings_menu.activate()

    all_buildings_menu_size = sum_two_vectors(BG_SIZE, (-20, -50))

    all_buildings_menu.change_property("pos", sum_multiple_vectors(cb_menu.pos, CB_MENU_OFFSET, (10, 40)))
    all_buildings_menu.change_property("size", all_buildings_menu_size)
    all_buildings_menu.calculate_hitbox()
    all_buildings_menu.objects["scroll_slidebar"].change_property("pos", (all_buildings_menu_size[0], 0))
    all_buildings_menu.objects["scroll_slidebar"].change_property("length", all_buildings_menu_size[1])

    all_buildings_dict = tb.get_all_buildings_dict()
    for i, ((building_template_id, building_level), (amount, base_name)) in enumerate(all_buildings_dict.items()):
        icon_image = Image((0, i*(BUILDING_ICON_SIZE+DISTANCE_BETWEEN)),
                           building_images[building_template_id])
        menu_handler.add_object("cb_submenu_all_buildings", f"icon_image_{i}", icon_image)

        building_text = Text((10+BUILDING_ICON_SIZE, i*(BUILDING_ICON_SIZE+DISTANCE_BETWEEN)+BUILDING_ICON_SIZE/2),
                             f"{amount}x {base_name}, level {building_level}",
                             font,
                             18,
                             anchor="w")
        menu_handler.add_object("cb_submenu_all_buildings", f"text_{i}", building_text)
