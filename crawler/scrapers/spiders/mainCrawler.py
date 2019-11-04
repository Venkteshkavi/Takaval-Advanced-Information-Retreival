import scrapy
import datetime
import csv
import os
import pandas
from googletrans import Translator
from google.cloud import translate
from html.parser import HTMLParser

translator = Translator()
translate_client = translate.Client()

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

#The Times of India Index Crawler
class toicSpider(scrapy.Spider):
    name = "toicSpider"
    indexCounter = 0
    titleDict = dict()

    def start_requests(self):
        url = 'https://timesofindia.indiatimes.com/topic'
        search = getattr(self, 'search', None)
        if search is not None:
            url += '/' + search
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        baseUrl = "https://timesofindia.indiatimes.com"
        SET_SELECTOR = "li.article"
        fromDate = getattr(self, 'from', None)
        toDate = getattr(self, 'to', None)
        limit = getattr(self, 'limit', None)
        toDateObj = None
        fromDateObj = None
        flag = 0
        if toDate is not None:
            toDateObj = datetime.datetime.strptime(toDate, "%Y-%m-%d")
        if fromDate is not None:
            fromDateObj = datetime.datetime.strptime(fromDate, "%Y-%m-%d")
        for article in response.css(SET_SELECTOR):
            TITLE_SELECTOR = ".content .title ::text"
            URL_SELECTOR = ".content a ::attr(href)"
            DATE_SELECTOR = ".content a .meta ::attr(rodate)"
            articleTitle = article.css(TITLE_SELECTOR).extract_first().strip()
            if articleTitle in self.titleDict:
                continue
            else:
                self.titleDict[articleTitle] = True
            if not article.css(DATE_SELECTOR):
                DATE_SELECTOR = ".content a .meta ::text"
                publisedDate = article.css(DATE_SELECTOR).extract_first()
                dateObj = datetime.datetime.strptime(article.css(DATE_SELECTOR).extract_first(), "%d %b %Y")
            else:
                dateObj = datetime.datetime.strptime(article.css(DATE_SELECTOR).extract_first(), "%Y-%m-%dT%H:%M:%SZ")
                publisedDate = dateObj.strftime("%d %b %Y")
            if toDateObj is not None and fromDateObj is not None:
                if dateObj > toDateObj or dateObj < fromDateObj:
                    continue
            data = {
                "og_title": strip_tags(article.css(TITLE_SELECTOR).extract_first().strip()),
                "title": strip_tags(article.css(TITLE_SELECTOR).extract_first().strip()),
                "lang": "en",
                "url": baseUrl+article.css(URL_SELECTOR).extract_first(),
                "publishedDate": publisedDate,
                "dateObject": dateObj
            }
            if limit is not None and self.indexCounter >= int(limit):
                return
            self.indexCounter += 1
            yield data

        NEXT_PAGE_SELECTOR = '.pagination a#raquo ::attr(href)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                callback=self.parse
            )

#The Times of India Article Crawler
class toicArticleSpider(scrapy.Spider):
    name = "toicArticleSpider"
    def start_requests(self):
        csvColumns = ["og_title","title", "lang", "url", "publishedDate", "dateObject"]
        filename = getattr(self, 'filename', None)
        if filename is not None:
            data = pandas.read_csv(filename, names=csvColumns)
            start_urls = data.url.tolist()[1:]
            og_title = data.og_title.tolist()[1:]
            title = data.title.tolist()[1:]
            pub_date = data.publishedDate.tolist()[1:]
            date_obj = data.dateObject.tolist()[1:]
        for url, otitle, title, pubdate, dateobj in zip(start_urls, og_title, title, pub_date, date_obj):
            yield scrapy.Request(url, self.parse, meta={'title':title,'otitle':otitle,'pubdate':pubdate,'dateobj':dateobj})

    def parse(self, response):
        baseUrl = "https://timesofindia.indiatimes.com"
        # TITLE_SELECTOR = ".K55Ut ::text"
        CONTENT = "._3WlLe *::text"
        story = ""
        for c in response.css(CONTENT):
            if c.get().strip() == "#ElectionsWithTimes" or c.get().strip() == "Download The Times of India":
                break
            story += c.get().strip()
            story += " "
        data = {
            "title": response.meta['title'],
            "og_title": response.meta['otitle'],
            "url": response.url,
            "lang": "en",
            "content": story,
            "publishedDate": response.meta['pubdate'],
            "dateObject": response.meta['dateobj']
        }
        yield data

