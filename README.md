
Name: Priyanshu Mathur

# Assignment Description
This Assignment is designed to fetch incident data from a PDF file containing daily incident summaries from the Norman Police Department's website. We then store that data in a SQLite database after doing the extraction.


# How to install
1. Clone the repository on your system:
    
$ git clone https://github.com/mathurpriyanshu/cis6930sp24-assignment0.git

$ cd cis6930sp24-assignment0
    

2. Install prerequisites:
$ pipenv install pypdf


# How to run
Branch to be used: main 

Command to run: 

pipenv run python assignment0/main.py --incidents https://www.normanok.gov/sites/default/files/documents/2024-01/2024-01-08_daily_incident_summary.pdf

# Functions

1. `pdf_download(url)`: This function downloads a PDF file from the given URL using urllib and saves it locally. It returns the local file path where the PDF is saved.

2. `data_extract(pdf_path)`: This function extracts data from the PDF file specified by the `pdf_path`. It uses PyPDF2 to read the PDF, extracts text from each page, and then parses the text to extract relevant incident data such as date/time, incident number, location, nature, and incident type. The extracted data is returned as a list of dictionaries.

3. `fields_extraction(non_empty_list, data)`: This function extracts fields from a non-empty list containing incident data and appends it to the `data` list. It handles cases where the list may contain missing values.

4. `db_connection()`: This function establishes a connection to the SQLite database using the path specified in the `dbstrings` constants. It returns a cursor object and a connection object.

5. `db_creation()`: This function creates the necessary database tables using SQL statements specified in the `create_db` constant.

6. `db_population(result)`: This function populates the database with the incident data extracted from the PDF file. It constructs and executes SQL INSERT statements based on the data provided in the `result` list.

7. `status()`: This function retrieves the status of the database by executing a SELECT query specified in the `select_db` constant. It filters out unwanted data and sorts the results based on specific criteria.

8. `print_status()`: This function prints the status of the database to the console and returns a formatted string containing the same information.

9. `db_get()`: This function retrieves all data from the database by executing a SELECT query specified in the `select_all_db` constant.

10. `db_deletion()`: This function deletes the database table using the SQL DROP TABLE statement specified in the `drop_table` constant.

11. `fun_execute(url)`: This function serves as the main execution function. It orchestrates the downloading of the PDF file, extraction of data, database operations, printing of database status, and deletion of the PDF file.

12. `pdf_deletion(pdf_path)`: This function deletes the PDF file specified by the `pdf_path` parameter.

13. `main()`: This function is the entry point of the script. It parses command-line arguments using argparse to get the URL of the incidents data. Then, it calls the `fun_execute` function to execute the main functionality of the script. If no URL is provided, it prints a message asking for the incidents URL.