import logging
import random
from time import sleep
from random import choice
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlparse
from crosslinked.logger import Log
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

csv = logging.getLogger('cLinked_csv')


class CrossLinked:
    def __init__(self, search_engine, target, timeout, clicks, conn_timeout=3, proxies=[], jitter=0):
        self.results = []
        self.url = {'duckduckgo': 'https://www.ddg.gg/?q=site:linkedin.com/in+"{}"',
                    'google': 'https://www.google.com/search?q=site:linkedin.com/in+"{}"&start={}'}

        self.runtime = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
        self.search_engine = search_engine
        self.conn_timeout = conn_timeout
        self.timeout = timeout
        self.proxies = proxies
        self.target = target
        self.jitter = jitter
        self.clicks = clicks


    def get_agent(self):
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:126.0) Gecko/20100101 Firefox/126.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        ]

        random_agent = (random.choice(user_agents))

        return random_agent


    def page_parser(self, source_code):
        soup = BeautifulSoup(source_code, 'lxml')
        links = soup.findAll('a')

        for link in links:
            try:
                url = str(link.get('href')).lower()   
                domain = urlparse(url).netloc

                if "linkedin.com" in domain:
                    data = self.link_parser(url, link)
                    self.log_results(data) if data['name'] else False
            except Exception as e:
                Log.warn('Failed Parsing: {}- {}'.format(link.get('href'), e))


    def search(self):
        attempt = 0

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, proxy=get_proxy(self.proxies))
            context = browser.new_context(user_agent=self.get_agent(), ignore_https_errors=True)
            page = context.new_page()

            url = self.url[self.search_engine].format(self.target, attempt)

            response = page.goto(url)

            page.wait_for_load_state("networkidle")

            page.pause()

            while self.clicks != attempt:
                
                try: 
                    if self.search_engine == 'duckduckgo':
                        page.click('#more-results')
                        page.wait_for_load_state("networkidle")

                    if self.search_engine == 'google':
                        page.click('a[aria-label="Page %s"]' % (attempt+2)) 
                        page.wait_for_load_state("networkidle")

                    http_code = response.status

                    if http_code != 200:
                        Log.info("{:<3} {} ({})".format(len(self.results), url, http_code))
                        Log.warn('None 200 response, exiting search ({})'.format(http_code))
                        break

                    self.page_parser(page.content())
                    Log.info("{:<3} {} ({})".format(len(self.results), url, http_code))

                    attempt+=1
                    sleep(self.jitter)
                except KeyboardInterrupt:
                    Log.warn("Key event detected, exiting search...")
                    break

            browser.close()

        return self.results


    def link_parser(self, url, link):
        u = {'url': url}
        u['text'] = unidecode(link.text.split("|")[0].split("...")[0])  # Capture link text before trailing chars
        u['title'] = self.parse_linkedin_title(u['text'])               # Extract job title
        u['name'] = self.parse_linkedin_name(u['text'])                 # Extract whole name
        return u


    def parse_linkedin_title(self, data):
        try:
            title = data.split("-")[1].split('https:')[0]
            return title.split("...")[0].split("|")[0].strip()
        except:
            return 'N/A'


    def parse_linkedin_name(self, data):
        try:
            name = data.split("-")[0].strip()
            return unidecode(name).lower()
        except:
            return False


    def log_results(self, d):
        # Prevent Duplicates & non-standard responses (i.e: "<span>linkedin.com</span></a>")
        if d in self.results:
            return
        elif 'linkedin.com' in d['name']:
            return

        self.results.append(d)
        # Search results are logged to names.csv but names.txt is not generated until end to prevent duplicates
        logging.debug('name: {:25} RawTxt: {}'.format(d['name'], d['text']))
        csv.info('"{}","{}","{}","{}","{}","{}",'.format(self.runtime, self.search_engine, d['name'], d['title'], d['url'], d['text']))


def get_proxy(proxies):
    if not proxies:
        return None
    
    if not isinstance(proxies, list):
        return {'server': proxies}
    else:
        proxy = choice(proxies)
        return {"server": proxy} 