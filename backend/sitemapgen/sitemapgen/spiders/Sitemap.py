import scrapy
from pathlib import Path
from collections import defaultdict
from scrapy.linkextractors import LinkExtractor
from scrapy.exporters import XmlItemExporter
from scrapy.spiders import CrawlSpider, Rule


class SitemapSpider(CrawlSpider):
    name = 'Sitemap'
    rules = (Rule(LinkExtractor(), callback='parse_item', follow=True),)

    def __init__(self, domain, depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain = domain
        self.rootdir = Path(f"SITEMAP_{self.domain}")
        self.rootdir.mkdir(parents=True)
        self.depth = int(depth)
        self.allowed_domains = [domain]
        self.start_urls = [f'http://{domain}/']

    def parse_item(self, response):
        url = response.url.rstrip('/')
        url_parts = url.split(self.domain,1)[1].split("/", self.depth)[1:]

        return {
            'loc' : url,
            'parent_directory' : self.rootdir /  "/".join(url_parts[:-1]),
            'filename' : url_parts[-1] if url_parts else 'index.html'
        }

    class SitemapgenPipeline:
        def open_spider(self, spider):
            self.exporters = {}
            indexpath = spider.rootdir / "sitemap_index.xml"
            self.indexexporter = XmlItemExporter(
                indexpath.open(mode='w'),
                root_element='sitemapindex',
                item_element='sitemap'
            )
            self.indexexporter.start_exporting()

        def _new_exporter(self, parent):
            parent.mkdir(parents=True, exist_ok=True)
            path = parent / 'sitemap.xml'
            exporter = XmlItemExporter(
                path.open(mode='w'),
                root_element='urlset',
                item_element='url'
            )
            exporter.start_exporting()
            self.indexexporter.export_item({'loc': str(path)})
            return exporter

        def process_item(self, item, spider):
            if item['parent_directory'] not in self.exporters:
                self.exporters[item['parent_directory']] = self._new_exporter(item['parent_directory'])

            self.exporters[item['parent_directory']].export_item(
                {
                    'loc' : item['loc'],
                    'lastmod' : 'TBA',
                    'changefreq' : 'monthly',
                    'priority' : '0.5'
                }
            )
            return item

    custom_settings = {'ITEM_PIPELINES' : {SitemapgenPipeline : 500}}