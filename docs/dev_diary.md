# Districts, 2025-04-21
Each terrestrial planet is divided into 16 districts, which represent different parts of a planet. Every district has a non-unique climate, that is selected from a list of climate presets. Earth, for example, has at year 2000 eleven ocean districts and some forest and desert districts. Each climate has unique properties, such as the inability to build most buildings in an ocean district.

Furthermore, every species living in a district has a habitability value, that is calculated from the planet's and said district's properties. Regarding planetary properties, habitability considers factors like atmospheric composition, atmospheric pressure, gravity and temperature. Said district's climate is also accounted for.

# Temperatures, 2025-04-22
I've figured out a way to represent planets' temperatures in-game. While using strings like "hot" or "moderate", there is an underlying arbitrary scale, where 0 is everything below ~-120 °C and the temperature of Earth is ~38. Base temperature is calculated by the effective temperature formula, and then additional heat is represented by extra points on the scale coming from partial pressures of greenhouse gases. Example given Venus, whose base temperature is similar to Earth's, but all the additional temperature points come from co2 and methane partial pressures. One problem with the effective temperature formula is that it includes planetary albedo, which I had hoped to exclude from the game. A simple solution which I hope will work would be to select an albedo (say 0.3) for all planets. After all, temperatures don't need to be represented that precisely. With some assumed constants, these values show up:

- Mercury: base temperature 61.8, with gases 61.8. Actual temperature 164 °C
- Venus: base temperature 39.8, with gases 330. Actual temperature 464 °C
- Earth: base temperature 30.9, with gases 38. Actual temperature 15 °C
- Mars: base temperature 21.3, with gases 23.6. Actual temperature -60 °C
- Proxima Centauri B: base temperature 26.0. Actual temperature -39 °C (estimated blackbody temperature)

The main way of representing temperature in-game will be adjectives describing temperature, and if the player hovers the mouse on the text a popup will show the temperature in my very made up scale. And if you ask for the source for the constants? My source is that I made them up. It works for now though.
