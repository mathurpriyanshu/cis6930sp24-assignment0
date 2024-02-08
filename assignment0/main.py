import os
import pypdf
import re
import sqlite3
import argparse
import urllib
import urllib.request
from assignment0.constants import strings

def pdf_download(url):
    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"

    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()
    local_file_path = strings.file_paths["local_file_path"]
    with open(local_file_path, "wb") as local_file:
        local_file.write(data)

    return local_file_path

def data_extract(pdf_path):
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

            matches = re.finditer(date_pattern, l)

            if matches:
                indices = [match.start() for match in matches]
                matched_lines = [l[i:j].strip() for i, j in zip([0] + indices, indices + [None])]

                matched_lines = list(filter(None, matched_lines))
                for ml in matched_lines:
                    split_line = re.split("   ", ml)
                    non_empty_list = [value for value in split_line if value is not None and value != ""]
                    fields_extraction(non_empty_list, data)

            else:
                matched_lines =  [l.strip()]
                split_line = re.split("   ", l)

                non_empty_list = [value for value in split_line if value is not None and value != ""]
                fields_extraction(non_empty_list, data)

    return data

def fields_extraction(non_empty_list, data):
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

def db_connection():
    con = sqlite3.connect(strings.dbstrings["db_path"])
    cur = con.cursor()

    return (cur, con)

def db_creation():
    (cur, con) = db_connection()
    statement = cur.execute(strings.dbstrings["create_db"])
    return statement

def db_population(result : list[dict[str, str]]):
    (cur, con) = db_connection()
    query_string = strings.dbstrings["insert_db"]
    for entry in result:
        query_string = query_string + "(" + "\'" + entry.get(strings.field_names["date_time"]) + "\'" + "," +  "\'" + entry.get(strings.field_names["incident_number"]) + "\'" + "," + "\'" + entry.get(strings.field_names["location"]) + "\'" + "," + "\'" + entry.get(strings.field_names["nature"]) + "\'" + "," + "\'" + entry.get(strings.field_names["incident_type"]) + "\'" + ")" + ","

    query_string = query_string[: -1]

    statement = cur.execute(query_string)
    con.commit()
    return statement.rowcount

def status():
    query_string = strings.dbstrings["select_db"]
    (cur, con) = db_connection()
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

def db_get():
    (cur, con) = db_connection()
    statement = cur.execute(strings.dbstrings["select_all_db"])
    return statement.fetchall()

def db_deletion():
    (cur, con) = db_connection()
    statement = cur.execute(strings.dbstrings["drop_table"])

def fun_execute(url):
    pdf = pdf_download(url)
    result = data_extract(pdf)
    db_deletion()
    db_creation()
    db_population(result)
    print_status()
    pdf_deletion(pdf)

def pdf_deletion(pdf_path):
    try:
        os.remove(pdf_path)
    except FileNotFoundError:
        print(f"PDF file not found: {pdf_path}")

def main():
    parser = argparse.ArgumentParser(description='Process incidents from a given URL.')
    parser.add_argument('--incidents', help='URL to fetch incidents data')
    args = parser.parse_args()

    if args.incidents:
        url = args.incidents
        fun_execute(url)

    else:
        print(strings.other["provide_incidents_url"])

if __name__ == "__main__":
    main()