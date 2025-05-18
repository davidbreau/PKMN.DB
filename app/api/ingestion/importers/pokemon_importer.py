import logging
from app.api.ingestion.client import PokeApiClient
from app.models.enums.pokeapi import EndPoint
from app.models.tables.pokemon import Pokemon
from app.models.tables.pokemon_detail import PokemonDetail
from app.models.tables.pokemon_stat import PokemonStat
from app.models.tables.pokemon_sprite import PokemonSprite
from app.models.tables.pokedex_number import PokedexNumber
from app.models.tables.pokemon_ability import PokemonAbility
from app.models.tables.pokemon_learnset import PokemonLearnset
from app.models.tables.move import Move
from app.models.tables.ability import Ability
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from functools import partial
import ujson
import time
from sqlmodel import Session, SQLModel, create_engine, select, delete

# Configuration variables
LIMIT_IMPORT = False
IMPORT_LIMIT = None  # Unlimited

logger = logging.getLogger(__name__)

# Default path for PKMN.db database
DB_PATH = Path('app/db/PKMN.db')
# Create SQLAlchemy engine directly
SQLITE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
# use standard SQLAlchemy engine

class PokemonImporter:
    """ Importer for Pokemon data from both Pokemon and Pokemon-species endpoints. """
    
    def __init__(self, client: Optional[PokeApiClient] = None):
        """ Initialize the Pokemon importer.
        Args:
            client: Optional API client, creates a new client by default """
        self.client = client or PokeApiClient()
        self.get_pokemon = partial(self.client.call, EndPoint.POKEMON)
        self.get_pokemon_species = partial(self.client.call, EndPoint.POKEMON_SPECIES)
        self.get_pokemon_form = partial(self.client.call, EndPoint.POKEMON_FORM)
        self.get_abilities = partial(self.client.call, EndPoint.ABILITY)
        self.get_moves = partial(self.client.call, EndPoint.MOVE)
        
        # Cache to avoid repeated API calls
        self.species_cache = {}
        self.pokemon_cache = {}
        self.ability_cache = {}
        self.move_cache = {}
        self.form_cache = {}
        
    def import_all(self):
        """ Import all Pokemon data to the database. """
        # Create tables if they don't exist
        SQLModel.metadata.create_all(engine)
        
        with Session(engine) as session:
            try:
                count = 0
                
                for pokemon_id, pokemon_data in self.client.get_items_generator(EndPoint.POKEMON):
                    if LIMIT_IMPORT and count >= IMPORT_LIMIT:
                        logger.info(f"Reached import limit of {IMPORT_LIMIT}")
                        break
                    
                    # Fetching the corresponding species data
                    species_id = self._extract_id_from_url(pokemon_data.get("species", {}).get("url", ""))
                    species_data = self._get_species_data(species_id)
                    
                    if not species_data:
                        logger.warning(f"Could not fetch species data for Pokemon ID {pokemon_id}")
                        continue
                    
                    try:
                        # Create Pokemon entry
                        pokemon = self._create_pokemon(pokemon_id, pokemon_data, species_data, session)
                        
                        # Create related entries
                        self._create_pokemon_detail(pokemon.id, pokemon_data, species_data, session)
                        self._create_pokemon_stat(pokemon.id, pokemon_data, session)
                        self._create_pokemon_sprite(pokemon.id, pokemon_data, session)
                        self._create_pokedex_number(pokemon.id, species_data, session)
                        self._create_pokemon_abilities(pokemon.id, pokemon_data, session)
                        self._create_pokemon_learnset(pokemon.id, pokemon_data, session)
                        
                        count += 1
                        logger.info(f"Imported Pokemon {pokemon.name_en} (ID: {pokemon.id})")
                        
                        # Commit after each Pokemon to avoid losing all data if something fails
                        session.commit()
                        
                        # Small delay to respect API rate limits
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error importing Pokemon ID {pokemon_id}: {e}")
                        session.rollback()
                
                logger.info(f"Imported {count} Pokemon")
                
            except Exception as e:
                logger.error(f"Error during Pokemon import: {e}")
                session.rollback()
                raise
    
    def _get_species_data(self, species_id: int) -> Optional[Dict[str, Any]]:
        """ Get species data from the API or cache.
        Args:
            species_id: The species ID
        Returns:
            The species data or None if not found
        """
        if not species_id:
            return None
            
        if species_id in self.species_cache:
            return self.species_cache[species_id]
            
        try:
            species_data = self.get_pokemon_species(resource_id=str(species_id))
            self.species_cache[species_id] = species_data
            return species_data
        except Exception as e:
            logger.error(f"Error fetching species data for ID {species_id}: {e}")
            return None
    
    def _get_ability_data(self, ability_id: int) -> Optional[Dict[str, Any]]:
        """ Get ability data from the API or cache.
        Args:
            ability_id: The ability ID
        Returns:
            The ability data or None if not found
        """
        if not ability_id:
            return None
            
        if ability_id in self.ability_cache:
            return self.ability_cache[ability_id]
            
        try:
            ability_data = self.get_abilities(resource_id=str(ability_id))
            self.ability_cache[ability_id] = ability_data
            return ability_data
        except Exception as e:
            logger.error(f"Error fetching ability data for ID {ability_id}: {e}")
            return None
    
    def _get_move_data(self, move_id: int) -> Optional[Dict[str, Any]]:
        """ Get move data from the API or cache.
        Args:
            move_id: The move ID
        Returns:
            The move data or None if not found
        """
        if not move_id:
            return None
            
        if move_id in self.move_cache:
            return self.move_cache[move_id]
            
        try:
            move_data = self.get_moves(resource_id=str(move_id))
            self.move_cache[move_id] = move_data
            return move_data
        except Exception as e:
            logger.error(f"Error fetching move data for ID {move_id}: {e}")
            return None
    
    def _get_pokemon_form_data(self, form_id: int) -> Optional[Dict[str, Any]]:
        """ Get form data from the API or cache.
        Args:
            form_id: The form ID
        Returns:
            The form data or None if not found
        """
        if not form_id:
            return None
            
        if form_id in self.form_cache:
            logger.info(f"Using cached form data for ID {form_id}")
            return self.form_cache[form_id]
            
        try:
            logger.info(f"Fetching form data for Pokemon form ID {form_id}")
            form_data = self.get_pokemon_form(resource_id=str(form_id))
            self.form_cache[form_id] = form_data
            return form_data
        except Exception as e:
            logger.error(f"Error fetching form data for ID {form_id}: {e}")
            return None
    
    def _extract_id_from_url(self, url: str) -> Optional[int]:
        """ Extract the ID from a PokeAPI URL.
        Args:
            url: The URL to extract ID from
        Returns:
            The extracted ID or None if not found
        """
        if not url:
            return None
            
        # URL format is usually like: https://pokeapi.co/api/v2/pokemon-species/1/
        try:
            return int(url.rstrip("/").split("/")[-1])
        except (ValueError, IndexError):
            return None
    
    def _create_pokemon(self, pokemon_id: int, pokemon_data: Dict[str, Any], 
                        species_data: Dict[str, Any], session: Session) -> Pokemon:
        """ Create a Pokemon entry in the database.
        Args:
            pokemon_id: The Pokemon ID
            pokemon_data: The Pokemon API data
            species_data: The species API data
            session: Database session
        Returns:
            The created Pokemon object
        """
        # Find English and French names from species data (best names for regular forms)
        species_name_en = next((name.get("name") for name in species_data.get("names", [])
                        if name.get("language", {}).get("name") == "en"), None)
        species_name_fr = next((name.get("name") for name in species_data.get("names", [])
                        if name.get("language", {}).get("name") == "fr"), None)
        
        # Default to API names if names are not found in species data
        name_en = species_name_en or pokemon_data.get("name", "")
        name_fr = species_name_fr or pokemon_data.get("name", "")
        
        # Check if this is a form variant (indicated by a dash in the name)
        is_form_variant = "-" in pokemon_data.get("name", "")
        
        if is_form_variant:
            # Get the form URL from the forms array if available
            form_url = None
            forms = pokemon_data.get("forms", [])
            if forms and len(forms) > 0:
                form_url = forms[0].get("url", "")
                
            # Extract the form ID from the URL
            form_id = self._extract_id_from_url(form_url) if form_url else pokemon_id
            
            form_data = self._get_pokemon_form_data(form_id)
            
            if form_data:
                # Update names if available in form data
                # First check in the "names" field which contains fully formatted names
                form_names = form_data.get("names", [])
                
                # Get English form name if available
                en_form_name = next((name.get("name") for name in form_names
                               if name.get("language", {}).get("name") == "en"), None)
                if en_form_name:
                    name_en = en_form_name  # Use the better formatted name from form data
                
                # Get French form name if available
                fr_form_name = next((name.get("name") for name in form_names
                               if name.get("language", {}).get("name") == "fr"), None)
                if fr_form_name:
                    name_fr = fr_form_name  # Use the properly formatted name with region
                
                # If no names found in the "names" array, try to construct a better name
                # from the form_names which contain form descriptors
                if not en_form_name and not fr_form_name:
                    base_pokemon_name = species_name_en or species_data.get("name", "").capitalize()
                    
                    # Get English form description if available
                    form_descriptions = form_data.get("form_names", [])
                    en_form_description = next((desc.get("name") for desc in form_descriptions
                                         if desc.get("language", {}).get("name") == "en"), None)
                    fr_form_description = next((desc.get("name") for desc in form_descriptions
                                         if desc.get("language", {}).get("name") == "fr"), None)
                    
                    # Combine base name with form description for a better display
                    if en_form_description and base_pokemon_name:
                        name_en = f"{base_pokemon_name} ({en_form_description})"
                    
                    # Do the same for French
                    fr_base_name = species_name_fr or next((name.get("name") for name in species_data.get("names", [])
                                       if name.get("language", {}).get("name") == "fr"), None)
                    
                    if fr_form_description and fr_base_name:
                        name_fr = f"{fr_base_name} ({fr_form_description})"
                        
                logger.info(f"Using form names: EN='{name_en}', FR='{name_fr}' for Pokemon ID {pokemon_id}")
        
        # Get types
        types = pokemon_data.get("types", [])
        type_1_id = next((t.get("type", {}).get("url", "").rstrip("/").split("/")[-1] 
                         for t in types if t.get("slot") == 1), None)
        type_2_id = next((t.get("type", {}).get("url", "").rstrip("/").split("/")[-1] 
                         for t in types if t.get("slot") == 2), None)
        
        # Create Pokemon object
        pokemon = Pokemon(
            id=pokemon_id,
            national_pokedex_number=pokemon_id,
            name_en=name_en,
            name_fr=name_fr,
            type_1_id=int(type_1_id) if type_1_id else None,
            type_2_id=int(type_2_id) if type_2_id else None,
            sprite_url=pokemon_data.get("sprites", {}).get("front_default"),
            cry_url=pokemon_data.get("cries", {}).get("latest")
        )
        
        # Check if Pokemon already exists
        existing = session.get(Pokemon, pokemon_id)
        if existing:
            logger.info(f"Pokemon ID {pokemon_id} already exists, updating")
            # Update existing Pokemon
            for key, value in pokemon.dict(exclude={"id"}).items():
                setattr(existing, key, value)
            return existing
        
        # Add new Pokemon
        session.add(pokemon)
        return pokemon
    
    def _create_pokemon_detail(self, pokemon_id: int, pokemon_data: Dict[str, Any], 
                              species_data: Dict[str, Any], session: Session) -> None:
        """ Create a PokemonDetail entry in the database.
        Args:
            pokemon_id: The Pokemon ID
            pokemon_data: The Pokemon API data
            species_data: The species API data
            session: Database session
        """
        # Extract relevant data
        species_id = self._extract_id_from_url(pokemon_data.get("species", {}).get("url", ""))
        height_cm = pokemon_data.get("height", 0) * 10  # Convert to cm
        weight_kg = pokemon_data.get("weight", 0) / 10  # Convert to kg
        
        # Extract species specific data
        gender_rate = species_data.get("gender_rate", -1)
        capture_rate = species_data.get("capture_rate")
        base_happiness = species_data.get("base_happiness")
        is_baby = species_data.get("is_baby", False)
        is_legendary = species_data.get("is_legendary", False)
        is_mythical = species_data.get("is_mythical", False)
        hatch_counter = species_data.get("hatch_counter")
        has_gender_differences = species_data.get("has_gender_differences", False)
        forms_switchable = species_data.get("forms_switchable", False)
        
        # Extract egg groups
        egg_groups = species_data.get("egg_groups", [])
        egg_group_1 = egg_groups[0].get("name") if len(egg_groups) > 0 else None
        egg_group_2 = egg_groups[1].get("name") if len(egg_groups) > 1 else None
        
        # Extract other data
        color = species_data.get("color", {}).get("name")
        shape = species_data.get("shape", {}).get("name")
        habitat = species_data.get("habitat", {}).get("name") if species_data.get("habitat") else None
        generation = species_data.get("generation", {}).get("name")
        growth_rate = species_data.get("growth_rate", {}).get("name")
        
        # Evolution chain and evolves from
        evolution_chain_id = self._extract_id_from_url(species_data.get("evolution_chain", {}).get("url", ""))
        evolves_from_species_id = self._extract_id_from_url(
            species_data.get("evolves_from_species", {}).get("url", "") if species_data.get("evolves_from_species") else ""
        )
        
        # Create or update detail
        detail = PokemonDetail(
            pokemon_id=pokemon_id,
            species_id=species_id,
            height_m=height_cm,  # The field name is height_m but we're storing in cm
            weight_kg=weight_kg, 
            base_experience=pokemon_data.get("base_experience"),
            order=pokemon_data.get("order"),
            is_default=pokemon_data.get("is_default", True),
            is_legendary=is_legendary,
            is_mythical=is_mythical,
            is_baby=is_baby,
            gender_rate=gender_rate,
            capture_rate=capture_rate,
            base_happiness=base_happiness,
            hatch_counter=hatch_counter,
            has_gender_differences=has_gender_differences,
            forms_switchable=forms_switchable,
            egg_group_1=egg_group_1,
            egg_group_2=egg_group_2,
            color=color,
            shape=shape,
            evolves_from_species_id=evolves_from_species_id,
            evolution_chain_id=evolution_chain_id,
            habitat=habitat,
            generation=generation,
            growth_rate=growth_rate
        )
        
        # Check if detail already exists
        existing = session.get(PokemonDetail, pokemon_id)
        if existing:
            logger.info(f"PokemonDetail for ID {pokemon_id} already exists, updating")
            # Update existing detail
            for key, value in detail.dict(exclude={"pokemon_id"}).items():
                setattr(existing, key, value)
        else:
            # Add new detail
            session.add(detail)
    
    def _create_pokemon_stat(self, pokemon_id: int, pokemon_data: Dict[str, Any], 
                            session: Session) -> None:
        """ Create a PokemonStat entry in the database.
        Args:
            pokemon_id: The Pokemon ID
            pokemon_data: The Pokemon API data
            session: Database session
        """
        # Extract stats
        stats = pokemon_data.get("stats", [])
        hp = next((s.get("base_stat", 0) for s in stats if s.get("stat", {}).get("name") == "hp"), 0)
        attack = next((s.get("base_stat", 0) for s in stats if s.get("stat", {}).get("name") == "attack"), 0)
        defense = next((s.get("base_stat", 0) for s in stats if s.get("stat", {}).get("name") == "defense"), 0)
        special_attack = next((s.get("base_stat", 0) for s in stats if s.get("stat", {}).get("name") == "special-attack"), 0)
        special_defense = next((s.get("base_stat", 0) for s in stats if s.get("stat", {}).get("name") == "special-defense"), 0)
        speed = next((s.get("base_stat", 0) for s in stats if s.get("stat", {}).get("name") == "speed"), 0)
        
        # Create or update stat
        stat = PokemonStat(
            pokemon_id=pokemon_id,
            hp=hp,
            attack=attack,
            defense=defense,
            special_attack=special_attack,
            special_defense=special_defense,
            speed=speed
        )
        
        # Check if stat already exists
        existing = session.get(PokemonStat, pokemon_id)
        if existing:
            logger.info(f"PokemonStat for ID {pokemon_id} already exists, updating")
            # Update existing stat
            for key, value in stat.dict(exclude={"pokemon_id"}).items():
                setattr(existing, key, value)
        else:
            # Add new stat
            session.add(stat)
    
    def _create_pokemon_sprite(self, pokemon_id: int, pokemon_data: Dict[str, Any], 
                              session: Session) -> None:
        """ Create a PokemonSprite entry in the database.
        Args:
            pokemon_id: The Pokemon ID
            pokemon_data: The Pokemon API data
            session: Database session
        """
        # Extract sprites
        sprites = pokemon_data.get("sprites", {})
        
        # Create or update sprite
        sprite = PokemonSprite(
            pokemon_id=pokemon_id,
            front_default=sprites.get("front_default"),
            back_default=sprites.get("back_default"),
            front_shiny=sprites.get("front_shiny"),
            back_shiny=sprites.get("back_shiny"),
            official_artwork=sprites.get("other", {}).get("official-artwork", {}).get("front_default"),
            official_artwork_shiny=sprites.get("other", {}).get("official-artwork", {}).get("front_shiny"),
            dream_world=sprites.get("other", {}).get("dream_world", {}).get("front_default"),
            home_default=sprites.get("other", {}).get("home", {}).get("front_default"),
            home_shiny=sprites.get("other", {}).get("home", {}).get("front_shiny"),
            pokemon_go=sprites.get("other", {}).get("go", {}).get("front_default"),
            pokemon_go_shiny=sprites.get("other", {}).get("go", {}).get("front_shiny")
        )
        
        # Check if sprite already exists
        existing = session.get(PokemonSprite, pokemon_id)
        if existing:
            logger.info(f"PokemonSprite for ID {pokemon_id} already exists, updating")
            # Update existing sprite
            for key, value in sprite.dict(exclude={"pokemon_id"}).items():
                setattr(existing, key, value)
        else:
            # Add new sprite
            session.add(sprite)
    
    def _create_pokedex_number(self, pokemon_id: int, species_data: Dict[str, Any], 
                              session: Session) -> None:
        """ Create a PokedexNumber entry in the database.
        Args:
            pokemon_id: The Pokemon ID
            species_data: The species API data
            session: Database session
        """
        # Extract pokedex numbers
        pokedex_numbers = species_data.get("pokedex_numbers", [])
        
        # Create empty pokedex entry
        pokedex = PokedexNumber(pokemon_id=pokemon_id)
        
        # Define mapping between pokedex names and field names
        pokedex_mapping = {
            "national": "national",
            "kanto": "kanto",
            "original-johto": "original_johto",
            "updated-johto": "updated_johto",
            "hoenn": "hoenn",
            "original-sinnoh": "original_sinnoh",
            "extended-sinnoh": "extended_sinnoh",
            "unova": "unova_bw",  # Approximation
            "kalos-central": "kalos_central",
            "kalos-coastal": "kalos_coastal",
            "kalos-mountain": "kalos_mountain",
            "alola": "alola",
            "melemele": "melemele",
            "akala": "akala",
            "ulaula": "ulaula",
            "poni": "poni",
            "galar": "galar",
            "isle-of-armor": "isle_of_armor",
            "crown-tundra": "crown_tundra",
            "hisui": "hisui",
            "paldea": "paldea",
        }
        
        # Fill in pokedex numbers
        for entry in pokedex_numbers:
            pokedex_name = entry.get("pokedex", {}).get("name")
            entry_number = entry.get("entry_number")
            
            if pokedex_name in pokedex_mapping:
                field_name = pokedex_mapping[pokedex_name]
                setattr(pokedex, field_name, entry_number)
        
        # Always set national number if available
        if not pokedex.national:
            pokedex.national = pokemon_id
        
        # Check if pokedex already exists
        existing = session.get(PokedexNumber, pokemon_id)
        if existing:
            logger.info(f"PokedexNumber for ID {pokemon_id} already exists, updating")
            # Update existing pokedex
            for key, value in pokedex.dict(exclude={"pokemon_id"}).items():
                if value is not None:  # Only update non-None values
                    setattr(existing, key, value)
        else:
            # Add new pokedex
            session.add(pokedex)
    
    def _create_pokemon_abilities(self, pokemon_id: int, pokemon_data: Dict[str, Any],
                                session: Session) -> None:
        """ Create PokemonAbility entries in the database.
        Args:
            pokemon_id: The Pokemon ID
            pokemon_data: The Pokemon API data
            session: Database session
        """
        # Extract abilities
        abilities = pokemon_data.get("abilities", [])
        
        # Create new ability entries
        for ability_data in abilities:
            ability_url = ability_data.get("ability", {}).get("url", "")
            ability_id = self._extract_id_from_url(ability_url)
            ability_name = ability_data.get("ability", {}).get("name", "")
            is_hidden = ability_data.get("is_hidden", False)
            slot = ability_data.get("slot", 0)
            
            # Create ability entry
            ability = PokemonAbility(
                pokemon_id=pokemon_id,
                ability_id=ability_id,
                ability_name=ability_name,
                is_hidden=is_hidden,
                slot=slot
            )
            
            # Add new ability
            session.add(ability)
            
        logger.info(f"Added {len(abilities)} abilities for Pokemon ID {pokemon_id}")
    
    def _create_pokemon_learnset(self, pokemon_id: int, pokemon_data: Dict[str, Any],
                               session: Session) -> None:
        """ Create PokemonLearnset entries in the database.
        Args:
            pokemon_id: The Pokemon ID
            pokemon_data: The Pokemon API data
            session: Database session
        """
        # Extract moves
        moves = pokemon_data.get("moves", [])
        
        learn_count = 0
        
        # Create new learnset entries
        for move_data in moves:
            move_url = move_data.get("move", {}).get("url", "")
            move_id = self._extract_id_from_url(move_url)
            move_name = move_data.get("move", {}).get("name", "")
            
            # Get version group details
            version_group_details = move_data.get("version_group_details", [])
            
            # For each version group where the Pokemon can learn this move
            for vg_detail in version_group_details:
                method_data = vg_detail.get("move_learn_method", {})
                method = method_data.get("name", "unknown")
                level = vg_detail.get("level_learned_at", 0)
                version_group = vg_detail.get("version_group", {}).get("name", "unknown")
                
                # Create learnset entry
                learnset = PokemonLearnset(
                    pokemon_id=pokemon_id,
                    move_id=move_id,
                    move_name=move_name,
                    method=method,
                    level=level,
                    version_group=version_group
                )
                
                # Add new learnset
                session.add(learnset)
                learn_count += 1
        
        logger.info(f"Added {learn_count} learnset entries for Pokemon ID {pokemon_id}")

# For CLI usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    importer = PokemonImporter()
    importer.import_all() 