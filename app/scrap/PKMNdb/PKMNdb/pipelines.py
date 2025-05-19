# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from pathlib import Path
from .items import PokemonItem, MoveItem

# Import database models
import sys
import os
# Add app to Python path (adjust based on actual path structure)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from app.models.GO_tables.GO_pokemon import GO_Pokemon
from app.models.GO_tables.GO_pokemon_stats import GO_PokemonStats
from app.models.GO_tables.GO_move import GO_Move
from app.models.GO_tables.GO_pokemon_learnset import GO_PokemonLearnset
from app.db.engine import engine


class CleanDataPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Remove any trailing spaces from string fields
        for field in adapter.field_names():
            value = adapter.get(field)
            if isinstance(value, str):
                adapter[field] = value.strip()
            elif isinstance(value, list):
                # Clean up strings in lists
                if all(isinstance(x, str) for x in value):
                    adapter[field] = [x.strip() for x in value]
        
        return item


class BaseDatabasePipeline:
    """Pipeline de base avec la logique commune d'initialisation de la BDD"""
    def __init__(self):
        pass
        
    def open_spider(self, spider):
        pass
        
    def close_spider(self, spider):
        pass

    def _get_session(self):
        return engine.connect("PKMNGO.db")


class PokemonDatabasePipeline(BaseDatabasePipeline):
    """Pipeline spécifique pour les données de Pokémon"""
    def __init__(self):
        super().__init__()
        self.processed_pokemon = 0
        self.processed_learnsets = 0
        
    def process_item(self, item, spider):
        if not isinstance(item, PokemonItem):
            return item
            
        self._process_pokemon_item(item, spider)
        return item
    
    def close_spider(self, spider):
        spider.logger.info(f"Pokemon pipeline - Processed: {self.processed_pokemon} Pokemon, {self.processed_learnsets} Learnsets")
        super().close_spider(spider)
    
    def _process_pokemon_item(self, item, spider):
        with self._get_session() as session:
            try:
                # Convert item to dict
                item_dict = dict(item)
                
                # Check if this Pokemon already exists
                pokemon_id = item_dict.get('id')
                name = item_dict.get('name')
                
                if not name:
                    spider.logger.warning(f"Pokemon has no name. Skipping.")
                    return
                
                existing_pokemon = session.query(GO_Pokemon).filter(
                    GO_Pokemon.name == name
                ).first()
                
                if existing_pokemon:
                    # Update existing record
                    existing_pokemon.pokedex_number = item_dict.get('pokedex_number', existing_pokemon.pokedex_number)
                    existing_pokemon.buddy_distance = item_dict.get('buddy_distance', existing_pokemon.buddy_distance)
                    existing_pokemon.released = item_dict.get('released', existing_pokemon.released)
                    
                    # Update stats
                    if hasattr(existing_pokemon, 'stats') and existing_pokemon.stats:
                        existing_pokemon.stats.max_cp = item_dict.get('max_cp', existing_pokemon.stats.max_cp)
                        existing_pokemon.stats.attack = item_dict.get('attack', existing_pokemon.stats.attack)
                        existing_pokemon.stats.defense = item_dict.get('defense', existing_pokemon.stats.defense)
                        existing_pokemon.stats.stamina = item_dict.get('stamina', existing_pokemon.stats.stamina)
                    else:
                        # Create stats if they don't exist
                        stats = GO_PokemonStats(
                            pokemon_id=existing_pokemon.id,
                            max_cp=item_dict.get('max_cp'),
                            attack=item_dict.get('attack'),
                            defense=item_dict.get('defense'),
                            stamina=item_dict.get('stamina')
                        )
                        session.add(stats)
                    
                    pokemon = existing_pokemon
                    spider.logger.info(f"Updated Pokemon: {pokemon.name} (#{pokemon.pokedex_number})")
                else:
                    # Create new Pokemon
                    pokemon = GO_Pokemon(
                        name=name,
                        pokedex_number=item_dict.get('pokedex_number'),
                        released=item_dict.get('released', True),
                        buddy_distance=item_dict.get('buddy_distance')
                    )
                    session.add(pokemon)
                    session.flush()  # Flush to get the generated ID
                    
                    # Create stats
                    stats = GO_PokemonStats(
                        pokemon_id=pokemon.id,
                        max_cp=item_dict.get('max_cp'),
                        attack=item_dict.get('attack'),
                        defense=item_dict.get('defense'),
                        stamina=item_dict.get('stamina')
                    )
                    session.add(stats)
                    spider.logger.info(f"Added new Pokemon: {pokemon.name} (#{pokemon.pokedex_number})")
                
                # Process moves (if we have a pokemon ID now)
                if pokemon.id:
                    # Process fast moves
                    fast_moves = item_dict.get('fast_moves', [])
                    for move_data in fast_moves:
                        self._add_pokemon_move(pokemon.id, move_data, is_fast=True, is_charged=False, spider=spider, session=session)
                    
                    # Process charged moves
                    charged_moves = item_dict.get('charged_moves', [])
                    for move_data in charged_moves:
                        self._add_pokemon_move(pokemon.id, move_data, is_fast=False, is_charged=True, spider=spider, session=session)
                
                self.processed_pokemon += 1
                
            except Exception as e:
                spider.logger.error(f"Error processing Pokemon item: {e}")
                raise
            
    def _add_pokemon_move(self, pokemon_id, move_data, is_fast, is_charged, spider, session):
        try:
            # Extract move name from move data (either string or dict)
            move_name = move_data['name'] if isinstance(move_data, dict) else move_data
            is_elite = move_data.get('is_elite', False) if isinstance(move_data, dict) else False
            
            # Find the move
            move = session.query(GO_Move).filter(GO_Move.name == move_name).first()
            
            if not move:
                # Create a placeholder move if it doesn't exist yet
                move = GO_Move(
                    name=move_name,
                    is_fast=is_fast,
                    is_charged=is_charged,
                    type_id=None  # Will be updated when the move is properly scraped
                )
                session.add(move)
                session.flush()
                spider.logger.info(f"Created placeholder move: {move_name}")
            
            # Check if the learnset relation already exists
            existing_learnset = session.query(GO_PokemonLearnset).filter(
                GO_PokemonLearnset.pokemon_id == pokemon_id,
                GO_PokemonLearnset.move_id == move.id
            ).first()
            
            if not existing_learnset:
                # Create the learnset relation
                learnset = GO_PokemonLearnset(
                    pokemon_id=pokemon_id,
                    move_id=move.id,
                    move_name=move_name,
                    is_fast=is_fast,
                    is_charged=is_charged,
                    is_elite=is_elite
                )
                session.add(learnset)
                self.processed_learnsets += 1
                spider.logger.debug(f"Added learnset relation: Pokemon ID {pokemon_id} - Move {move_name}")
        
        except Exception as e:
            spider.logger.error(f"Error adding Pokemon-Move relation: {e}")
            raise


