from recordbook_writer import Level, ServiceRole, LeadershipRole, RecordbookWriter
from docx import Document

def main():
    writer = RecordbookWriter("copy.docx")
    writer.append_leadership("Led U.S Pledge", LeadershipRole.APPOINTED, Level.CLUB, duties="")
    writer.append_service(ServiceRole.MEMBER, activity="Made masks for health workers", year="2020", impact="Served those on the front lines")

main()

