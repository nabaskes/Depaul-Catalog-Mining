import requests
import sqlite3

conn = sqlite3.connect('catalog.db')
url_prefix = 'https://csh.depaul.edu/_layouts/DUC.SR.ClassSvc/DUClassSvc.ashx?action='

# these correspond with 2018 fall, winter, spring for some reason
terms = [1000, 1005, 1010]
subjects = ['PHY', 'BIO', 'CHE', 'ENV', 'HLTH']


def get_classes(subject, term):
    url = url_prefix + 'searchclassbysubject&strm='+str(term)+'&subject='+str(subject)+'catalog_nbr=&acad_org=556100&acad_career=all'
    resp = requests.get(url).json()
    return resp


def get_course(term, subject, catalog_number):
    url = url_prefix+"getcourse&strm="+str(term)+"&subject="+str(subject)+"&catalog_nbr="+str(catalog_number)
    print(url)
    resp = requests.get(url).json()
    return resp


if __name__ == "__main__":
    cursor = conn.cursor()
    catalog = []
    for term in terms:
        catalog = get_classes(subjects[0], term)
        for department in catalog:
            dept = department['descr']
            subj = department['subject']
            for course in department['classes']:
                catalog_number = course['catalog_nbr'].replace("'", "")
                title = course['descr'].replace("'", "")
                course_data = get_course(term, subj, catalog_number)
                try:
                    descr = course_data['descrlong']
                    if descr:
                        descr = descr.replace("'", "")
                except KeyError:
                    descr = None
                try:
                    term_title = course_data.get('terms')[0]['descr'].replace("'", "")
                except IndexError:
                    term_title = None
                cursor.execute(f"""INSERT INTO Courses
                (Department, Subject, Term, Title,
                CatalogNumber, Description, TermTitle, DIVISION)
                VALUES ('{dept}', '{subj}', '{term}', '{title}',
                '{catalog_number}', '{descr}', '{term_title}', 'CSH');""")
            conn.commit()
