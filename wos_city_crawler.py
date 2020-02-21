#from file_reader import get_city
import requests
import codecs
import sys
from bs4 import BeautifulSoup
from file_writer import write_addresses, write_doc_info
import re
import db_reader
from db_writer import DbWriter
from fake_useragent import UserAgent
from selenium import webdriver

class WosCrawler:
    month_dict = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
                  'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}

    def __init__(self, year, city_name, start_doc, max_to_crawl):
        self.max_to_crawl = max_to_crawl
        #information on product id and session id for a particular wos search criteria is in db
        #this is the data we will get below.
        self.city_year = db_reader.get_city_year(year, city_name, start_doc)


    def run(self):
        self.logger.log("Preprocessing")
        print("Preprocessing")
        url = "http://apps.webofknowledge.com/Search.do?product=WOS&SID=%s&search_mode=GeneralSearch&prID=%s" \
              % (self.city_year.session_id, self.city_year.product_id)

        resp = self.fetch_data(url)

        #update total docs
        self.set_total_docs(resp)

        #get_web_address_for_full_docs
        link_frame = self.get_link_to_full_docs(resp)

        #add the precise doc (num) that you want to crawl into the link
        start_doc_final = max(self.city_year.start_doc, self.city_year.doc_crawled + 1)
        end_doc = min(self.city_year.start_doc + self.max_to_crawl - 1, self.city_year.total_doc)

        search_id = db_reader.get_search_param(self.city_year.year, self.city_year.name)[0]['id']
        dbw = DbWriter()
        dbw.connect()

        #get the details of each article
        for i in range(start_doc_final, end_doc + 1):
            print("Processing doc %s. Progress: %s out of %s"
                            % (i, i - self.city_year.start_doc + 1, end_doc -
                               self.city_year.start_doc + 1))
            link = link_frame + str(i)

            resp = self.fetch_data(link)

            doi = self.get_doi(resp)
            isbn = self.get_isbn(resp)
            title = self.get_title(resp)

            identifer = "N.A."
            iden_type = "N.A."
            if doi != "N.A.":
                iden_type = "DOI"
                identifier = doi
            elif isbn != "N.A.":
                iden_type = "ISBN"
                identifier = isbn
            else:
                iden_type = "Title"
                identifier = title

            auth_sequence, addresses = self.get_addresses(resp)
            journal_name = self.get_journal_name(resp)
            published_date = self.get_published_date(resp)

            published_date_arr = published_date.split(" ")
            published_year = 0
            published_month = 0
            published_day = 0

            for datel in published_date_arr:
                if datel.isdigit():
                    if len(datel) == 4:
                        published_year = int(datel)
                    else:
                        published_day = int(datel)
                else:
                    if "-" in datel:
                        datel = datel[datel.index("-") + 1:len(datel)]

                    if datel not in self.month_dict.keys():
                        published_month = 0
                    else:
                        published_month = self.month_dict[datel]

            doc_type = self.get_document_type(resp)
            num_citation = self.get_num_citation(resp)
            rarea, wos_rarea = self.get_research_area(resp)
            reprint_authors = self.get_reprint_authors(resp)
            is_highly_cited = self.is_highly_cited_paper(resp)
            is_hot_paper = self.is_hot_paper(resp)

            self.city_year.doc_crawled = i
            self.city_year.percent_crawled = (self.city_year.doc_crawled -
                                              self.city_year.start_doc + 1) * 1.0 / \
                                             (end_doc - self.city_year.start_doc + 1)

            #if len(auth_sequence) > 1:
            write_doc_info(self.city_year, identifier, iden_type, journal_name, num_citation,
                           doc_type, published_day, published_month, published_year,
                           rarea, wos_rarea, auth_sequence, reprint_authors, is_highly_cited,
                           is_hot_paper)
            write_addresses(self.city_year, addresses)
            dbw.update_crawl_progress(search_id, self.city_year.start_doc, self.city_year.total_doc,
                                      self.city_year.doc_crawled, self.city_year.percent_crawled)
            dbw.commit()



        dbw.close()

    def is_hot_paper(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        cat_tag = soup.find("div", {"class": "flex-row-partition2"})

        if cat_tag is not None and "\'hotpaper\': true" in cat_tag.text.lower():
            return True
        else:
            return False

    def is_highly_cited_paper(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        cat_tag = soup.find("div", {"class": "flex-row-partition2"})

        if cat_tag is not None and "\'highlycited\': true" in cat_tag.text.lower():
            return True
        else:
            return False

    def set_doc_crawled(self, link):
        self.city.doc_crawled = link[link.rfind("=") + 1:len(link)]

        #print(self.city.doc_crawled)

    def fetch_data_selenium(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--test-type")
        options.add_argument("--disable-notifications")
        #options.add_argument("--headless")

        driver = webdriver.Chrome("C:\Program Files (x86)\Google\Chrome\chromedriver", options=options)
        # driver = webdriver.PhantomJS("C:\Program Files (x86)\Google\Chrome\phantomjs")
        driver.get(url)
        page = driver.page_source

        return page

    def fetch_data(self, url):
        ua = UserAgent()
        header = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                            'image/webp,image/apng,*/*;q=0.8',
                  'Accept-Encoding': 'gzip, deflate',
                  'Accept-Language': 'en-US,en;q=0.9',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                                'AppleWebKit/537.36 (KHTML, like Gecko) '
                                'Chrome/72.0.3626.121 Safari/537.36'}

        

        resp = requests.get(url, headers=header)

        if b"Server.sessionNotFound" in resp.content:
            self.logger.log("Session Expires\n")
            sys.exit("Session Expires")
        else:
            return resp.text


    def set_total_docs(self, content):
        soup = BeautifulSoup(content, "html.parser")
        nod = soup.find("span", {"id": "trueFinalResultCount"})

        #self.city.total_doc = int(nod.text)
        self.city_year.total_doc = int(nod.text)

    def get_link_to_full_docs(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        raw_link = soup.find("a", {"class": "smallV110 snowplow-full-record"})
        link = "".join(["http://apps.webofknowledge.com", raw_link['href']])
        link = link.replace("page=1","")
        link = link[0:link.rfind("=")+1]
        return link

    def get_journal_name(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        cat_tag = soup.find("span", {"class": "sourceTitle"})

        return cat_tag.value.text

    def get_research_area(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        ra_tag = soup.find("span", text="Research Areas:")
        ra = ra_tag.parent.text.replace("Research Areas:","")

        wora_tag = soup.find("span", text="Web of Science Categories:")
        wora = wora_tag.parent.text.replace("Web of Science Categories:","")

        #ra = ra.replace(", ", " subarea ");
        #wora = wora.replace(", ", " subarea ");

        return ra.strip(), wora.strip()

    def get_title(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        div = soup.find("div", {"class": "title"})
        val = div.find("value")
        return val.text.strip()

    def get_document_type(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        doctag = soup.find("span", text="Document Type:")

        if doctag is not None:
            doc = doctag.parent.text.replace("Document Type:", "")
            return doc.strip()
        else:
            return "N.A."

    def get_published_date(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        pubtag = soup.find("span", text="Published:")

        if pubtag is not None:
            pub = pubtag.parent.text.replace("Published:", "")
            #print(pub.strip())
            return pub.strip()
        else:
            return "N.A."

    def get_isbn(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        isbntag = soup.find("span", text="ISBN:")

        if isbntag is not None:
            isbn = isbntag.parent.text.replace("ISBN:", "")
            return isbn.strip()
        else:
            return "N.A."

    def get_doi(self, content):
        soup = BeautifulSoup(content, 'html.parser')

        doitag = soup.find("span", text="DOI:")

        if doitag is not None:
            doi = doitag.parent.text.replace("DOI:", "")
            return doi.strip()
        else:
            return "N.A."
        #print(doi)

    def get_reprint_authors(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        spans = soup.find_all("span", text=re.compile("Reprint Address:*"))

        authors = []
        for span in spans:
            author = span.next_sibling.replace("(reprint author)", "").strip()
            author = author.replace(",","")
            if ";" in author:
                for a in author.split(";"):
                    if a.strip() not in authors:
                        authors.append(a.strip())
            else:
                if author.strip() not in authors:
                    authors.append(author.strip())

        #print(" and ".join(authors))
        return authors

    def get_num_citation(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        td = soup.find("span", {"class": "large-number"})

        numtxt = td.text.replace(",", "")

        return int(numtxt)


    def get_author_idx_and_name(self, content):
        dict = {}

        soup = BeautifulSoup(content, "html.parser")

        auth = soup.find("p", {"class": "FR_field"})
        author_ltxt = auth.text.replace("By:","")
        authors = author_ltxt.split(";")

        auth_array = []

        if len(authors) == 1:
            author = authors[0]
            try:
                left_circ = author.index("(")
                right_circ = author.index(")")
            except ValueError:
                left_circ = -1
                right_circ = -1

            if left_circ != -1 and right_circ != -1:
                author = author[left_circ + 1:right_circ]

            auth_array.append(author.strip())
            dict[1] = [author.strip()]
        else:
            for author in authors:
                try:
                    left_sqr = author.index("[")
                    right_sqr = author.index("]")
                except ValueError:
                    left_sqr = -1
                    right_sqr = -1

                author_indices = []
                if left_sqr != -1 and right_sqr != -1:
                    author_idx_txt = author[left_sqr + 1: right_sqr]
                    author_indices = author_idx_txt.split(",")
                    author_indices = [int(x) for x in author_indices]

                try:
                    left_circ = author.index("(")
                    right_circ = author.index(")")
                except ValueError:
                    left_circ = -1
                    right_circ = -1

                if left_circ != -1 and right_circ != -1:
                    author = author[left_circ+1:right_circ]

                auth_array.append(author)

                for author_idx in author_indices:
                    if author_idx in dict:
                        dict[author_idx].append(author)
                    else:
                        dict[author_idx] = [author]

        return auth_array, dict

    def get_addresses(self, content):
        auth_seq, auth_dict = self.get_author_idx_and_name(content)

        addresses = []
        soup = BeautifulSoup(content, 'html.parser')
        tds = soup.findAll("td", {"class": "fr_address_row2"})

        address_dict = {}
        org_dict = {}

        for td in tds:
            if '[' in td.text:
                str_to_process = td.text

                idx = str_to_process.find("]")
                #get number from string
                num = str_to_process[1:idx]
                num = int(num.strip())

                # remove [ (number) ] from string
                str_to_process = str_to_process[idx + 1:len(td.text)]
                # remove Organization-Enhanced Name(s)
                str_to_process = str_to_process.replace("Organization-Enhanced Name(s)", "")
                str_to_process = str_to_process.replace(u'\xa0', u'')

                vals = str_to_process.split("\n")
                address = vals[0].strip()
                vals[0] = ""
                vals = [value.strip() for value in vals if value != ""]
                org = ",".join(vals)

                address_dict[num] = address
                org_dict[num] = org

        address_auth_dict = {}
        address_org_dict = {}

        for auth_key in auth_dict.keys():
            auth_array = auth_dict.get(auth_key)

            if auth_key in address_dict.keys():
                address = address_dict[auth_key]
                org = org_dict[auth_key]

                if auth_key == 0:
                    if "Unknown" not in address_org_dict:
                        address_org_dict["Unknown"] = "Unknown"

                    if "Unknown" in address_auth_dict:
                        address_auth_dict["Unknown"].extend(auth_array)
                    else:
                        address_auth_dict["Unknown"] = auth_array
                else:
                    if address in address_org_dict:
                        if len(org) > len(address_org_dict[address]):
                            address_org_dict[address] = org
                    else:
                        address_org_dict[address] = org

                    if address in address_auth_dict:
                        address_auth_dict[address].extend(auth_array)
                    else:
                        address_auth_dict[address] = auth_array

        for address in address_auth_dict:
            authors = " and ".join(address_auth_dict[address])
            addresses.append([authors, address, address_org_dict[address]])

        '''for address in addresses:
            print(address)'''
        return auth_seq, addresses



def dump_sample():
    url = "http://apps.webofknowledge.com/full_record.do?product=WOS&search_mode=GeneralSearch&qid=2&SID=D3KSLj65Tvc7bqqetXi&page=1&doc=5"
    resp = requests.get(url)
    writer = codecs.open("resp2.html","w","utf-8")
    writer.write(resp.text)
    writer.close()


if __name__ == "__main__":
    year = int(sys.argv[1])
    city_name = sys.argv[2]
    start_doc = int(sys.argv[3])
    max_to_crawl = int(sys.argv[4])
    wos = WosCrawler(year, city_name, start_doc, max_to_crawl)
    wos.run()



