from PhoenixGUI import MenuHandler, TextInput, Menu
from physics.atmosphere import GASES
from util import round_to_significant_figures


class AtmosphereCalculator:
    def __init__(self):
        self.saved_data = {}

    def update_menu(self, menu_handler: MenuHandler, tb_size, star_system_id, cb_id):
        menu = menu_handler.menues["atmosphere_calculator"]
        self.save_data(star_system_id, cb_id, menu_handler)

        percentages = {}
        for gas in GASES:
            input_obj: TextInput = menu.objects[f"percentage_input_{gas}"]
            if input_obj.get_validity() and input_obj.get_text() != "":
                percentages[gas] = float(input_obj.get_text())

        thickness_text = menu.objects["thickness_input"].get_text()
        if thickness_text == "":
            self.update_info_text(menu, "Thickness not given.")
            return

        if not percentages:  # No given percentages
            self.update_info_text(menu, "No percentages given.")
            return

        if sum(percentages.values()) != 100:
            self.update_info_text(menu, f"Percentages must sum up to 100, not {sum(percentages.values())}.")
            return

        thickness = float(thickness_text.replace(",", "."))
        composition = self.calculate_composition(thickness, tb_size, percentages)

        for gas, value in composition.items():
            rounded = round_to_significant_figures(value, 3, make_int=True)
            menu.objects[f"units_text_{gas}"].change_property("text", f"{rounded} u")

        self.update_info_text(menu, "")

    def calculate_composition(self, thickness, tb_size, percentages):
        composition_sum = tb_size**2 * thickness

        composition = {gas: int(value/100 * composition_sum) 
                       for gas, value in percentages.items()}

        for gas in GASES:
            if gas not in composition:
                composition[gas] = 0

        return composition

    def update_info_text(self, menu: Menu, text: str):
        menu.objects["info_text"].change_property("text", text)

    def save_data(self, star_system_id, cb_id, menu_handler: MenuHandler):
        menu = menu_handler.menues["atmosphere_calculator"]
        data = (menu.objects["thickness_input"].get_text(), 
                {gas: menu.objects[f"percentage_input_{gas}"].get_text() 
                 for gas in GASES})

        self.saved_data[(star_system_id, cb_id)] = data

    def load_data(self, star_system_id, cb_id, menu_handler: MenuHandler):
        if (star_system_id, cb_id) not in self.saved_data:
            self.reset_fields(menu_handler)
            return

        menu = menu_handler.menues["atmosphere_calculator"]
        thickness, percentages = self.saved_data[(star_system_id, cb_id)]

        menu.objects["thickness_input"].set_text(thickness)
        for gas, value in percentages.items():
            menu.objects[f"percentage_input_{gas}"].set_text(value)

    def reset_fields(self, menu_handler: MenuHandler):
        menu = menu_handler.menues["atmosphere_calculator"]
        menu.objects["thickness_input"].set_text("")
        for gas in GASES:
            menu.objects[f"percentage_input_{gas}"].set_text("")
            menu.objects[f"units_text_{gas}"].change_property("text", "0 u")

        self.update_info_text(menu, "")
