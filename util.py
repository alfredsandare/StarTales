import math
from PIL import Image


def multiply_vector(vector, factor):
    return [factor*vector[0], factor*vector[1]]

def set_value_in_boundaries(value, lower_boundary=None, upper_boundary=None):
    if lower_boundary is not None and value < lower_boundary:
        return lower_boundary
    
    if upper_boundary is not None and value > upper_boundary:
        return upper_boundary
    
    return value

def round_to_significant_figures(num: float, 
                                 significant_figures: int, 
                                 make_int: bool = False, 
                                 make_zero: bool = False) -> float:
    
    if num == 0:
        return 0
    
    is_negative = False
    if num < 0:
        num *= -1
        is_negative = True

    output = 0
    if num >= 1:
        output = round(num, significant_figures-len(str(int(num))))
    else:
        output = round(num, significant_figures+len(str(int(1/num)))-1)

    if round(output) == output and make_int: #so that 436.0 becomes 436
        output = int(output)

    if is_negative:
        output *= -1
        
    if round(output) == 0 and make_zero:
        output = 0

    return output

def round_seconds(seconds: float) -> str:
    if seconds < 300:
        return f"{round(seconds)} s"
    
    minutes = seconds/60
    if minutes < 60:
        return f"{round(minutes)} m"
    
    hours = minutes/60
    if hours < 48:
        return f"{round_to_significant_figures(hours, 2, make_int=True)} h"
    
    days = hours/24
    if days < 28:
        return f"{round(days)} d"
    
    weeks = days / 7
    if weeks < 52:
        return f"{round(weeks)} weeks"
    
    years = weeks / 7.02403846
    return f"{round(years, 1)} years"

def convert_erv_to_day_length(erv, radius):
    # erv in m/s
    # radius in km

    radius_in_m = radius * 1000

    circumference = 2 * radius_in_m * math.pi

    return circumference / erv

def run_convert_erv_to_day_length_program():
    print("Convert equatorial rotation velocity to day length")
    erv = float(input("Enter equatorial rotation velocity [m/s]: "))
    radius = float(input("Enter radius [km]: "))
    print(f"Day length is {convert_erv_to_day_length(erv, radius)} s")

def is_valid_image(file_name):
    try:
        with Image.open(file_name) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False
    
def calculate_total_atmosphere_units(thickness, radius):
    # thickness in kPa
    # radius in km

    cb_size = radius / 400

    return thickness * cb_size**2

def run_calculate_total_atmosphere_units_program():
    print("Calculate total amount of atmosphere units from atmospheric pressure and radius")
    thickness = float(input("Enter atmospheric pressure [kPa]: "))
    radius = float(input("Enter radius [km]: "))
    atmosphere_units = calculate_total_atmosphere_units(thickness, radius)
    print(f"Total amount of atmosphere units: {atmosphere_units}")

if __name__ == "__main__":
    # run_convert_erv_to_day_length_program()
    run_calculate_total_atmosphere_units_program()
