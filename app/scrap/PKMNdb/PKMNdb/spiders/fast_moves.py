import scrapy
from scrapy_splash import SplashRequest
import re
import time
from ..items import MoveItem


class FastMovesSpider(scrapy.Spider):
    name = "fast_moves"
    allowed_domains = ["db.pokemongohub.net", "localhost"]
    
    # Configuration spécifique pour cette araignée
    custom_settings = {
        'ITEM_PIPELINES': {
            'PKMNdb.pipelines.CleanDataPipeline': 300,
            'PKMNdb.pipelines.MoveDatabasePipeline': 900,
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

    def start_requests(self):
        """
        Itère sur des IDs numériques croissants pour trouver les moves
        """
        # On commence à l'ID 1 et on essaie jusqu'à MAX_MOVE_ID
        MAX_MOVE_ID = 300  # Valeur suffisamment grande pour couvrir tous les moves
        base_url = "https://db.pokemongohub.net/move/"
        
        self.logger.info(f"Trying moves with IDs from 1 to {MAX_MOVE_ID}")
        
        # Générer des requêtes pour chaque ID possible de move
        for move_id in range(1, MAX_MOVE_ID + 1):
            move_url = f"{base_url}{move_id}"
            self.logger.info(f"Scheduling request for move ID: {move_id}")
            yield SplashRequest(
                move_url,
                self.parse_move,
                args={
                    'wait': 2,
                    'timeout': 90,
                    'resource_timeout': 20,
                },
                # Retry policy for 404s
                errback=self.handle_error,
                meta={'move_id': move_id}
            )
    
    def handle_error(self, failure):
        """
        Gère les erreurs lors des requêtes, notamment les 404 (move non trouvé)
        """
        move_id = failure.request.meta.get('move_id')
        self.logger.info(f"Move ID {move_id} not found (404 or other error)")

    def parse_move(self, response):
        """
        Parse individual move page to extract all data
        """
        # Vérifier si la page existe et contient un move
        if response.css('h1.Card_cardTitle__URr_A::text').get() is None:
            self.logger.info(f"Skipping ID {response.meta.get('move_id')} - not a valid move page")
            return
        
        # Vérifier si c'est un move rapide (si non, on ignore)
        move_category = response.css('tr:contains("Category") td::text').get()
        if move_category and "fast" not in move_category.lower():
            self.logger.info(f"Skipping ID {response.meta.get('move_id')} - not a fast move")
            return
        
        move = MoveItem()
        
        # Extract move ID from URL
        move['id'] = str(response.meta.get('move_id'))
        
        # Extract move name
        name = response.css('h1.Card_cardTitle__URr_A::text').get()
        if name:
            move['name'] = name.strip()
        
        # Extract move type
        move_type = response.css('tr:contains("Type") td span::text').get()
        if not move_type:
            # Backup: try to get from the type image
            move_type = response.css('figure img::attr(title)').get()
        if move_type:
            move['type'] = move_type.strip()
        
        # Set move category
        move['is_fast'] = True
        move['is_charged'] = False
        
        # Extract Raid/Gym stats
        stats_section = response.css('section:contains("Gym and Raid Battles")')
        
        # Extract base power
        power = stats_section.css('tr:contains("Power") td::text').get()
        if power:
            try:
                move['power'] = int(power.strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert power to int: {power}")
        
        # Extract energy
        energy = stats_section.css('tr:contains("Energy") td::text').get()
        if energy:
            try:
                move['energy'] = int(energy.strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert energy to int: {energy}")
        
        # Extract animation duration
        duration = stats_section.css('tr:contains("Animation Duration") td::text').get()
        if duration:
            try:
                move['animation_duration'] = float(duration.strip().replace('s', ''))
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert duration to float: {duration}")
        
        # Extract damage window
        damage_window = stats_section.css('tr:contains("Damage Window") td::text').get()
        if damage_window:
            move['damage_window'] = damage_window.strip()
        
        # Extract DPS
        dps = stats_section.css('tr:contains("DPS") td::text').get()
        if dps:
            try:
                move['dps'] = float(dps.split()[0])  # Get first number before "Damage per second"
            except (ValueError, TypeError, IndexError):
                self.logger.warning(f"Could not convert DPS to float: {dps}")
        
        # Extract DPE
        dpe = stats_section.css('tr:contains("DPE") td::text').get()
        if dpe:
            try:
                move['dpe'] = float(dpe.split()[0])  # Get first number before "Damage per Energy"
            except (ValueError, TypeError, IndexError):
                self.logger.warning(f"Could not convert DPE to float: {dpe}")
        
        # Extract PVP stats
        pvp_section = response.css('section:contains("Trainer Battles")')
        
        # Set PVP flag
        move['is_pvp'] = True
        
        # PVP power
        pvp_power = pvp_section.css('tr:contains("Power") td::text').get()
        if pvp_power:
            try:
                move['pvp_power'] = int(pvp_power.strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert PVP power to int: {pvp_power}")
        
        # PVP energy
        pvp_energy = pvp_section.css('tr:contains("Energy") td::text').get()
        if pvp_energy:
            try:
                move['pvp_energy'] = int(pvp_energy.strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert PVP energy to int: {pvp_energy}")
        
        # PVP duration
        pvp_duration = pvp_section.css('tr:contains("Duration") td::text').get()
        if pvp_duration:
            # Pour les fast moves, la durée est en secondes
            try:
                move['pvp_duration'] = float(pvp_duration.replace('s', '').strip())
            except (ValueError, TypeError):
                self.logger.warning(f"Could not convert PVP duration to float: {pvp_duration}")
        
        # PVP DPS
        pvp_dps = pvp_section.css('tr:contains("DPS") td::text').get()
        if pvp_dps:
            try:
                move['pvp_dps'] = float(pvp_dps.split()[0])  # Get first number before "Damage per second"
            except (ValueError, TypeError, IndexError):
                self.logger.warning(f"Could not convert PVP DPS to float: {pvp_dps}")
        
        # PVP DPE
        pvp_dpe = pvp_section.css('tr:contains("DPE") td::text').get()
        if pvp_dpe:
            try:
                move['pvp_dpe'] = float(pvp_dpe.split()[0])  # Get first number before "Damage per Energy"
            except (ValueError, TypeError, IndexError):
                self.logger.warning(f"Could not convert PVP DPE to float: {pvp_dpe}")
        
        # Extract tags
        tags = pvp_section.css('tr:contains("Tags") td::text').get()
        if tags:
            move['tags'] = [tag.strip() for tag in tags.split(',')]
        
        # Extract Pokémon that can learn this move
        pokemon_with_move = response.css('ul.MoveInfo_pokemonList__ZJB1N li a::text').getall()
        if pokemon_with_move:
            move['pokemon_with_move'] = [p.strip() for p in pokemon_with_move]
        
        self.logger.info(f"Scraped Fast Move: {move.get('name')} (ID: {move.get('id')})")
        
        time.sleep(0.2)  # Small delay between requests
        yield move 