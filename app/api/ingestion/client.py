import requests
import ujson
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Generator, Tuple
from app.models.enums.pokeapi import EndPoint
from functools import partial
from app.db.engine import Engine


class PokeApiClient:
    """ Client to interact with the PokeAPI. """
    
    BASE_URL = "https://pokeapi.co/api/v2/"
    
    def __init__(self, base_url: str = None, timeout: int = 30, rate_limit_delay: float = 1.0):
        """ Initialize the PokeAPI client.
        Args:
            base_url: Optional base URL, uses BASE_URL by default
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between API calls in seconds """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.logger = logging.getLogger(__name__)
    
    def call(self, endpoint: EndPoint, resource_id: Optional[str] = None, 
             limit: Optional[int] = None, offset: Optional[int] = None,
             params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """ Generic method to call the API
        Args:
            endpoint: The API endpoint (type, pokemon, etc.)
            resource_id: Optional specific resource identifier
            limit: Maximum number of items to retrieve
            offset: Pagination offset
            params: Additional request parameters
            
        Returns:
            The API response data as dict """
        url = f"{self.base_url}{endpoint.value}"
        if resource_id:
            url = f"{url}/{resource_id}"
        
        request_params = params or {}
        if limit is not None:
            request_params["limit"] = limit
        if offset is not None:
            request_params["offset"] = offset
        # build request params
        
        self.logger.info(f"API call: {url} with params: {request_params}")
        
        try:
            response = requests.get(url, params=request_params, timeout=self.timeout)
            response.raise_for_status()
            return ujson.loads(response.text)
        # fetch API data
        
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            raise
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise
        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout: {e}")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise
        # handle request errors
    
    def get_all_items(self, endpoint: EndPoint) -> List[Dict[str, Any]]:
        """ Get all items from an endpoint with pagination
        Args:
            endpoint: The API endpoint to retrieve items from
            
        Returns:
            List of all items from the endpoint """
        response = self.call(endpoint, limit=1)
        total_count = response.get("count", 0)
        
        self.logger.info(f"Retrieving all {total_count} items from {endpoint.value}")
        return self.call(endpoint, limit=total_count).get("results", [])
        # fetch all items at once
    
    def get_items_generator(self, endpoint: EndPoint, batch_size: int = 20) -> Generator[Tuple[int, Dict[str, Any]], None, None]:
        """ Generate items one by one with their index, handling rate limiting
        Args:
            endpoint: The API endpoint to retrieve items from
            batch_size: Number of items to request in each batch
            
        Returns:
            Generator yielding (index, item_data) tuples """
        all_items = self.get_all_items(endpoint)
        
        for i, item_info in enumerate(all_items, 1):
            resource_id = str(i)
            self.logger.info(f"Fetching details for {endpoint.value} {resource_id}")
            
            item_data = self.call(endpoint, resource_id=resource_id)
            yield i, item_data
            
            time.sleep(self.rate_limit_delay)
        # yield items one by one with rate limiting
    
    @staticmethod
    def batch_ingest(items_generator: Generator[Tuple[int, Dict[str, Any]], None, None], 
                    engine: Engine, process_function: Callable, 
                    batch_size: int = 100, db_name: str = "test.db"):
        """ Static utility method to ingest items in batches
        Args:
            items_generator: Generator providing (index, item_data) tuples
            engine: Database engine
            process_function: Function to process each item before ingestion
            batch_size: Size of batches for committing to database
            db_name: Database name """
        logger = logging.getLogger(__name__)
        logger.info(f"Starting batch ingestion with batch size {batch_size}")
        
        with engine.connect(db_name=db_name) as session:
            batch_count = 0
            item_count = 0
            
            for i, item_data in items_generator:
                try:
                    db_object = process_function(item_data)
                    session.add(db_object)
                    # process item 
                    
                    item_count += 1
                    batch_count += 1
                    
                    if batch_count >= batch_size:
                        session.commit()
                        logger.info(f"Committed batch of {batch_count} items")
                        batch_count = 0
                    # batch commit
                        
                except Exception as e:
                    logger.error(f"Error processing item {i}: {e}")
            
            if batch_count > 0:
                session.commit()
                logger.info(f"Committed final batch of {batch_count} items")
            # commit remaining items
                
            logger.info(f"Ingestion completed. {item_count} items processed.")
        # process in batches, periodic commits