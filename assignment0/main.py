import argparse

import assignment0


def main(url):
    # Download data
    incident_data = assignment0.fetchincidents(url)

    # Extract data
    incidents = assignment0.extractincidents(incident_data)
	
    # Create new database
    db = assignment0.createdb()
	
    # Insert data
    assignment0.populatedb(db, incidents)
	
    # Print incident counts
    assignment0.status(db)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)

import urllib

url = ("https://www.normanok.gov/sites/default/files/documents/"
       "2024-01/2024-01-01_daily_incident_summary.pdf")
headers = {}
headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"                          

data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()


import pypdf
from pypdf import PdfReader

reader = PdfReader("example.pdf")
page = reader.pages[0]
print(page.extract_text()) # Shows the extracted text