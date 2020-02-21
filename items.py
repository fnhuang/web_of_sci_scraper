class CityYear:
    def __init__(self, year, name, start_doc, total_doc, doc_crawled,
                 percent_crawled, session_id, product_id):
        self.start_doc = start_doc
        self.name = name
        self.total_doc = total_doc
        self.doc_crawled = doc_crawled
        self.percent_crawled = percent_crawled
        self.session_id = session_id
        self.product_id = product_id
        self.year = year



'''ra = ResearchArea()
for area in ra.area_field:
    print(area, len(ra.area_field[area]))'''