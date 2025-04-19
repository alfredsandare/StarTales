Woow, documentation.

Modifiers can be pretty incomprehensible I think, so here's how they work.

A modifier is a value in a civ, and modifiers can affect other modifiers, that's why they exist in the first place. For example, a planet can generate science gain every week, which affects the civ's total science gain each week. Perhaps the civ has some modifier that gives +10% science gain (a base, percentage modifier with a multiplication factor of 1.1), which will automatically be calculated.

Many values are not only a modifier, they also exist in other places in the code. For example population. Every TerrestrialBody has a Population object, which stores data about how many people of each species live there. But the civ that owns the planet also has modifiers for population, whose base values are retrieved from the tb's population. When values like science gain are retrieved every week, they are retrieved from the civ's ModifierHandler.

## class Modifier

### Properties

- `name`: `str`. Name of the modifier.
- `base_value`: `float`. The base value of the modifier. Then, the modifiers value is its base value added with values from other modifiers that affect this modifier.
- `affects`: `list[tuple[str, float, bool]]`. A list of tuples describing which modifiers this modifier affects. Each tuple represents one affected modifier. The first element of a tuple holds the id of the affected modifier. The second element is a multiplier, which this modifier's value will be multiplied by when added to the affected modifier. Can be `float`, `str` or `callable`. If callable, the function will be called and the returned value used as the multiplier. The third element tells whether the value of this modifier will be added to the affected modifier, OR, if this modifier holds a value that the affected modifier will be multiplied by.
- `id`: `str`. The id of this modifier.
- `get_base_value_func`: `callable`. When calculating modifiers, this function will be called to fetch the modifier's base value, instead of using its base_value property.
- `is_base`: `bool`. Whether or not this modifier is a base modifier. A base modifier cannot be affected by other modifiers, and they will be displayed differently in the game.
- `affects_generators`: `list[tuple[callable, float OR callable, bool]]`. A list of tuples that generates affects-tuples. The callable should return a list of strings, and for all strings a new affects-tuple will be created and added to `self.affects`. The second value of the tuple is the multiplier, which can either be provided directly with a float value, or with a callable that returns a float value. The function will be called with one positional argument, the id of the affects-tuple.

## Spreadsheet explanation

In the spreadsheet every modifier type is listed. They're called "modifier type" because some modifier types instantiate multiple modifiers.

Explanation for column titles:

- Type ID: A unique ID for every modifier type.
- Name: Its name.
- ID format: How the modifier instances' IDs should be formatted.
- Desc: Description
- Affects: Which modifier types this modifier type affects, formatted like: [affect_id, multiplier, is_percentage]. See society/modifier.py for further explanation.
- Middle: Whether or not this modifier type is a middle modifier type. A middle modifier type is a modifier type that acts as a "middle" between modifiers.
- Multiple: Whether or not this modifier type instantiates multiple modifiers.
- Multiple format: How a modifier type should be instantiated.
