# -*- coding: utf-8 -*-
# Authors: Juan Gabardini y Pablo Tortorella
#

from string import Template
import csv
import os

from xhtml2pdf import pisa
import cStringIO as StringIO

# Shortcut for dumping all logs to the screen
pisa.showLogging()

_FIRST_NAME = 'Nombre'
_LAST_NAME = 'Apellido'
_COURSE_NAME = 'Curso'
_TOOK_EXAM = 'Examen'

PDF_PATH = ''


def HTML2PDF(data, filename, open=False):
    """
    Create a PDF file from PML Source String.
    Also shows errors and tries to start the resulting PDF
    """

    pdf = pisa.CreatePDF(
        StringIO.StringIO(data),
        file(filename, "wb"))

    if open and (not pdf.err):
        pisa.startViewer(filename)

    return not pdf.err


def reemplazar(base, **kws):
    return Template(base).substitute(kws)


def generador_csv(csv_file):
    reader = csv.DictReader(csv_file)
    try:
        for row in reader:
            yield row
    except csv.Error, e:
        sys.exit('line %d: %s' % (reader.line_num, e))


def generate_filename(type, student):
    path = PDF_PATH + (
            '/' if len(PDF_PATH) > 0 and PDF_PATH[-1] != '/' else ''
            )
    return "%sKleer - Certificado %s %s - %s %s.pdf" % (
        path,
        type,
        student[_COURSE_NAME],
        student[_FIRST_NAME],
        student[_LAST_NAME]
    )


def certificate_generator(html, type, student):
    certificado = reemplazar(base=html, **student)
    HTML2PDF(certificado, generate_filename(type, student), open=False)


def all_students_certificates(students, attendance_tmpl, certification_tmpl):
    """
    Generate one or two pdf for each student
    Expect
        a iterable with a dict for each student
        two html templates
    """
    for student in students:
        certificate_generator(attendance_tmpl, "Asistencia", student)
        if _TOOK_EXAM in student and student[_TOOK_EXAM].lower() == "si":
            certificate_generator(certification_tmpl, "Examen", student)


def certificates_generator(student_file):
    print("Procesando %s con path %s" % (student_file, PDF_PATH) )
    students = generador_csv(open(student_file))
    with open("template - asistencia.html") as template:
        attendance_tmpl = template.read()
    with open("template - examen.html") as template:
        certification_tmpl = template.read()
    if (PDF_PATH != '') and not os.path.exists(PDF_PATH):
        os.makedirs(PDF_PATH)

    all_students_certificates(students, attendance_tmpl, certification_tmpl)


def help():
    print("""
Uso: cert_gen <alumnos.csv> <path_pdf>
    <alumnos.csv>: lista de alumnos, separado por comas,
    con al menos las columnas Curso, Nombre, Apellido
    utiliza "template - asistencia.html"
    Opcionalmente, si existe la columna Examen, en los casos en que tenga 'si'
    se genera un pdf adicional utilizando "template - examen.html"
""")


class Certificate():
    "create a pdf using templates and variables"
    def __init__(self):
        self.template = ''

    def replace_variables(self, **kws):
        return Template(self.template).substitute(kws)

if __name__ == '__main__':
    import sys

    if (len(sys.argv) <= 1):
        help()
    else:
        student_file = sys.argv[1]
        PDF_PATH = '' if len(sys.argv) == 2 else sys.argv[2]
        certificates_generator(student_file)
