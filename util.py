def multiply_vector(vector, factor):
    return [factor*vector[0], factor*vector[1]]

def set_value_in_boundaries(value, lower_boundary=None, upper_boundary=None):
    if lower_boundary is not None and value < lower_boundary:
        return lower_boundary
    
    if upper_boundary is not None and value > upper_boundary:
        return upper_boundary
    
    return value