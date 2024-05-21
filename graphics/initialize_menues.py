# module for adding content to menues
# function names here are only the name of the menu

from PhoenixGUI.util import sum_two_vectors
from PhoenixGUI import *
from physics.star import Star
from physics.terrestrial_body import TerrestrialBody

YES_NO = {
    True: "Yes",
    False: "No"
}

def outliner(menu_handler, cbs, star_id, show_moons_in_outliner, font, invoke_command):
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
                          cb.name, 
                          font, 
                          18,
                          anchor="nw")
        
        menu_handler.add_object("outliner", 
                                f"cb_title_{added_planets}", 
                                title_text)

        types = {Star: "Star", TerrestrialBody: "Terrestrial World"}
        type_content_text = types[type(cb)]

        cb_type_text = Text(sum_two_vectors(button.pos, (40, 35)), 
                            type_content_text, 
                            font, 
                            14,
                            anchor="sw")
        
        menu_handler.add_object("outliner", 
                                f"cb_type_{added_planets}", 
                                cb_type_text)

        added_planets += 1

def cb_menu(menu_handler, cb, host_cb, font):
    menu_handler.menues["cb_menu"].objects["title_text"].text = cb.name

    SIZE = [900, 600]

    menu_handler.menues["cb_menu"].size = SIZE
    menu_handler.menues["cb_menu"].objects["top_bar"].size = [SIZE[0], 30]

    INFO_SIZE = [250, 500]
    menu_handler.menues["cb_menu"].objects["info_bg"].size = INFO_SIZE

    INFO_POS = [SIZE[0]-10, 40]
    menu_handler.menues["cb_menu"].objects["info_bg"].pos = INFO_POS
    menu_handler.menues["cb_menu"].objects["info_bg_title"].pos = \
        [INFO_POS[0]-INFO_SIZE[0]/2, INFO_POS[1]+10]
    
    properties = [["Size", cb.size]]
    if isinstance(cb, TerrestrialBody):
        properties.extend([
            ["Orbital host", host_cb.name],
            ["Tidally locked", YES_NO[cb.is_tidally_locked]],
            ["Orbital Velocity", cb.orbital_velocity],
            ["Day length", cb.day_length],
            ["Gravity", cb.gravity],
            ["SMA", cb.sma]
        ])

    ROW_HEIGHT = 40
    for i, (name, property) in enumerate(properties):
        pos = [INFO_POS[0]-INFO_SIZE[0]+10, (i+1)*INFO_POS[1]+ROW_HEIGHT]
        text = Text(pos, name, font, 18, anchor="w")
        menu_handler.add_object("cb_menu", f"property_title_{i}", text)

        pos = [INFO_POS[0]-10, (i+1)*INFO_POS[1]+ROW_HEIGHT]
        text = Text(pos, property, font, 18, anchor="e")
        menu_handler.add_object("cb_menu", f"property_{i}", text)