class MoveDatabasePipeline(BaseDatabasePipeline):
    """Pipeline spécifique pour les données de moves"""
    def __init__(self):
        super().__init__()
        self.processed_moves = 0
        
    def process_item(self, item, spider):
        if not isinstance(item, MoveItem):
            return item
            
        self._process_move_item(item, spider)
        return item
        
    def close_spider(self, spider):
        spider.logger.info(f"Move pipeline - Processed: {self.processed_moves} Moves")
        super().close_spider(spider)
    
    def _process_move_item(self, item, spider):
        with self._get_session() as session:
            try:
                # Convert item to dict
                item_dict = dict(item)
                
                # Check if this move already exists
                move_name = item_dict.get('name')
                
                if not move_name:
                    spider.logger.warning(f"Move has no name. Skipping.")
                    return
                
                existing_move = session.query(GO_Move).filter(
                    GO_Move.name == move_name
                ).first()
                
                # Determine move type
                is_fast = item_dict.get('is_fast')
                is_charged = item_dict.get('is_charged')
                
                if existing_move:
                    # Update existing record
                    existing_move.type_id = item_dict.get('type_id', existing_move.type_id)
                    existing_move.is_fast = is_fast
                    existing_move.is_charged = is_charged
                    existing_move.damage = item_dict.get('damage', existing_move.damage)
                    existing_move.energy = item_dict.get('energy', existing_move.energy)
                    existing_move.duration = item_dict.get('duration', existing_move.duration)
                    existing_move.pvp_damage = item_dict.get('pvp_damage', existing_move.pvp_damage)
                    existing_move.pvp_energy = item_dict.get('pvp_energy', existing_move.pvp_energy)
                    existing_move.pvp_effects = item_dict.get('pvp_effects', existing_move.pvp_effects)
                    
                    move = existing_move
                    spider.logger.info(f"Updated Move: {move.name}")
                else:
                    # Create new Move
                    move = GO_Move(
                        name=move_name,
                        type_id=item_dict.get('type_id'),
                        is_fast=is_fast,
                        is_charged=is_charged,
                        damage=item_dict.get('damage'),
                        energy=item_dict.get('energy'),
                        duration=item_dict.get('duration'),
                        pvp_damage=item_dict.get('pvp_damage'),
                        pvp_energy=item_dict.get('pvp_energy'),
                        pvp_effects=item_dict.get('pvp_effects')
                    )
                    session.add(move)
                    spider.logger.info(f"Added new Move: {move.name}")
                
                self.processed_moves += 1
                
            except Exception as e:
                spider.logger.error(f"Error processing Move item: {e}")
                raise
