import scrapy
from scrapy_splash import SplashRequest
import re
import time
from ..items import PokemonItem


class PokemonsSpider(scrapy.Spider):
    name = "pokemons"
    allowed_domains = ["db.pokemongohub.net", "localhost"]
    
    # Configuration spécifique pour cette araignée
    custom_settings = {
        'ITEM_PIPELINES': {
            'PKMNdb.pipelines.CleanDataPipeline': 300,
            'PKMNdb.pipelines.PokemonDatabasePipeline': 900,
        },
        'SPLASH_URL': 'http://localhost:8050',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
        },
        'SPIDER_MIDDLEWARES': {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
    }

    def __init__(self, max_id=2000, *args, **kwargs):
        super(PokemonsSpider, self).__init__(*args, **kwargs)
        # Valeur paramétrable en ligne de commande
        self.MAX_POKEMON_ID = int(max_id) if max_id else 200
        self.pokemon_count = 0
        
    def start_requests(self):
        """
        Itère sur des IDs numériques croissants pour trouver les pokémons
        """
        base_url = "https://db.pokemongohub.net/pokemon/"
        
        self.logger.info(f"Trying pokemons with IDs from 1 to {self.MAX_POKEMON_ID}")
        
        # Générer des requêtes pour chaque ID possible de pokémon
        for pokemon_id in range(1, self.MAX_POKEMON_ID + 1):
            pokemon_url = f"{base_url}{pokemon_id}"
            self.logger.info(f"Scheduling request for pokemon ID: {pokemon_id}")
            yield SplashRequest(
                pokemon_url,
                self.parse_pokemon,
                args={
                    'wait': 2,
                    'timeout': 90,
                    'resource_timeout': 20,
                },
                # Retry policy for 404s
                errback=self.handle_error,
                meta={'pokemon_id': pokemon_id}
            )
    
    def handle_error(self, failure):
        """
        Gère les erreurs lors des requêtes, notamment les 404 (pokémon non trouvé)
        """
        pokemon_id = failure.request.meta.get('pokemon_id')
        self.logger.info(f"Pokemon ID {pokemon_id} not found (404 or other error)")
    
    def parse_pokemon(self, response):
        """
        Parse individual Pokemon page to extract all data
        """
        # Vérifier si la page existe et contient un Pokémon
        if response.css('h1.Card_cardTitle__URr_A::text').get() is None:
            self.logger.info(f"Skipping ID {response.meta.get('pokemon_id')} - not a valid pokemon page")
            return
        
        pokemon = PokemonItem()
        
        # Extract Pokemon ID from the URL (for internal use)
        pokemon['id'] = str(response.meta.get('pokemon_id'))
        
        # Extract Pokemon name
        name = response.css('h1.Card_cardTitle__URr_A::text').get()
        if name:
            pokemon['name'] = name.strip()
        
        # Extract Pokedex number from URL (optional)
        pokemon['pokedex_number'] = str(response.meta.get('pokemon_id'))
        
        # Extract basic stats (GO_PokemonStats)
        max_cp = response.css('tr:contains("Max CP") td strong::text').get()
        if max_cp:
            try:
                pokemon['max_cp'] = int(max_cp.strip().replace('CP', '').strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Impossible de convertir max_cp en entier: {max_cp}")
            
        attack = response.css('tr:contains("Attack") td strong::text').get()
        if attack:
            try:
                pokemon['attack'] = int(attack.strip().replace('ATK', '').strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Impossible de convertir attack en entier: {attack}")
            
        defense = response.css('tr:contains("Defense") td strong::text').get()
        if defense:
            try:
                pokemon['defense'] = int(defense.strip().replace('DEF', '').strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Impossible de convertir defense en entier: {defense}")
            
        stamina = response.css('tr:contains("Stamina") td strong::text').get()
        if stamina:
            try:
                pokemon['stamina'] = int(stamina.strip().replace('HP', '').strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Impossible de convertir stamina en entier: {stamina}")
        
        # Extract buddy distance
        buddy_distance = response.css('tr:contains("Buddy distance") td::text').get()
        if buddy_distance:
            try:
                # Extraire le nombre et convertir en flottant
                match = re.search(r'(\d+(\.\d+)?)\s*km', buddy_distance)
                if match:
                    pokemon['buddy_distance'] = float(match.group(1))
                else:
            pokemon['buddy_distance'] = buddy_distance.strip()
            except (ValueError, TypeError):
                self.logger.warning(f"Impossible de convertir buddy_distance: {buddy_distance}")
        
        # Extract released status
        released = response.css('tr:contains("Released") td::text').get()
        if released:
            pokemon['released'] = 'Yes' in released
        
        # Extract moves for learnset
        # Fast moves
        fast_moves = []
        for move in response.css('h3:contains("Fast Attacks") + ul li summary strong::text').getall():
            move_name = move.strip()
            is_elite = '*' in move_name
            fast_moves.append({
                'name': move_name.replace('*', '').strip(),
                'is_elite': is_elite,
                'is_fast': True,
                'is_charged': False
            })
        pokemon['fast_moves'] = fast_moves
        
        # Charged moves
        charged_moves = []
        for move in response.css('h3:contains("Charged Moves") + ul li summary strong::text').getall():
            move_name = move.strip()
            is_elite = '*' in move_name
            charged_moves.append({
                'name': move_name.replace('*', '').strip(),
                'is_elite': is_elite,
                'is_fast': False,
                'is_charged': True
            })
        pokemon['charged_moves'] = charged_moves
        
        self.pokemon_count += 1
        self.logger.info(f"Scraped Pokemon {pokemon.get('name')} (ID: {pokemon.get('id')}) - Total: {self.pokemon_count}")
        
        time.sleep(0.2)  # Small delay between requests
        yield pokemon 
        
    def closed(self, reason):
        """Appelé quand le spider se termine"""
        self.logger.info(f"Spider closed. Stats: {self.pokemon_count} pokemons scraped.") 