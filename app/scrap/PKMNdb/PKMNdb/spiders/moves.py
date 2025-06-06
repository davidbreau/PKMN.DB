import scrapy
from scrapy_splash import SplashRequest
import re
import time
from ..items import MoveItem


class MovesSpider(scrapy.Spider):
    name = "moves"
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

    def __init__(self, max_id=1000, *args, **kwargs):
        super(MovesSpider, self).__init__(*args, **kwargs)
        # Valeur paramétrable en ligne de commande
        self.MAX_MOVE_ID = int(max_id) if max_id else 300
        self.fast_moves_count = 0
        self.charged_moves_count = 0
        
    def start_requests(self):
        """
        Itère sur des IDs numériques croissants pour trouver les moves
        """
        base_url = "https://db.pokemongohub.net/move/"
        
        self.logger.info(f"Trying moves with IDs from 1 to {self.MAX_MOVE_ID}")
        
        # Générer des requêtes pour chaque ID possible de move
        for move_id in range(1, self.MAX_MOVE_ID + 1):
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
        
        # Déterminer le type de move (rapide ou chargé)
        move_category = response.css('tr:contains("Category") td::text').get()
        is_fast_move = move_category and "fast" in move_category.lower()
        is_charged_move = move_category and ("charged" in move_category.lower() or "charge" in move_category.lower())
        
        # Ignorer si ce n'est ni un move rapide ni un move chargé
        if not (is_fast_move or is_charged_move):
            self.logger.info(f"Skipping ID {response.meta.get('move_id')} - unknown move category: {move_category}")
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
        move['is_fast'] = is_fast_move
        move['is_charged'] = is_charged_move
        
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
        
        # PVP duration - Différent selon le type de move
        pvp_duration = pvp_section.css('tr:contains("Duration") td::text').get()
        if pvp_duration:
            try:
                if is_fast_move:
                    # Pour les fast moves, la durée est en secondes
                    move['pvp_duration'] = float(pvp_duration.replace('s', '').strip())
                else:
                    # Pour les charged moves, la durée peut être en tours (Turns) ou en secondes
                    if 'turn' in pvp_duration.lower() or 'turns' in pvp_duration.lower():
                        move['pvp_duration'] = int(pvp_duration.split()[0])  # Get number before "Turns"
                    else:
                        # Si c'est en secondes
                        move['pvp_duration'] = float(pvp_duration.replace('s', '').strip())
            except (ValueError, TypeError, IndexError):
                self.logger.warning(f"Could not convert PVP duration: {pvp_duration}")
        
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
        
        # For charged moves, extract PVP effects if any
        if is_charged_move:
            pvp_effects = pvp_section.xpath('./following-sibling::section[1]/header[contains(text(), "Effects")]/following-sibling::text()').get()
            if pvp_effects and "no special effects" not in pvp_effects.lower():
                move['pvp_effects'] = pvp_effects.strip()
        
        # Extract Pokémon that can learn this move
        pokemon_with_move = response.css('ul.MoveInfo_pokemonList__ZJB1N li a::text').getall()
        if pokemon_with_move:
            move['pokemon_with_move'] = [p.strip() for p in pokemon_with_move]
        
        # Incrémenter le compteur approprié
        if is_fast_move:
            self.fast_moves_count += 1
            self.logger.info(f"Scraped Fast Move: {move.get('name')} (ID: {move.get('id')}) - Total: {self.fast_moves_count}")
        else:
            self.charged_moves_count += 1
            self.logger.info(f"Scraped Charged Move: {move.get('name')} (ID: {move.get('id')}) - Total: {self.charged_moves_count}")
        
        time.sleep(0.2)  # Small delay between requests
        yield move
        
    def closed(self, reason):
        """Appelée quand le spider se termine"""
        self.logger.info(f"Spider closed. Stats: {self.fast_moves_count} fast moves, {self.charged_moves_count} charged moves scraped.") 