# Introduction
This code is scraping web of science dataset given that you have university access. You can only run this code inside university network. 

# How to
First, go to web of science and enter your search criteria. In this scraper, the search criteria will be city, and year: 
https://www.webofknowledge.com/

In the URL after search, you will find session id and product id. Store this information somewhere. In this scraper, you store the 
information in the database. 
https://apps.webofknowledge.com/Search.do?product=WOS&SID=[session_id]&search_mode=GeneralSearch&prID=[product_id]

Results is stored in file. file_writer.py writes data into files. 

Additionally, after a document is crawled, database will store which document (document number) for which search criteria. Once in a while 
you will get kicked out either because session id expires, or for other unknown reasons. In this case you will have to re-run the crawler. 
In this situation the doc no will be useful for you, because you will know from which document to re-start your crawling. 
