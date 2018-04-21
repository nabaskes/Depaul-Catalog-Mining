import requests
import sqlite3

db = sqlite3.connect('catalog.db')


def get_course(term, subject, catalog_number):
    url_prefix = 'https://resources.depaul.edu/_layouts/DUC.SR.ClassSvc/DUClassSvc.ashx?action='
    url = url_prefix+"getcourse&strm="+str(term)+"&subject="+str(subject)+"&catalog_nbr="+str(catalog_number)
    resp = requests.get(url).json()
    return resp


def get_subjects(strm):
    url = 'https://resources.depaul.edu/_layouts/DUC.SR.ClassSvc/DUClassSvc.ashx?action=searchclassbysubject&strm='+str(strm)+'&subject=all&catalog_nbr=&acad_org=all&acad_career=all'
    resp = requests.get(url)
    data = resp.json()
    c = db.cursor()

    for subject in data:
        dept = subject['descr'].replace("'", "")
        subj = subject['subject']
        for course in subject['classes']:
            cat_num = course['catalog_nbr']
            title = course['descr'].replace("'", "")
            term = course['strm']
            print(f"{title} {term}")
            c.execute(f"""INSERT INTO Classes
            (Department, Subject, Term, Title, CatalogNumber)
            VALUES ('{dept}','{subj}','{term}','{title}','{cat_num}');""")
        db.commit()


if __name__ == "__main__":
    for strm in ['1000', '1005', '1010', '1015', '1020', '1024']:
        get_subjects(strm)
    c = db.cursor()
    c.execute("""SELECT Term, Subject, CatalogNumber
    FROM classes
    WHERE Description is NULL;""")
    result = c.fetchall()
    for cls in result:
        course = get_course(*cls)
        description = course['descrlong'].replace("'", "") if course['descrlong'] else None
        if description is None:
            continue
        print(cls)
        c.execute(f"""UPDATE Classes
        SET Description='{description}'
        WHERE CatalogNumber='{cls[2]}'
        AND Term='{cls[0]}'
        AND Subject='{cls[1]}'
        AND Description is null;""")
        db.commit()
