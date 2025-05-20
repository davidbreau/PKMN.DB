# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class PkmndbSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn't have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class PkmndbDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        if not isinstance(request, SplashRequest):
            request.meta['splash'] = {
                'args': {
                    'wait': 2,  # Wait for JavaScript to execute
                    'timeout': 90,
                    'resource_timeout': 20,
                },
                'endpoint': 'render.html',
            }
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class JavaScriptMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def process_request(self, request, spider):
        if not isinstance(request, SplashRequest):
            # Configure default Splash parameters for all requests that aren't already SplashRequests
            request.meta['splash'] = {
                'args': {
                    'wait': 3,  # Wait for JavaScript to execute (increased from 2)
                    'timeout': 90,
                    'resource_timeout': 20,
                    'images': 0,  # Don't load images to speed up rendering
                    'render_all': 1,  # Render the full page, including content outside the viewport
                    'http_method': request.method,
                    'js_enabled': True,  # Make sure JavaScript is enabled
                },
                'endpoint': 'render.html',
            }
            
            # Add headers for better compatibility
            if 'User-Agent' not in request.headers:
                request.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            
        return None
    
    def process_response(self, request, response, spider):
        # Handle response from Splash
        if 'splash' in request.meta and hasattr(response, 'data'):
            # Extract the HTML from the Splash response
            if isinstance(response.data, dict) and 'html' in response.data:
                # Create a new HtmlResponse with the HTML from Splash
                return HtmlResponse(
                    url=response.url,
                    status=response.status,
                    headers=response.headers,
                    body=response.data['html'].encode('utf-8'),
                    request=request,
                    encoding='utf-8'
                )
        return response
