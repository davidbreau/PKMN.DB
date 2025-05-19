import scrapy
import re
from PKMNdb.items import MoveItem


class MovesSpider(scrapy.Spider):
    name = "moves"
    allowed_domains = ["db.pokemongohub.net"]
    
    # Starting with both fast and charged move lists
    start_urls = [
        "https://db.pokemongohub.net/moves-list/category-fast",  # Fast moves
        "https://db.pokemongohub.net/moves-list/category-charge"  # Charged moves
    ]
    
    # Mapping des types vers leurs IDs
    TYPE_ID_MAPPING = {
        "Normal": 1,
        "Fighting": 2,
        "Flying": 3,
        "Poison": 4,
        "Ground": 5,
        "Rock": 6,
        "Bug": 7,
        "Ghost": 8,
        "Steel": 9,
        "Fire": 10,
        "Water": 11,
        "Grass": 12,
        "Electric": 13,
        "Psychic": 14,
        "Ice": 15,
        "Dragon": 16,
        "Dark": 17,
        "Fairy": 18
    }
    
    # Paramètre de limite pour les tests
    # Mettre à None pour désactiver la limite
    LIMIT = 5  # Limiter à 5 attaques par catégorie pour les tests
    
    # Configuration spécifique pour cette araignée
    custom_settings = {
        'ITEM_PIPELINES': {
            'PKMNdb.pipelines.CleanDataPipeline': 300,
            'PKMNdb.pipelines.MoveDatabasePipeline': 900,
        }
    }
    
    def __init__(self, limit=None, *args, **kwargs):
        super(MovesSpider, self).__init__(*args, **kwargs)
        # La limite peut être passée par la ligne de commande
        if limit is not None:
            self.LIMIT = int(limit) if limit.lower() != 'none' else None
        
        # Compteurs pour le suivi des limites par catégorie
        self.fast_moves_count = 0
        self.charged_moves_count = 0
        self.logger.info(f"MovesSpider initialisé avec une limite de {self.LIMIT if self.LIMIT is not None else 'aucune limite'} par catégorie")
    
    def parse(self, response):
        """
        Parse the moves list pages (fast or charged)
        """
        # Determine move type based on URL
        move_category = "fast" if "category-fast" in response.url else "charged"
        
        # Extract move links
        move_links = response.css('a.MoveChip_moveChipContent__Oo_tS::attr(href)').getall()
        
        # Remove duplicates
        move_links = list(set(move_links))
        
        # Appliquer la limite si configurée
        if self.LIMIT is not None:
            if move_category == "fast":
                remaining = self.LIMIT - self.fast_moves_count
                if remaining <= 0:
                    self.logger.info(f"Limite de {self.LIMIT} attaques rapides atteinte. Arrêt du scraping pour cette catégorie.")
                    return
                move_links = move_links[:remaining]
            else:  # charged
                remaining = self.LIMIT - self.charged_moves_count
                if remaining <= 0:
                    self.logger.info(f"Limite de {self.LIMIT} attaques chargées atteinte. Arrêt du scraping pour cette catégorie.")
                    return
                move_links = move_links[:remaining]
        
        for move_link in move_links:
            # Pass the move category to the callback
            yield response.follow(
                move_link, 
                callback=self.parse_move,
                cb_kwargs={"move_category": move_category}
            )
    
    def parse_move(self, response, move_category):
        """
        Parse individual move page to extract all data
        """
        move = MoveItem()
        
        # Extract move ID from URL - simplified
        move['id'] = response.url.split('/')[-1]
        
        # Extract move name
        name = response.css('h1.Card_cardTitle__URr_A::text').get()
        if name:
            move['name'] = name.strip()
        
        # Extract move type and convert to type_id
        move_type = response.css('tr:contains("Type") td span::text').get()
        if not move_type:
            # Backup: try to get from the type image
            move_type = response.css('figure img::attr(title)').get()
        if move_type:
            move_type = move_type.strip()
            # Convertir le type en type_id
            move['type_id'] = self.TYPE_ID_MAPPING.get(move_type)
            if move['type_id'] is None:
                self.logger.warning(f"Type inconnu trouvé: {move_type} pour {move.get('name')}")
        
        # Set is_fast and is_charged based on category
        move['is_fast'] = (move_category == "fast")
        move['is_charged'] = (move_category == "charged")
        
        # Extract base stats
        stats_section = response.css('section:contains("Gym and Raid Battles")')
        
        # Extract damage
        damage = stats_section.css('tr:contains("Damage") td::text').get()
        if damage:
            move['damage'] = damage.strip()
        
        # Extract energy
        energy = stats_section.css('tr:contains("Energy") td::text').get()
        if energy:
            move['energy'] = energy.strip()
        
        # Extract duration (for fast moves)
        duration = stats_section.css('tr:contains("Duration") td::text').get()
        if duration:
            move['duration'] = duration.strip()
        
        # Extract PVP stats
        pvp_section = response.css('section:contains("Trainer Battles")')
        
        # PVP damage
        pvp_damage = pvp_section.css('tr:contains("Damage") td::text').get()
        if pvp_damage:
            move['pvp_damage'] = pvp_damage.strip()
        
        # PVP energy
        pvp_energy = pvp_section.css('tr:contains("Energy") td::text').get()
        if pvp_energy:
            move['pvp_energy'] = pvp_energy.strip()
        
        # For charged moves, extract PVP effects if any
        pvp_effects = pvp_section.xpath('./following-sibling::section[1]/header[contains(text(), "Effects")]/following-sibling::text()').get()
        if pvp_effects and "no special effects" not in pvp_effects.lower():
            move['pvp_effects'] = pvp_effects.strip()
        
        # Extract Pokémon that can learn this move
        pokemon_with_move = response.css('ul.MoveInfo_pokemonList__ZJB1N li a::text').getall()
        if pokemon_with_move:
            move['pokemon_with_move'] = [p.strip() for p in pokemon_with_move]
        
        # Incrémenter le compteur selon la catégorie
        if move_category == "fast":
            self.fast_moves_count += 1
            count_text = f"{self.fast_moves_count}/{self.LIMIT if self.LIMIT is not None else '∞'}"
        else:  # charged
            self.charged_moves_count += 1
            count_text = f"{self.charged_moves_count}/{self.LIMIT if self.LIMIT is not None else '∞'}"
            
        self.logger.info(f"Scraped Move {count_text}: {move.get('name')} ({move_category})")
        
        yield move 