#The Hindu Index Crawler
class thcSpider(scrapy.Spider):
    name = "thcSpider"
    url = 'https://www.thehindu.com/search/?q='
    indexCounter = 0
    titleDict = dict()

    def start_requests(self):
        self.url = 'https://www.thehindu.com/search/?q='
        search = getattr(self, 'search', None)
        if search is not None:
            self.url += search+'&order=DESC&sort=publishdate&ct=text'
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        baseUrl = "https://www.thehindu.com"
        SET_SELECTOR = ".story-card"
        curl = response.url
        fromDate = getattr(self, 'from', None)
        toDate = getattr(self, 'to', None)
        limit = getattr(self, 'limit', None)
        toDateObj = None
        fromDateObj = None
        flag = 0
        if toDate is not None:
            toDateObj = datetime.datetime.strptime(toDate, "%Y-%m-%d")
        if fromDate is not None:
            fromDateObj = datetime.datetime.strptime(fromDate, "%Y-%m-%d")
        for article in response.css(SET_SELECTOR):
            TITLE_SELECTOR = "a.story-card75x1-text ::text"
            URL_SELECTOR = "a.story-card75x1-text ::attr(href)"
            DATE_SELECTOR = ".dateline ::text"
            articleTitle = article.css(TITLE_SELECTOR).extract_first().strip()
            if articleTitle in self.titleDict:
                continue
            else:
                self.titleDict[articleTitle] = True
            dateObj = datetime.datetime.strptime(article.css(DATE_SELECTOR).extract_first().strip(), "%B %d, %Y")
            if toDateObj is not None and fromDateObj is not None:
                if dateObj <= toDateObj:
                    flag = 1
                else:
                    continue
                if fromDateObj > dateObj and flag == 1:
                    print('#######BREAK##########')
                    return 
            publisedDate = dateObj.strftime("%d %b %Y")
            data = {
                "title": article.css(TITLE_SELECTOR).extract_first().strip(),
                "url": article.css(URL_SELECTOR).extract_first(),
                "publishedDate": publisedDate,
                "dateObject": dateObj
            }
            if limit is not None and self.indexCounter >= int(limit):
                return
            self.indexCounter += 1
            yield data

        NEXT_PAGE_SELECTOR = '.next a.page-link ::attr(data-page-no)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        next_page_url = self.url+"&page="+next_page
        if next_page_url:
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse
            )

#The Hindu Article Crawler
class thcArticleSpider(scrapy.Spider):
    name = "thcArticleSpider"
    def start_requests(self):
        csvColumns = ["title", "url", "publishedDate", "dateObject"]
        filename = getattr(self, 'filename', None)
        if filename is not None:
            data = pandas.read_csv(filename, names=csvColumns)
            start_urls = data.url.tolist()[1:]
        for url in start_urls:
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        baseUrl = "https://www.thehindu.com"
        articleId = response.css(".articlepage ::attr(data-artid)").extract_first()
        TITLE_SELECTOR = ".article h1.title ::text"
        KEYWORDS = ".article h2.intro ::text"
        IMG = ".article .lead-img-cont picture img ::attr(src)"
        CONTENT = ".article #content-body-14269002-"+articleId+" *::text"
        story = ""
        for c in response.css(CONTENT):
            story += c.get().strip()
        data = {
            "title": response.css(TITLE_SELECTOR).extract_first().strip(),
            "url": response.url,
            "keywords": response.css(KEYWORDS).extract_first(),
            "imageUrl": response.css(IMG).extract_first(),
            "content": story
        }
        yield data

