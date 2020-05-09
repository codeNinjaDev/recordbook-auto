from docx import Document
from recordbook_writer import RecordbookWriter

def main():
    document = Document("form.docx")
    tables = document.tables
    i = 0
    for table in tables:
        j = 0
        for row in table.rows:
            print("Table #", i, "Row #", j, end=": ")
            print_row(row)
            j += 1
        i += 1
def print_row(row):
    for cell in row.cells:
        if not cell.text: 
            print("______", end=" | ")
            continue
        print(cell.text, end=" | ")
    print(end="\n\n\n")

main()
