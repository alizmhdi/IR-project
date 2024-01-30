from bs4 import BeautifulSoup
import requests
import os
import re
import json

API_KEY = os.environ.get('API_KEY', 'a0ce25ec0fcff1f0a4e4af53e16162cc')

class Crawler():
    def __init__(self, prof, urls, limit=200):
        self.prof_name = prof
        self.start_queue = urls
        self.visited = set()
        self.limit = limit

    def get_page(self, URL):
        payload = {'api_key': 'a0ce25ec0fcff1f0a4e4af53e16162cc', 'url': URL.strip()}
        r = requests.get('http://api.scraperapi.com/', params=payload)
        return r.text

    def get_next_url(self):
        next_url = self.start_queue.pop(0)
        self.visited.add(next_url)
        return next_url
        
    def get_page_urls(self, page):
        new_urls = []
        soup = BeautifulSoup(page, "html.parser")
        for reference in soup.find_all('div', {'class':'cl-paper-row citation-list__paper-row'}):
            try:
              url = "https://www.semanticscholar.org" + reference.find('a', {'class':'link-button--show-visited'}).get('href')
              if url not in self.visited:
                new_urls.append(url)
            except Exception as e:
                pass
        return new_urls
    
    def get_page_content(self, page):
        soup = BeautifulSoup(page, "html.parser")

        paper_id = self.page_url.split('/')[-1]
        title = soup.find('h1', {'data-test-id': 'paper-detail-title'}).text
        abstract = soup.find('meta', {'name':'description'}).get('content')
        year = soup.find('span', {'data-test-id':'paper-year'}).text
        citation_count = soup.find_all('h2', {'class':'dropdown-filters__result-count__header dropdown-filters__result-count__citations'})[0].text.split(' ')[0]
        reference_count = soup.find_all('h2', {'class':'dropdown-filters__result-count__header dropdown-filters__result-count__citations'})[1].text.split(' ')[0]
        authors = re.findall('author={(.*)}', page).pop().split(' and ')
        card2 = soup.find('div', {'data-test-id':'reference'})
        refs = []
        for reference in card2.find_all('div', {'class':'cl-paper-row citation-list__paper-row paper-v2-font-only'}):
            ref = reference.find('a', {'class':'link-button--show-visited'}).get('href')
            id_ = ref.split('/')[-1]
            refs.append(id_)
        related_topics = soup.find('ul', {'class':'flex-row-vcenter paper-meta'}).findAll('li', {'class': 'paper-meta-item',})[2].text.split(', ')
        
        return {
            'URL' : self.page_url,
            'ID': paper_id,
            'Title': title,
            'Abstract': abstract,
            'Publication Year': year,
            'Citation Count': citation_count,
            'Reference Count': reference_count,
            'Authors': authors,
            'Related Topics' : related_topics,
            'References' : refs
        }
    
    def save_result(self, crawled_pages):
        with open(f'{self.prof_name}.json', 'w') as f:
            json.dump(crawled_pages, f, indent=4)

    def crawl(self):
        crawled_pages = []
        current_url = self.get_next_url()
        while current_url is not None and len(self.visited) <= self.limit:
            
            self.page_url = current_url
            self.visited.add(current_url)
            page = self.get_page(current_url)
            
            try:
                crawled_content = self.get_page_content(page)
                crawled_pages.append(crawled_content)
                print(f'crawled {current_url}')
            except Exception as e:
                pass
            new_urls = self.get_page_urls(page)

            self.start_queue.extend(new_urls)
            current_url = self.get_next_url()

        self.save_result(crawled_pages)
      