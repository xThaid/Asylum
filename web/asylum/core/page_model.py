class PageModel:
    user = {}
    page_name = ''
    breadcrumb = []

    def __init__(self, page_name, user):
        self.user = user
        self.page_name = page_name
        self.breadcrumb = [
            {
                'name': 'Strona główna',
                'href': '/home'
            }
        ]

    def add_breadcrumb_page(self, name, href):
        self.breadcrumb.append(
            {
                'name': name,
                'href': href
            }
        )
        return self

    def to_dict(self):
        self_dict = vars(self)
        self_dict['breadcrumb'] = self.breadcrumb
        return self_dict