#The NDTV Index Crawler
class ndtvcSpider(scrapy.Spider):
    name = "ndtvcSpider"
    pageno = 1
    url = 'https://www.ndtv.com/page/topic-load-more?type=news&query='
    indexCounter = 0
    titleDict = dict()

    def start_requests(self):
        url = 'https://www.ndtv.com/page/topic-load-more?type=news&query='
        search = getattr(self, 'search', None)
        if search is not None:
            self.url += search+"&page="+str(self.pageno)
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        baseUrl = "https://www.ndtv.com"
        SET_SELECTOR = "ul li"
        curl = response.url
        fromDate = getattr(self, 'from', None)
        toDate = getattr(self, 'to', None)
        limit = getattr(self, 'limit', None)
        toDateObj = None
        fromDateObj = None
        flag = 0
        if toDate is not None:
            toDateObj = datetime.datetime.strptime(toDate, "%Y-%m-%d")
        if fromDate is not None:
            fromDateObj = datetime.datetime.strptime(fromDate, "%Y-%m-%d")
        for article in response.css(SET_SELECTOR):
            TITLE_SELECTOR = "p.header a ::attr(title)"
            URL_SELECTOR = "p.header a ::attr(href)"
            DATE_SELECTOR = "p.list_dateline ::text"
            articleTitle = article.css(TITLE_SELECTOR).extract_first().strip()
            if articleTitle in self.titleDict:
                continue
            else:
                self.titleDict[articleTitle] = True
            if len(article.css(DATE_SELECTOR).extract()) > 1:
                dateStr = article.css(DATE_SELECTOR).extract()[1].strip().split("|")[-1].strip()
            else:
                dateStr = article.css(DATE_SELECTOR).extract()[0].strip().split("|")[-1].strip()
            dateObj = datetime.datetime.strptime(dateStr, "%A %B %d, %Y")
            # if toDateObj is not None and fromDateObj is not None:
            #     if dateObj <= toDateObj:
            #         flag = 1
            #     else:
            #         continue
            #     if fromDateObj > dateObj and flag == 1:
            #         print('#######BREAK##########')
            #         return
            if toDateObj is not None and fromDateObj is not None:
                if dateObj > toDateObj or dateObj < fromDateObj:
                    continue 
            publisedDate = dateObj.strftime("%d %b %Y")
            data = {
                "og_title": strip_tags(article.css(TITLE_SELECTOR).extract_first().strip()),
                "title": strip_tags(article.css(TITLE_SELECTOR).extract_first().strip()),
                "lang": "en",
                "url": article.css(URL_SELECTOR).extract_first(),
                "publishedDate": publisedDate,
                "dateObject": dateObj
            }
            if limit is not None and self.indexCounter >= int(limit):
                return
            self.indexCounter += 1
            yield data

        self.pageno += 1
        next_page_url = self.url[:-1]+str(self.pageno)
        if next_page_url:
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse
            )

#The NDTV Article Crawler
class ndtvcArticleSpider(scrapy.Spider):
    name = "ndtvcArticleSpider"
    def start_requests(self):
        csvColumns = ["og_title","title", "lang", "url", "publishedDate", "dateObject"]
        filename = getattr(self, 'filename', None)
        if filename is not None:
            data = pandas.read_csv(filename, names=csvColumns)
            start_urls = data.url.tolist()[1:]
            og_title = data.og_title.tolist()[1:]
            title = data.title.tolist()[1:]
            pub_date = data.publishedDate.tolist()[1:]
            date_obj = data.dateObject.tolist()[1:]
        for url, otitle, title, pubdate, dateobj in zip(start_urls, og_title, title, pub_date, date_obj):
            yield scrapy.Request(url, self.parse, meta={'title':title,'otitle':otitle,'pubdate':pubdate,'dateobj':dateobj})

    def parse(self, response):
        baseUrl = "https://www.ndtv.com"
        # TITLE_SELECTOR = ".ins_headline h1 span ::text"
        CONTENT = ".ins_storybody#ins_storybody p *::text"
        story = ""
        for c in response.css(CONTENT):
            if c.css('#blog_temp_content'):
                continue
            story += c.get().strip()
            story += " "
        data = {
            "title": response.meta['title'],#response.css(TITLE_SELECTOR).extract_first().strip()
            "og_title": response.meta['otitle'],
            "url": response.url,
            "lang": "en",
            "content": story,
            "publishedDate": response.meta['pubdate'],
            "dateObject": response.meta['dateobj']
        }
        yield data

