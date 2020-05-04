""" Simple replacement for distlib SimpleScrapingLocator """
import requests


class SimpleJsonLocator(object):

    """ Simple replacement for distlib SimpleScrapingLocator """

    def __init__(self, base_index):
        self.base_index = base_index

    def get_project(self, project_name):
        url = "%s/pypi/%s/json" % (self.base_url, project_name)
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        items = []
        for version, releases in data["releases"].items():
            for release in releases:
                try:
                    item = {
                        "name": project_name,
                        "version": version,
                        "url": release["url"],
                        "digests": release["digests"],
                        "requires_python": release["requires_python"],
                    }
                except KeyError:
                    continue
                items.append(item)
        return items
