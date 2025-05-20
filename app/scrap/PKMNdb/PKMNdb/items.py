# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PokemonItem(scrapy.Item):
    # Pokemon basic info (GO_Pokemon)
    id = scrapy.Field()  # Internal use only
    name = scrapy.Field()
    pokedex_number = scrapy.Field()
    released = scrapy.Field()
    buddy_distance = scrapy.Field()
    
    # Pokemon stats (GO_PokemonStats)
    max_cp = scrapy.Field()
    attack = scrapy.Field()
    defense = scrapy.Field()
    stamina = scrapy.Field()
    
    # Pokemon moves (for GO_PokemonLearnset)
    fast_moves = scrapy.Field()  # List of dicts with name, is_elite, is_fast, is_charged
    charged_moves = scrapy.Field()  # List of dicts with name, is_elite, is_fast, is_charged


class MoveItem(scrapy.Item):
    # Basic info
    id = scrapy.Field()  # Move ID from URL
    name = scrapy.Field()
    type = scrapy.Field()
    tags = scrapy.Field()
    
    # Move type flags
    is_pvp = scrapy.Field()
    is_fast = scrapy.Field()
    is_charged = scrapy.Field()
    
    # Raid/Gym stats
    power = scrapy.Field()  # Base power/damage
    energy = scrapy.Field()  # Energy cost/gain
    animation_duration = scrapy.Field()  # In seconds
    damage_window = scrapy.Field()  # Start-End in seconds
    dps = scrapy.Field()  # Damage per second
    dpe = scrapy.Field()  # Damage per energy
    
    # PVP stats
    pvp_power = scrapy.Field()  # PVP power/damage
    pvp_energy = scrapy.Field()  # PVP energy cost/gain
    pvp_duration = scrapy.Field()  # In seconds for fast moves, in turns for charged moves
    pvp_dps = scrapy.Field()  # PVP damage per second
    pvp_dpe = scrapy.Field()  # PVP damage per energy
    pvp_effects = scrapy.Field()  # Special effects in PVP
