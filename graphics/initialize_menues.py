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
from physics.terraformprojects import PROJECTS
from physics.terrestrial_body import TerrestrialBody
from util import orbital_vel_to_orbital_period, round_seconds, round_to_significant_figures

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
                        command=(invoke_command, [f"open_cb_menu {cb.id}"], {}))
        
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
            invoke_command,
            settings,
            menu_settings,
            images: dict[str, pygame.Surface],
            switch_atm_mode_command):

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
        "districts_bg",
        "districts_title",
        "active_terraforming_bg",
        "active_terraforming_title",
        "available_terraforming_bg",
        "available_terraforming_title"
    ]

    for object_id in to_deactivate:
        cb_menu.objects[object_id].deactivate()

    if isinstance(cb, TerrestrialBody):
        _init_districts(menu_handler, cb, climate_images)

    if isinstance(cb, TerrestrialBody) and menu_settings["cb_menu_mode"] == "overview":
        _init_atmosphere(menu_handler, cb, font, menu_settings["atmosphere_menu_mode"], 
                         images, switch_atm_mode_command)

    if menu_settings["cb_menu_mode"] == "overview":
        _init_properties(menu_handler, cb, host_cb, font, settings, SIZE)
        _init_moons(menu_handler, font, cb, cbs, invoke_command)

    elif menu_settings["cb_menu_mode"] == "terraforming":
        _init_terraforming(menu_handler, cb, font, settings, images)

def _init_terraforming(menu_handler: MenuHandler, cb: CelestialBody, font, settings, images):
    menu_handler.menues["cb_submenu_active_terraforming"].activate()
    menu_handler.menues["cb_submenu_available_terraforming"].activate()

    cb_menu = menu_handler.menues["cb_menu"]
    active_menu = menu_handler.menues["cb_submenu_active_terraforming"]
    available_menu = menu_handler.menues["cb_submenu_available_terraforming"]

    cb_menu.objects["active_terraforming_bg"].activate()
    cb_menu.objects["active_terraforming_title"].activate()
    cb_menu.objects["available_terraforming_bg"].activate()
    cb_menu.objects["available_terraforming_title"].activate()

    ACTIVE_PROJECT_BASE_POS = (350, 40)  # relative to cb_menu's pos
    BG_SIZE = (250, 500)
    TERRAFORMINGPROJECT_ITEM_SIZE = (230, 50)
    SPACE_BETWEEN_ITEMS = 10
    SUBMENU_SIZE = (BG_SIZE[0]-20, BG_SIZE[1]-50)

    cb_menu.objects["active_terraforming_bg"].change_property("pos", ACTIVE_PROJECT_BASE_POS)
    cb_menu.objects["active_terraforming_bg"].change_property("size", BG_SIZE)

    pos = (ACTIVE_PROJECT_BASE_POS[0]+BG_SIZE[0]/2, ACTIVE_PROJECT_BASE_POS[1]+17)
    cb_menu.objects["active_terraforming_title"].change_property("pos", pos)

    active_menu.pos = sum_multiple_vectors(cb_menu.pos, ACTIVE_PROJECT_BASE_POS, (10, 40))
    active_menu.size = SUBMENU_SIZE
    active_menu.calculate_hitbox()
    active_menu.objects["scroll_slidebar"].change_property("pos", (SUBMENU_SIZE[0], 0))
    active_menu.objects["scroll_slidebar"].change_property("length", SUBMENU_SIZE[1])

    AVAILABE_PROJECTS_BASE_POS = (610, 40)  # relative to cb_menu's pos
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

        button = Button(base_pos, 
                        enable_rect=True, 
                        rect_length=TERRAFORMINGPROJECT_ITEM_SIZE[0], 
                        rect_height=TERRAFORMINGPROJECT_ITEM_SIZE[1], 
                        rect_color=(0, 0, 0, 120),
                        rect_hover_color=(255, 255, 255, 60),
                        rect_click_color=(0, 0, 0, 60),
                        command=(add_terraformproject, [menu_handler, project, font, cb], {}))
        menu_handler.add_object("cb_submenu_available_terraforming", f"project_button_{i}", button)

        icon_image = images[f"terraform_project_icons/{project['icon']}"]
        icon_image = pygame.transform.scale(icon_image, (50, 50))
        icon = Image(base_pos, icon_image, anchor="nw")
        menu_handler.add_object("cb_submenu_available_terraforming", f"project_icon_{i}", icon)

        text = Text(sum_two_vectors(base_pos, (60, TERRAFORMINGPROJECT_ITEM_SIZE[1]/2)), project["name"], font, 16, anchor="w")
        menu_handler.add_object("cb_submenu_available_terraforming", f"project_text_{i}", text)

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

def _init_districts(menu_handler: MenuHandler, cb, climate_images):
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
                        rect_outline_width=2)
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
                            command=(invoke_command, [f"open_cb_menu {cb.id}"], {}))
            
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

    text = str(round(tb.atmosphere.get_thickness(tb.size))) + " kPa"
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

    command = (atmosphere_calculator.update_menu, [menu_handler, tb_size, star_system_id, cb_id], {})
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
                         project: dict, font: str, cb: CelestialBody):
    menu = menu_handler.menues["add_terraformproject"]
    menu.activate()
    menu.objects["amount_input"].change_property("command", (add_terraformproject, [menu_handler, project, font, cb], {}))
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
    elif project["window"] == "change_property" and project["property"] == "day_length":
        unit_text = "hours"
    elif project["window"] == "change_property" and project["property"] == "orbital_velocity":
        unit_text = "km/s"
    elif project["window"] == "change_property" and project["property"] == "sma":
        unit_text = "AU"
    
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

    if project["window"] == "change_gas":
        reverse_dict = {value: key for key, value in GASES_NAMES.items()}
        gas = reverse_dict[gas_dropdown.get_selected_option()]
        menu.objects["add_button"].change_property("command", (cb.add_terraformproject, [menu, project, weekly_amount, total_time, gas], {}))
    else:
        menu.objects["add_button"].change_property("command", (cb.add_terraformproject, [menu, project, weekly_amount, total_time], {}))
