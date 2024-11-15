import math
from graphics.celestial_body_visual import CelestialBodyVisual
from physics.celestial_body import CelestialBody
from data.consts import METERS_PER_AU, SECONDS_PER_WEEK


class PlanetaryBody(CelestialBody):
    def __init__(self,
                 visual: CelestialBodyVisual,
                 size: float,
                 name: str,
                 id: str,
                 star_system_id: str,
                 orbital_host: str,
                 is_tidally_locked: bool,
                 orbital_velocity: float,  # m/s
                 sma: float,
                 owner: str):

        super().__init__(visual, size, name, id, star_system_id, owner)
        self.orbital_host = orbital_host
        self.is_tidally_locked = is_tidally_locked
        self.orbital_velocity = orbital_velocity
        self.sma = sma

        self.orbit_progress = 0  # 0 - 1.
        # orbit_progress only changes every in-game time tick,
        # but visual_orbit_progress lags behind smoothly.
        self.visual_orbit_progress = 0  # 0 - 1.

    def _get_progress_per_week(self) -> float:
        # Gets the fraction of the orbit that this pb travels every week.

        orbit_length = 2 * math.pi * self.sma * METERS_PER_AU
        seconds_passed = SECONDS_PER_WEEK
        length_traveled = self.orbital_velocity * seconds_passed
        
        return length_traveled / orbit_length

    def update_orbit_progress(self) -> None:
        self.orbit_progress += self._get_progress_per_week()
        if self.orbit_progress >= 1:
            self.orbit_progress -= 1
            self.visual_orbit_progress -= 1

    def perform_visual_orbit_progress_calculations(self, fps, time_ticks_per_s):
        if self.visual_orbit_progress >= self.orbit_progress:
            return

        progress = self._get_progress_per_week()

        progress_per_s = progress * time_ticks_per_s
        progress_per_frame = progress_per_s / fps

        self.visual_orbit_progress += progress_per_frame

        if self.visual_orbit_progress > self.orbit_progress:
            self.orbit_progress = self.visual_orbit_progress
