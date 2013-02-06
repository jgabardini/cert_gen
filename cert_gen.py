# -*- coding: utf-8 -*-
# Authors: Juan Gabardini y Pablo Tortorella
#

from string import Template
import csv

from xhtml2pdf import pisa
import cStringIO as StringIO

# Shortcut for dumping all logs to the screen
pisa.showLogging()

_FIRST_NAME = 'Nombre'
_LAST_NAME = 'Apellido'
_COURSE_NAME = 'Curso'
_TOOK_EXAM = 'Examen'


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
    return "Kleer - Certificado %s %s - %s %s.pdf" % (
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


def certificates_generator(input):
    students = generador_csv(open(input))
    with open("template - asistencia.html") as template:
        attendance_tmpl = template.read()
    with open("template - examen.html") as template:
        certification_tmpl = template.read()
    all_students_certificates(students, attendance_tmpl, certification_tmpl)


def help():
    print("""
Uso: cert_gen <alumnos.csv>
    csv: separado por comas, con al menos las columnas Curso, Nombre, Apellido
    utiliza "template - asistencia.html" y "template - examen.html"
""")

if __name__ == '__main__':
    import sys

    if (len(sys.argv) <= 1):
        help()
    else:
        print("Procesando %s" % sys.argv[1])
        certificates_generator(sys.argv[1])
