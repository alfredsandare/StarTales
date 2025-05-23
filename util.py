import math
from PIL import Image

from data.consts import METERS_PER_AU, TEMPERATURES_ADJECTIVES


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
    
    weeks = days / 7.02403846
    if weeks < 52:
        return f"{round(weeks)} weeks"
    
    years = weeks / 52
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

    tb_size = radius / 400

    return thickness * tb_size**2

def run_calculate_total_atmosphere_units_program():
    print("Calculate total amount of atmosphere units from atmospheric pressure and radius")
    thickness = float(input("Enter atmospheric pressure [kPa]: "))
    radius = float(input("Enter radius [km]: "))
    atmosphere_units = calculate_total_atmosphere_units(thickness, radius)
    print(f"Total amount of atmosphere units: {atmosphere_units}")

def convert_weeks_to_years(weeks, format="time"):
    # converts weeks to years and weeks
    done = False
    years = 0
    while not done:
        if weeks > (51 if format == "time" else 52):
            weeks -= 52
            years += 1
        else:
            done = True

    if format == "time":
        if years == 0:
            return f'{weeks} weeks'
        elif weeks == 0:
            return f'{years} years'
        else:
            return f'{years} years and {weeks} weeks'

    elif format == "date":
        return f"week {weeks}, {years}"
    
def check_rect_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
    # This function works by checking if one rectangle is to the left, right, above, or below the other. 
    # If none of these conditions are true, then the rectangles must overlap.
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

def orbital_vel_to_orbital_period(orbital_vel: float, sma: float) -> float:
    ''' orbital vel in m/s, sma in AU '''
    sma_in_m = sma * METERS_PER_AU
    orbit_length = 2 * math.pi * sma_in_m
    time_in_s = orbit_length / orbital_vel
    return time_in_s

def orbital_period_to_orbital_vel(period: float, sma: float) -> float:
    ''' Period in days, sma in AU'''
    period_in_s = period * 86_400
    sma_in_m = sma * METERS_PER_AU
    orbit_length = 2 * math.pi * sma_in_m
    return orbit_length / period_in_s

def get_path_from_file_name(file_name: str) -> str:
    return file_name[:file_name.find("StarTales") + 10]

def round_and_add_suffix(num, significant_figures, include_space=True, make_int=False, threshold=10000):
    prefixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc', 
                'Ud', 'Dd', 'Td', 'Qad', 'Qid', 'Sxd', 'Spd', 'Ocd', 'Nod', 'Vg', 'Uvg']

    if num == 0:
        return '0'

    if -threshold < num < threshold:
        return str(num)

    for i in range(len(prefixes)):
        divided = num/10**(3*i)
        if -1000 <= divided < 1000 or i == len(prefixes)-1:
            output = float(round_to_significant_figures(divided, significant_figures, make_int=make_int))
            if round(output) == output: #so that 436.0 becomes 436
                output = int(output)
            return str(output) + (' ' if include_space else '') + prefixes[i]

def get_temperature_adjective(temperature):
    for limit, adjective in TEMPERATURES_ADJECTIVES.items():
        if temperature >= limit:
            return adjective
    return ""

if __name__ == "__main__":
    # run_convert_erv_to_day_length_program()
    # run_calculate_total_atmosphere_units_program()
    print(orbital_period_to_orbital_vel(11.18, 0.0485))
