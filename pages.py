class Page:
    def __init__(self, number: int, text: str):
        self.number = number
        self.text = text


class Pages:
    def __init__(self):
        self.pages = []

    def add_page(self, page: Page):
        self.pages.append(page)

    def get_page(self, number: int) -> Page:
        return self.pages[number - 1]

    def get_total_pages(self) -> int:
        return len(self.pages)
