import scrapy
import re
import time
from ..items import PokemonItem


class PokemonsSpider(scrapy.Spider):
    name = "pokemons"
    allowed_domains = ["db.pokemongohub.net"]
    start_urls = ["https://db.pokemongohub.net/tools/pokedex"]
    
    # Paramètre de limite pour les tests
    # Mettre à None pour désactiver la limite
    LIMIT = None  # No limit on number of Pokemon to scrape
    
    # Configuration spécifique pour cette araignée
    custom_settings = {
        'ITEM_PIPELINES': {
            'PKMNdb.pipelines.CleanDataPipeline': 300,
            'PKMNdb.pipelines.PokemonDatabasePipeline': 900,
        }
    }
    
    def __init__(self, limit=None, *args, **kwargs):
        super(PokemonsSpider, self).__init__(*args, **kwargs)
        # La limite peut être passée par la ligne de commande
        if limit is not None:
            self.LIMIT = int(limit) if limit.lower() != 'none' else None
        
        # Compteur pour le suivi de la limite
        self.pokemon_count = 0
        self.logger.info(f"PokemonsSpider initialisé avec une limite de {self.LIMIT if self.LIMIT is not None else 'aucune limite'}")
    
    def parse(self, response):
        """
        Start by parsing the regional pokedex page to get all pokedex lists
        """
        # Extract all regional pokedex links
        pokedex_links = response.css('a[href^="/pokedex/"]:has(h2)::attr(href)').getall()
        
        # Remove duplicates
        pokedex_links = list(set(pokedex_links))
        
        for pokedex_link in pokedex_links:
            yield response.follow(pokedex_link, callback=self.parse_pokedex)
    
    def parse_pokedex(self, response):
        """
        Parse each pokedex page to get the list of Pokemon
        """
        # Extract all Pokemon links
        pokemon_links = response.css('span.PokemonChip_pokemonChipContent__8xgo_').xpath('./parent::a/@href').getall()
        
        # Remove duplicates and filter out non-Pokemon pages
        pokemon_links = [link for link in set(pokemon_links) if re.match(r'/pokemon/\d+$', link)]
        
        # Appliquer la limite si configurée
        if self.LIMIT is not None:
            remaining = max(0, self.LIMIT - self.pokemon_count)
            if remaining == 0:
                self.logger.info(f"Limite de {self.LIMIT} Pokémon atteinte. Arrêt du scraping.")
                return
            pokemon_links = pokemon_links[:remaining]
        
        for pokemon_link in pokemon_links:
            self.pokemon_count += 1  # Incrémenter avant de scraper
            yield response.follow(pokemon_link, callback=self.parse_pokemon)
    
    def parse_pokemon(self, response):
        """
        Parse individual Pokemon page to extract all data
        """
        pokemon = PokemonItem()
        
        # Extract Pokemon ID from the URL (for internal use)
        pokemon_id_match = re.search(r'/pokemon/(\d+)', response.url)
        if pokemon_id_match:
            pokemon['id'] = pokemon_id_match.group(1)
        
        # Extract Pokemon name
        name = response.css('h1.Card_cardTitle__URr_A::text').get()
        if name:
            pokemon['name'] = name.strip()
        
        # Extract Pokedex number from URL (optional)
        url_match = re.search(r'/pokemon/(\d+)', response.url)
        if url_match:
            pokemon['pokedex_number'] = url_match.group(1)
        
        # Extract basic stats (GO_PokemonStats)
        max_cp = response.css('tr:contains("Max CP") td strong::text').get()
        if max_cp:
            pokemon['max_cp'] = max_cp.strip().replace('CP', '').strip()
            
        attack = response.css('tr:contains("Attack") td strong::text').get()
        if attack:
            pokemon['attack'] = attack.strip().replace('ATK', '').strip()
            
        defense = response.css('tr:contains("Defense") td strong::text').get()
        if defense:
            pokemon['defense'] = defense.strip().replace('DEF', '').strip()
            
        stamina = response.css('tr:contains("Stamina") td strong::text').get()
        if stamina:
            pokemon['stamina'] = stamina.strip().replace('HP', '').strip()
        
        # Extract buddy distance
        buddy_distance = response.css('tr:contains("Buddy distance") td::text').get()
        if buddy_distance:
            pokemon['buddy_distance'] = buddy_distance.strip()
        
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
        
        self.logger.info(f"Scraped Pokémon {self.pokemon_count}/{self.LIMIT if self.LIMIT is not None else '∞'}: {pokemon.get('name')} (#{pokemon.get('pokedex_number')})")
        
        time.sleep(0.2)  # Small delay between requests
        yield pokemon 