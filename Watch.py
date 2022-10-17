from Core.WatcherThread import WatcherThread
from Core.Logger import Logger
from ZinoAPI import API
from concurrent.futures import ThreadPoolExecutor
from time import time

if __name__ == "__main__":
    logger = Logger()
    zino_api = API(logger)
    categories = zino_api.getCategories()
    found = []
    watcher = WatcherThread(logger)

    while True:
        start_time = time()
        with ThreadPoolExecutor(50) as e:
            for category_name, category_slug in categories.items():
                e.submit(watcher.watch, category_name, category_slug)
