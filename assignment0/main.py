import urllib.request
from io import BytesIO
import sqlite3
from sqlite3 import Error
from pypdf import PdfReader
import argparse


def download_pdf(url, headers):
    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    return BytesIO(data)


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = reader.pages[0].extract_text()
    return reader, text


def create_database(db):
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


def insert_data_into_database(reader, cursor):
    num_pages = len(reader.pages)
    for i in range(0, num_pages):
        page = reader.pages[i]
        text = page.extract_text()
        table_text = text.split('\n')
        if i == 0:
            table_text.pop(0)
            table_text.pop(len(table_text) - 1)
            table_text[len(table_text)-1]=table_text[len(table_text) - 1].replace("NORMAN POLICE DEPARTMENT", "")  
        elif i == num_pages - 1:
            table_text.pop(len(table_text) - 1)
        for k in range(0, len(table_text)):
            line_text = table_text[k].split(' ')
            string = ''
            final_dict = {'Date / Time': line_text[0]+' '+line_text[1]}
            final_dict['Incident Number'] = line_text[2]
            final_dict['Incident ORI'] = line_text[-1]
            line_text.remove(line_text[0])
            line_text.remove(line_text[0])
            line_text.remove(line_text[0])
            line_text.remove(line_text[-1])
            for j in range(0, len(line_text)):
                if any(c.islower() for c in line_text[j]) :
                    for a in range (j, len(line_text)):
                        if line_text[a-1] == '911':
                            string += line_text[a-1] + ' '
                        string += line_text[a] + ' ' 
                    break
                elif line_text[j] == 'COP':
                    string += line_text[j] + ' '
                elif line_text[j] == 'EMS':
                    string += line_text[j] + ' '
                elif line_text[j] == 'DDACTS':
                    string += line_text[j] + ' '
                elif line_text[j] == 'MVA':
                    string += line_text[j] + ' '

            final_dict['Incident Type'] = string.strip()
            final_dict['Location'] = ' '.join(line_text).replace(string.strip(), '').strip()
            try:
                cursor.execute("INSERT INTO incidents VALUES (?, ?, ?, ?, ?)", (final_dict['Date / Time'], final_dict['Incident Number'], final_dict['Location'], final_dict['Incident Type'], final_dict['Incident ORI']))
            except Error as e:
                print(e)
                print(final_dict)


def main(url):
    # url = (
    #     "https://www.normanok.gov/sites/default/files/documents/"
    #     "2024-01/2024-01-01_daily_incident_summary.pdf"
    # )
    headers = {}
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
    
    pdf_file = download_pdf(url, headers)
    reader, text = extract_text_from_pdf(pdf_file)
    db = 'resources/normanpd.db'
    dbase, cursor = create_database(db)
    insert_data_into_database(reader, cursor)
    dbase.commit()

    # command_status = """select nature, count(distinct incident_number) from incidents group by nature order by count(incident_number) desc, nature asc"""
    # cursor.execute(command_status)

    # for row in cursor.fetchall():
    #     print(row[0]+'|', row[1])
    # dbase.close()

    # def status(db):
    # current =  dbase.cursor()
    data = cursor.execute("""
                SELECT nature, COUNT(*)
                FROM incidents
                GROUP BY nature
                ORDER BY COUNT(*) DESC, NATURE ASC;
                """)
        
    blank_count = 0
    for (nature, count) in data:
        if nature:
            print(f"{nature}|{count}")
        else:
            blank_count = count
    
    if blank_count > 0:
        print(f"|{count}")
    
    cursor.close()

    # def disconnectdb(conn):
    # conn.close()


if _name_ == '_main_':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)