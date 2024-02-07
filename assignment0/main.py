import urllib.request
from io import BytesIO
import sqlite3
from sqlite3 import Error
from pypdf import PdfReader
import argparse


def fetchincidents(url, headers):
    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    return BytesIO(data)


def extractincidents(pdf_file):
    reader = PdfReader(pdf_file)
    return reader


def createdb(db):
    dbase = sqlite3.connect(db)
    cursor = dbase.cursor()
    command_insert = """CREATE TABLE IF NOT EXISTS incidents (
        date DATE,
        incident_number TEXT,
        location TEXT,
        nature TEXT,
        incident_ori TEXT
        )"""
    cursor.execute(command_insert)
    return dbase, cursor


def populatedb(reader, cursor):
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        table_text = text.split('\n')
        
        if i == 0:
            table_text = table_text[1:-1]
            table_text[-1] = table_text[-1].replace("NORMAN POLICE DEPARTMENT", "")  
        elif i == len(reader.pages) - 1:
            table_text.pop()
        
        for line in table_text:
            line_text = line.split(' ')
            date_time = ' '.join(line_text[:2])
            incident_number = line_text[2]
            incident_ori = line_text[-1]
            
            # Remove unnecessary elements from line_text
            line_text = line_text[3:-1]
            
            # Extract Incident Type and Location
            incident_type = ''
            location = ''
            for word in line_text:
                if any(c.islower() for c in word) or word in {'COP', 'EMS', 'DDACTS', 'MVA'}:
                    incident_type += word + ' '
                else:
                    location += word + ' '
            
            # Remove extra whitespaces
            incident_type = incident_type.strip()
            location = location.strip()
            
            try:
                cursor.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)", (date_time, incident_number, location, incident_type, incident_ori))
            except Error as e:
                print(e)
                print({
                    'Date / Time': date_time,
                    'Incident Number': incident_number,
                    'Location': location,
                    'Incident Type': incident_type,
                    'Incident ORI': incident_ori
                })


def main(url):
    headers = {}
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    
    pdf_file = fetchincidents(url, headers)
    reader = extractincidents(pdf_file)
    db = './resources/normanpd.db'
    dbase, cursor = createdb(db)
    populatedb(reader, cursor)
    dbase.commit()

    
    command_status = """select nature, count() from incidents group by nature order by count() desc, nature asc"""
    output = cursor.execute(command_status)

        
    blanks = 0
    for (nature, count) in output:
        if nature:
            print(f"{nature}|{count}")
        else:
            blanks = count
    
    if blanks > 0:
        print(f"|{count}")
    
    cursor.close()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
       
        main(args.incidents)


