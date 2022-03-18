# Scrapy settings for sitemapgen project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'sitemapgen'

SPIDER_MODULES = ['sitemapgen.spiders']
NEWSPIDER_MODULE = 'sitemapgen.spiders'

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'sitemapgen.pipelines.SitemapgenPipeline': 500,
}