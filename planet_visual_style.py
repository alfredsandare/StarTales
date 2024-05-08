class PlanetVisualStyle:
    def __init__(self, color_limits, cloud_color):
        self.color_limits = color_limits
        self.cloud_color = cloud_color


EARTHLY = [
    {
        50: (0, 0, 255),
        65: (0, 255, 0),
        100: (150, 150, 150)
    },
    (255, 255, 255)
]
        
MESA = [
    {
        50: (255, 0, 0),
        65: (255, 255, 0),
        100: (150, 150, 150)
    },
    (255, 255, 255)
]