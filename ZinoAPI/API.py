from requests import Session
from Core import Logger
import re
from json import loads
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


class API:
    ENDPOINTS = {
        'website_url': 'https://www.zinio.com/',
        'categories': 'api/newsstand/newsstands/101/'
                      'categories?limit=50&content_rating_max=30&language=en',
    }

    def __init__(self, logger=None):
        self.__session = Session()
        self.__logger = Logger() if not logger else Logger()
        self.__session.headers.update({
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'referer': 'https://www.zinio.com'
        })
        self.__categories = {}

    @property
    def categories(self):
        return self.__categories

    def getCategories(self):
        try:
            response = self.__session.get(self.ENDPOINTS['website_url'] + self.ENDPOINTS['categories'])
            if response.status_code == 200:
                self.__logger.log('Website categories has been fetched successfully.')
                categories_data = response.json().get('data', [])
                categories_count = 0
                for category_info in categories_data:
                    self.__categories[category_info['name']] = category_info['slug'] + f"-c{category_info['id']}"
                    categories_count += 1
                self.__logger.log(f'{categories_count} categories has been found')
                return self.__categories
            self.__logger.log("Website categories couldn't be fetched")
        except Exception as e:
            self.__logger.log(f"Website categories couldn't be fetched.\n\t[-] errors: {e}", True)
        return {}

    def getCategoryIssuesByPage(self, category_slug, page):
        try:
            response = self.__session.get(self.ENDPOINTS['website_url'] + category_slug + f"/?sort=most-popular"
                                                                                          f"&page={page}"
                                                                                          f"&locale=en")
            response_text = response.text
            script = re.findall(r'"CATEGORY_PUBLICATION":(.*),"RECENT_ISSUES"', response_text)[0]
            library_data = loads(script)
            issues = {}
            for issue in library_data["flatData"]:
                issues[issue['id']] = {
                    'publish_date': datetime.strptime(issue['datePublished'].split('+')[0], "%Y-%m-%dT%H:%M:%S"),
                    'url': self.ENDPOINTS['website_url'] + issue['anchor'][1:],
                    'title': issue['title']
                }
            return issues, library_data['pageTotal']
        except Exception as e:
            self.__logger.log(f"Website issues couldn't be fetched.\n\t[-] errors: {e}", True)
        return {}, -1

    def getCategoryLatestIssues(self, category_slug):
        try:
            issues, page_limit = self.getCategoryIssuesByPage(category_slug, page=1)
            with ThreadPoolExecutor(50) as e:
                threads = []
                for index in range(2, page_limit+1):
                    thread = e.submit(self.getCategoryIssuesByPage, category_slug, index)
                    threads.append(thread)

                for thread in threads:
                    temp_issues, page_limit = thread.result()
                    if page_limit != -1:
                        issues.update(temp_issues)
            return issues
        except Exception as e:
            self.__logger.log(f"Website issues couldn't be fetched.\n\t[-] errors: {e}", True)
        return {}, -1


if __name__ == "__main__":
    api = API()
    categories = api.getCategories()
    # for category_name, category_slug in categories.items():
    print(api.getCategoryLatestIssues("tech-gaming-c123"))
