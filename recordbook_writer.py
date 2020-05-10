from sys import argv
from docx import Document
from enum import Enum

import datetime

class Level(Enum):
    CLUB = "Cl"
    COUNTY = "Co"
    DISTRICT = "D"
    STATE = "S"

class LeadershipRole(Enum):
    ELECTED = "E"
    APPOINTED = "A"
    VOLUNTEER = "V"
    PROMOTIONAL = "P"

class ServiceRole(Enum):
    YOURSELF = "Y"
    MEMBER = "M"
    PRIMARY = "P"

class RecordbookDict:
    def __init__(self):
        pass

    def create_recordbook_dict(self):
        book_dict = {
                "personal_info": { "name": "", "county": "", "district": "", "division": "", "category": "", "club": ""},
                "leadership": [],
                "service": [],
                "awards": [],
                "career": []
                }
        return book_dict

class RecordbookWriter:

    def __init__(self, document_name):
        self.document = Document(document_name)
        self.document_name = document_name
        tables = self.document.tables

        self.name = tables[0].cell(0, 1)
        self.county = tables[0].cell(0, 3)
        self.district = tables[0].cell(0, 5)
        self.division = tables[0].cell(1, 1)
        self.category = tables[0].cell(1, 3)

        self.leadership_form = tables[6].rows[3:]
        self.service_form = tables[8].rows[3:]
        self.award_form = tables[12].rows[3:]
        self.career_form = tables[16].rows[6:]

    def row_empty(self, row):
        i = 0
        for cell in row.cells:
            if cell.text and i != 0:
                return False
            i += 1
        return True

    def get_empty_row(self, rows):
        curr_row = None
        for row in rows:
            if self.row_empty(row):
                curr_row = row
                break
        return curr_row


    def fill_info(self, name="", county="", district="", division="", category=""):
        self.name.text = name
        self.county.text = county
        self.district.text = district
        self.division.text = division
        self.category.text = category
        self.document.save(self.document_name)

    def append_leadership(self, activity, role, level, year=str(datetime.datetime.today().year), duties=""):


        curr_row = self.get_empty_row(self.leadership_form)
        if not curr_row:
            curr_row = self.document.tables[6].add_row()
        row_cells = curr_row.cells

        row_cells[1].text = year
        row_cells[2].text = activity
        row_cells[3].text = role
        row_cells[4].text = level
        row_cells[5].text = duties
        self.document.save(self.document_name)

    def append_service(self, role, activity, year=str(datetime.datetime.today().year), impact=""):

        curr_row = self.get_empty_row(self.service_form)
        if not curr_row:
            curr_row = self.document.tables[8].add_row()
        row_cells = curr_row.cells

        row_cells[1].text = year
        row_cells[2].text = role
        row_cells[3].text = activity
        row_cells[4].text = impact
        self.document.save(self.document_name)

    def append_award(self, level, recognition, year=str(datetime.datetime.today().year), importance=""):

        curr_row = self.get_empty_row(self.award_form)
        if not curr_row:
            curr_row = self.document.tables[12].add_row()
        row_cells = curr_row.cells

        row_cells[1].text = year
        row_cells[2].text = level
        row_cells[3].text = recognition
        row_cells[4].text = importance
        self.document.save(self.document_name)

    def append_career(self, activity, year=str(datetime.datetime.today().year), importance=""):
        curr_row = self.get_empty_row(self.career_form)
        if not curr_row:
            curr_row = self.document.tables[16].add_row()
        row_cells = curr_row.cells

        row_cells[1].text = year
        row_cells[2].text = activity
        row_cells[3].text = importance
        self.document.save(self.document_name)
