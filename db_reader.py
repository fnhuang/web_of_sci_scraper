import db
from items import CityYear

def get_search_param(year, city_name):
    sql_statement = 'SELECT * FROM search_param WHERE lower(city) = \'%s\' and year = %s'\
                    %(city_name, year)
    results = db.read(sql_statement)
    return results


def get_city_year(year, city_name, start_doc):

    sql_statement = "select * from crawl_progress where search_id in " \
                    "(SELECT id FROM search_param WHERE lower(city) = \'%s\' and year = %s)" \
                    "AND start_doc = %s" \
                    % (city_name.lower(), year, start_doc)

    results = db.read(sql_statement)
    result = results[0]

    city_year = CityYear(year, city_name, start_doc, result['total_doc'], result['doc_num'],
                         result['percent_crawled'], result['session_id'], result['product_id'])

    return city_year


