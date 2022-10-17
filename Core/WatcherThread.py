from ZinoAPI import API
from datetime import datetime, timedelta
from Core.Logger import Logger


class WatcherThread:
    def __init__(self, logger=None):
        self.__logger = Logger() if not logger else logger
        self.__api = API(self.__logger)
        self.__found_issues = []

    def watch(self, category_name, category_slug):
        issues = self.__api.getCategoryLatestIssues(category_slug=category_slug)
        for issue_id, issue_info in issues.items():
            if issue_info['publish_date'].date() >= datetime.today().date()\
                    and issue_info['url'] not in self.__found_issues:
                self.__logger.log(f'>> {issue_info["title"]} - '
                                  f'{issue_info["publish_date"].strftime("%Y-%m-%d")} >> \u2713')
                self.__found_issues.append(issue_info['url'])
            # else:
            #     self.__logger.log(f'>> {issue_info["title"]} - '
            #                       f'{issue_info["publish_date"].strftime("%Y-%m-%d")} >> X')

    @property
    def found(self):
        return self.__found_issues