#The Detik 
class detikcSpider(scrapy.Spider):
    name = "detikcSpider"
    pageno = 1
    url = 'https://www.detik.com/search/searchall?query='
    indexCounter = 0
    titleDict = dict()

    def start_requests(self):
        url = 'https://www.detik.com/search/searchall?query='
        search = getattr(self, 'search', None)
        if search is not None:
            self.url += search+"&siteid=2&sortby=time&page="+str(self.pageno)
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        SET_SELECTOR = "div.list > article"
        curl = response.url
        fromDate = getattr(self, 'from', None)
        toDate = getattr(self, 'to', None)
        limit = getattr(self, 'limit', None)
        toDateObj = None
        fromDateObj = None
        flag = 0
        if toDate is not None:
            toDateObj = datetime.datetime.strptime(toDate, "%Y-%m-%d")
        if fromDate is not None:
            fromDateObj = datetime.datetime.strptime(fromDate, "%Y-%m-%d")
        for article in response.css(SET_SELECTOR):
            if article.css('.video_tag') or article.css('.foto_tag'):
                continue
            else:
                TITLE_SELECTOR = "h2.title ::text"
                URL_SELECTOR = "a ::attr(href)"
                DATE_SELECTOR = ".date ::text"
                articleTitle = article.css(TITLE_SELECTOR).extract_first().strip()
                if articleTitle in self.titleDict:
                    continue
                else:
                    self.titleDict[articleTitle] = True
                dateStr = " ".join(article.css(DATE_SELECTOR).extract()[1].strip().split(" ")[1:-1]).strip()
                try:
                    dateObj = datetime.datetime.strptime(dateStr, "%d %b %Y %H:%M")
                except:
                    continue
                if toDateObj is not None and fromDateObj is not None:
                    if dateObj <= toDateObj:
                        flag = 1
                    else:
                        continue
                    if fromDateObj > dateObj and flag == 1:
                        print('#######BREAK##########')
                        return 
                publisedDate = dateObj.strftime("%d %b %Y")
                data = {
                    "og_title": article.css(TITLE_SELECTOR).extract_first().strip(),
                    "title": translate_client.translate(article.css(TITLE_SELECTOR).extract_first())['translatedText'],
                    # "title": translator.translate(article.css(TITLE_SELECTOR).extract_first().strip()).text,
                    "lang": "id",
                    "url": article.css(URL_SELECTOR).extract_first(),
                    "publishedDate": publisedDate,
                    "dateObject": dateObj
                }
                if limit is not None and self.indexCounter >= int(limit):
                    return
                self.indexCounter += 1
            yield data
        self.pageno += 1
        next_page_url = self.url[:-1]+str(self.pageno)
        if next_page_url:
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse
            )

#Detic Article Crawler
class detikcArticleSpider(scrapy.Spider):
    name = "detikcArticleSpider"
    def start_requests(self):
        csvColumns = ["og_title","title", "lang", "url", "publishedDate", "dateObject"]
        filename = getattr(self, 'filename', None)
        if filename is not None:
            data = pandas.read_csv(filename, names=csvColumns)
            start_urls = data.url.tolist()[1:]
            og_title = data.og_title.tolist()[1:]
            title = data.title.tolist()[1:]
            pub_date = data.publishedDate.tolist()[1:]
            date_obj = data.dateObject.tolist()[1:]
        for url, otitle, title, pubdate, dateobj in zip(start_urls, og_title, title, pub_date, date_obj):
            yield scrapy.Request(url, self.parse, meta={'title':title,'otitle':otitle,'pubdate':pubdate,'dateobj':dateobj})

    def parse(self, response):
        baseUrl = "https://news.detik.com"
        # TITLE_SELECTOR = "article .jdl h1 ::text"
        # IMG = ".pic_artikel img ::attr(src)"
        CONTENT = "article .detail_wrap #detikdetailtext *::text"
        story = ""
        for c in response.css(CONTENT):
            if c.css('.linksisip'):
                continue
            story += c.get().strip()
            story += " "
        data = {
            "title": response.meta['title'],
            "og_title": response.meta['otitle'],
            "url": response.url,
            "lang": "id",
            "content": translate_client.translate(story.strip())['translatedText'],#translator.translate(story.strip()).text
            "publishedDate": response.meta['pubdate'],
            "dateObject": response.meta['dateobj']
        }
        yield data


