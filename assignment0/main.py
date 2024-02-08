import os

import pypdf
import re
import sqlite3
import argparse
import urllib
import urllib.request
from assignment0.constants import strings

def download_data(url):
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"

    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    local_file_path = strings.file_paths["local_file_path"]
    with open(local_file_path, "wb") as local_file:
        local_file.write(data)

    return local_file_path

def extract_data_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text(extraction_mode="layout")

    lines = text.splitlines()
    lines = lines[2:]
    lines = lines[:-1]

    data = []
    for l in lines:
        if(l != ""):
            date_pattern = r'\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}'

            # Find all occurrences of the date pattern in the line
            matches = re.finditer(date_pattern, l)

            # If there are matches, split the line at each match
            if matches:
                indices = [match.start() for match in matches]
                matched_lines = [l[i:j].strip() for i, j in zip([0] + indices, indices + [None])]

                # Filter out empty lines
                matched_lines = list(filter(None, matched_lines))
                for ml in matched_lines:
                    split_line = re.split("   ", ml)
                    non_empty_list = [value for value in split_line if value is not None and value != ""]
                    extract_fields(non_empty_list, data)

            else:
                matched_lines =  [l.strip()]
                split_line = re.split("   ", l)

                non_empty_list = [value for value in split_line if value is not None and value != ""]
                extract_fields(non_empty_list, data)

    return data

def extract_fields(non_empty_list, data):
    if(len(non_empty_list) == 5):
        categories = ["Date/Time", "Incident Number", "Location", "Nature", "Incident ORI"]
        date_time = non_empty_list[0].strip()
        incident_number = non_empty_list[1].strip()
        location = non_empty_list[2].strip()
        if(non_empty_list[3] != " "):
            nature = non_empty_list[3].strip()
        else: nature = non_empty_list[3]
        incident_type = non_empty_list[4].strip()

        extracted_data = {
            strings.field_names["date_time"]: date_time,
            strings.field_names["incident_number"]: incident_number,
            strings.field_names["location"]: location,
            strings.field_names["nature"] : nature,
            strings.field_names["incident_type"]: incident_type
        }

        # Append the data to the list
        data.append(extracted_data)

    else:
        nature = ""
        for entry in non_empty_list:
            if(entry.isalpha()):
                nature = entry

        extracted_data = {
            strings.field_names["date_time"] : "",
            strings.field_names["incident_number"] : "",
            strings.field_names["location"] : "",
            strings.field_names["nature"] : nature,
            strings.field_names["incident_type"]: ""
        }

        data.append(extracted_data)

def connectdb():
    con = sqlite3.connect(strings.dbstrings["db_path"])
    cur = con.cursor()

    return (cur, con)

def createdb():
    (cur, con) = connectdb()
    statement = cur.execute(strings.dbstrings["create_db"])
    return statement

def populatedb(result : list[dict[str, str]]):
    (cur, con) = connectdb()
    query_string = strings.dbstrings["insert_db"]
    for entry in result:
        query_string = query_string + "(" + "\'" + entry.get(strings.field_names["date_time"]) + "\'" + "," +  "\'" + entry.get(strings.field_names["incident_number"]) + "\'" + "," + "\'" + entry.get(strings.field_names["location"]) + "\'" + "," + "\'" + entry.get(strings.field_names["nature"]) + "\'" + "," + "\'" + entry.get(strings.field_names["incident_type"]) + "\'" + ")" + ","

    query_string = query_string[: -1]

    statement = cur.execute(query_string)
    con.commit()
    return statement.rowcount

def status():
    # query_string = "SELECT nature, COUNT(*) AS nature_count FROM incidents GROUP BY nature"
    query_string = strings.dbstrings["select_db"]
    (cur, con) = connectdb()
    statement = cur.execute(query_string)
    data = statement.fetchall()
    filtered_data_nature = [entry for entry in data if entry[0] != 'Nature' and entry[0] != 'NATURE' and entry[0] != 'RAMP']
    empty_entry = [entry for entry in filtered_data_nature if entry[0] == '']
    filtered_data_empty_entry = [entry for entry in filtered_data_nature if entry[0] != '']
    sorted_data = sorted(filtered_data_empty_entry, key=lambda x: (-x[1], x[0]))

    if(len(empty_entry) != 0): sorted_data.append(empty_entry[0])

    return sorted_data

def print_status():
    sorted_data = status()
    final_str = ""
    for data in sorted_data:

        final_str = final_str + data[0] + strings.other["seperator"] +  str(data[1]) + strings.other["new_line"]
        print(data[0] + strings.other["seperator"] +  str(data[1]))

    return final_str

def getdb():
    (cur, con) = connectdb()
    statement = cur.execute(strings.dbstrings["select_all_db"])
    return statement.fetchall()

def deletedb():
    (cur, con) = connectdb()
    statement = cur.execute(strings.dbstrings["drop_table"])

def execute_functions(url):
    pdf = download_data(url)
    result = extract_data_from_pdf(pdf)
    deletedb()
    createdb()
    populatedb(result)
    print_status()
    delete_pdf(pdf)

def delete_pdf(pdf_path):
    try:
        os.remove(pdf_path)
        # print(f"Deleted PDF file: {pdf_path}")
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")

def main():
    parser = argparse.ArgumentParser(description='Process incidents from a given URL.')
    parser.add_argument('--incidents', help='URL to fetch incidents data')
    args = parser.parse_args()

    if args.incidents:
        url = args.incidents
        execute_functions(url)

    else:
        print(strings.other["provide_incidents_url"])

if __name__ == "__main__":
    main()