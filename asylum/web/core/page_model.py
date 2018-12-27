class PageModel:

    def __init__(self, page_name, user):
        self.user = user
        self.page_name = page_name
        self.breadcrumb = [
            {
                'name': 'Strona główna',
                'href': '/home'
            }
        ]
        self.tabs = []
        self.active_tab = 0

    def add_breadcrumb_page(self, name, href):
        self.breadcrumb.append(
            {
                'name': name,
                'href': href
            }
        )
        return self

    def add_tab(self, name, url):
        self.tabs.append({
            'name': name,
            'url': url
        })
        return self

    def activate_tab(self, tab_index):
        self.active_tab = tab_index
        return self

    def to_dict(self):
        self_dict = vars(self)
        self_dict['breadcrumb'] = self.breadcrumb
        return self_dict