class bangpcSpider(scrapy.Spider):
    name = "bangpcSpider"
    url = 'http://search.bangkokpost.com/search/result?q=riot&category=all&refinementFilter=&sort=newest'
    def start_requests(self):
        self.url = 'http://search.bangkokpost.com/search/result?q='
        search = getattr(self, 'search', None)
        if search is not None:
            self.url += search+'&category=all&refinementFilter=&sort=newest'
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        baseUrl = "https://www.bangkokpost.com"
        SET_SELECTOR = "ul.SearchList li"
        curl = response.url
        for article in response.css(SET_SELECTOR):
            TITLE_SELECTOR = "a.story-card75x1-text ::text"
            URL_SELECTOR = "a.story-card75x1-text ::attr(href)"
            DATE_SELECTOR = ".dateline ::text"
            dateObj = datetime.datetime.strptime(article.css(DATE_SELECTOR).extract_first().strip(), "%B %d, %Y")
            publisedDate = dateObj.strftime("%d %b %Y")
            data = {
                "title": article.css(TITLE_SELECTOR).extract_first(),
                "url": article.css(URL_SELECTOR).extract_first(),
                "publishedDate": publisedDate,
                "dateObject": dateObj
            }
            yield data

        NEXT_PAGE_SELECTOR = '.next a.page-link ::attr(data-page-no)'
        next_page = response.css(NEXT_PAGE_SELECTOR).extract_first()
        next_page_url = self.url+"&page="+next_page
        if next_page_url:
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse
            )


class indiaNewsTimes(scrapy.Spider):
    name = "indiaNewsTimes"
    indexCounter = 0
    titleDict = dict()
    pageno = 1
    url = 'https://timesofindia.indiatimes.com/india'

    def start_requests(self):
        url = 'https://timesofindia.indiatimes.com/india'
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        baseUrl = "https://timesofindia.indiatimes.com"
        SET_SELECTOR = "#c_wdt_list_1 ul li"
        fromDate = getattr(self, 'from', None)
        toDate = getattr(self, 'to', None)
        limit = getattr(self, 'limit', None)
        toDateObj = None
        fromDateObj = None
        flag = 0
        if toDate is not None:
            toDateObj = datetime.datetime.strptime(toDate, "%Y-%m-%d")
        if fromDate is not None:
            fromDateObj = datetime.datetime.strptime(fromDate, "%Y-%m-%d")
        for article in response.css(SET_SELECTOR):
            TITLE_SELECTOR = ".w_tle a::attr(title)"
            URL_SELECTOR = ".w_tle a::attr(href)"
            DATE_SELECTOR = ".w_bylinec .strlastupd::attr(rodate)"
            try:
                articleTitle = article.css(TITLE_SELECTOR).extract_first().strip()
            except:
                continue
            if articleTitle in self.titleDict:
                continue
            else:
                self.titleDict[articleTitle] = True
            if not article.css(DATE_SELECTOR):
                DATE_SELECTOR = ".content a .meta ::text"
                publisedDate = article.css(DATE_SELECTOR).extract_first()
                dateObj = datetime.datetime.strptime(article.css(DATE_SELECTOR).extract_first(), "%d %b %Y")
            else:
                dateObj = datetime.datetime.strptime(article.css(DATE_SELECTOR).extract_first(), "%d %b %Y, %H:%M")
                publisedDate = dateObj.strftime("%d %b %Y")
            if toDateObj is not None and fromDateObj is not None:
                if dateObj > toDateObj or dateObj < fromDateObj:
                    continue
            data = {
                "title": article.css(TITLE_SELECTOR).extract_first().strip(),
                "url": baseUrl+article.css(URL_SELECTOR).extract_first(),
                "publishedDate": publisedDate,
                "dateObject": dateObj
            }
            if limit is not None and self.indexCounter >= int(limit):
                return
            self.indexCounter += 1
            yield data
        self.pageno += 1
        if self.pageno >= 12:
            return
        next_page_url = self.url+"/"+str(self.pageno)
        if next_page_url:
            yield scrapy.Request(
                response.urljoin(next_page_url),
                callback=self.parse
            )