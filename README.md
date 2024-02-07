
Name: Priyanshu Mathur

# Assignment Description
This Assignment is designed to fetch incident data from a PDF file containing daily incident summaries from the Norman Police Department's website. Here's an overview of its functionality:

1. **Fetching PDF**: The `fetchincidents` function fetches the PDF file from the provided URL using `urllib.request` and returns a `BytesIO` object containing the file data.

2. **Extracting Data from PDF**: The `extractincidents` function uses the `PdfReader` from the `pypdf` library to extract data from the PDF file.

3. **Creating SQLite Database**: The `createdb` function establishes a connection to an SQLite database and creates a table named `incidents` to store incident data, including date, incident number, location, nature, and incident ORI.

4. **Populating Database**: The `populatedb` function populates the SQLite database with data extracted from the PDF. It iterates over each page of the PDF, parses the text, extracts relevant information, and inserts it into the database table.

5. **Main Function**: The `main` function orchestrates the execution of the entire process. It fetches the PDF, extracts data, creates/connects to the database, populates the database with incident data, executes a query to retrieve and print the count of incidents grouped by nature, and finally closes the database cursor.

6. **Argument Parsing**: The script utilizes the `argparse` module to parse command-line arguments. It expects a single argument `--incidents`, representing the URL of the incident summary PDF file.


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

1. **`fetchincidents(url, headers)`**:
   - This function is responsible for fetching the PDF file from the specified URL.
   - It uses `urllib.request.urlopen()` to make a request to the URL with custom headers.
   - The response data is read and wrapped in a `BytesIO` object and returned.
   - Parameters:
     - `url`: The URL from which the PDF file is fetched.
     - `headers`: Additional headers for the HTTP request.

2. **`extractincidents(pdf_file)`**:
   - This function extracts data from the PDF file using the `PdfReader` from the `pypdf` library.
   - It returns the reader object containing the PDF data.
   - Parameters:
     - `pdf_file`: A `BytesIO` object containing the PDF file data.

3. **`createdb(db)`**:
   - This function establishes a connection to an SQLite database and creates a table named `incidents`.
   - It returns both the database connection (`dbase`) and a cursor object.
   - Parameters:
     - `db`: The path to the SQLite database file.

4. **`populatedb(reader, cursor)`**:
   - This function populates the SQLite database with data extracted from the PDF.
   - It iterates over each page of the PDF, extracts relevant information, and inserts it into the database table.
   - Parameters:
     - `reader`: The PDF reader object containing the PDF data.
     - `cursor`: The cursor object for executing SQL queries on the database.

5. **`main(url)`**:
   - This is the main function that orchestrates the entire process.
   - It fetches the PDF, extracts data, creates/connects to the database, populates the database, executes a query to retrieve incident counts, and prints the results.
   - Parameters:
     - `url`: The URL of the incident summary PDF file.


