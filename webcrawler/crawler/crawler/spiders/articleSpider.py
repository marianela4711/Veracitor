

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from crawler.xpaths import Xpaths
from crawler.items import ArticleItem



class ArticleSpider(BaseSpider):
    name = "article"
    allowed_domains = ["dn.se"]
    start_urls = [
        "http://www.dn.se/nyheter/sverige/abdullah-och-aqilah-fran-irak-lever-pa-en-tusenlapp-var",
        "http://www.dn.se/nyheter/vetenskap/kristall-lik-solsten-funnen-pa-medeltida-skepp",
        "http://www.dn.se/kultur-noje/dn-medarbetare-tar-plats-i-svenska-akademien",
        "http://www.dn.se/kultur-noje/film-tv/harrison-ford-med-i-nya-anchorman"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        xpaths = Xpaths('/home/jonathan/Veracitor/webcrawler/crawler/crawler/webpages.xml')
        article = ArticleItem()
        
        for xpath in xpaths.get_title_xpaths("dn.se"):
            article["title"] = hxs.select(xpath).extract()
            break
        
        for xpath in xpaths.get_author_xpaths("dn.se"):
            article["author"] = hxs.select(xpath).extract()
            break
            
        for xpath in xpaths.get_date_xpaths("dn.se"):
            article["date"] = hxs.select(xpath).extract()
            break
            
        for xpath in xpaths.get_summary_xpaths("dn.se"):
            article["summary"] = hxs.select(xpath).extract()
            break
            
        return article
        