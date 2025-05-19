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
    # Move basic info
    id = scrapy.Field()
    name = scrapy.Field()
    type_id = scrapy.Field()  # Foreign key vers go_types.id
    is_fast = scrapy.Field()
    is_charged = scrapy.Field()
    
    # Gym & Raid stats
    damage = scrapy.Field()
    energy = scrapy.Field()
    duration = scrapy.Field()
    
    # PVP stats
    pvp_damage = scrapy.Field()
    pvp_energy = scrapy.Field()
    pvp_effects = scrapy.Field()
