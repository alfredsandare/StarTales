from physics.climates import Climate


class District:
    def __init__(self, climate: Climate):
        self.climate = climate

    def __repr__(self):
        return f"District: {self.climate.name}"