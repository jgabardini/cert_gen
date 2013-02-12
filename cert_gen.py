# -*- coding: utf-8 -*-
# Authors: Juan Gabardini y Pablo Tortorella
#

from string import Template
import csv
import os
import sys
import argparse

from xhtml2pdf import pisa
import cStringIO as StringIO

# Shortcut for dumping all logs to the screen
pisa.showLogging()

_FIRST_NAME = 'Nombre'
_LAST_NAME = 'Apellido'
_COURSE_NAME = 'Curso'
_TOOK_EXAM = 'Examen'

PDF_PATH = ''


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
    certificate = Certificate()
    certificate.template = html
    certificate.output_file = generate_filename(type, student)
    certificate.generate(**student)


def x_all_students_certificates(students, attendance_tmpl, certification_tmpl):
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


def all_students_certificates2(students, attended_cert, certified_cert):
    """
    Generate one or two pdf for each student
    Expect
        a iterable with a dict for each student
        two html templates
    """
    for student in students:
        attended_cert.generate(**student)
        if _TOOK_EXAM in student and student[_TOOK_EXAM].lower() == "si":
            certified_cert.generate(**student)


def x_certificates_generator(
        students_file,
        attended_tmpl,
        certified_tmpl,
        output_path
        ):

    PDF_PATH = output_path

    print("Procesando %s con path %s" % (students_file, PDF_PATH))
    students = generador_csv(open(students_file))
    with open(attended_tmpl) as template:
        attendance_tmpl = template.read()
    with open(certified_tmpl) as template:
        certification_tmpl = template.read()
    if (PDF_PATH != '') and not os.path.exists(PDF_PATH):
        os.makedirs(PDF_PATH)

    # all_students_certificates(students, attendance_tmpl, certification_tmpl)


def certificates_generator(
        students_file,
        attended_tmpl,
        certified_tmpl,
        output_path
        ):

    PDF_PATH = output_path

    print("Procesando %s con path %s" % (students_file, PDF_PATH))
    students = generador_csv(open(students_file))
    attended_cert = Certificate(
            output_path=output_path,
            template=attended_tmpl,
            type='Asistencia'
        )
    certified_cert = Certificate(
            output_path=output_path,
            template=certified_tmpl,
            type='Examen'
        )
    all_students_certificates2(students, attended_cert, certified_cert)


class Certificate():
    "create a pdf using templates and variables"
    def __init__(self, output_path='', template=None, type=''):
        if template:
            with open(template) as template_file:
                self.template = template_file.read()
        else:
            self.template = ''

        self.output_file = ''
        self.output = ''
        self.type = type
        if (output_path != '') and not os.path.exists(output_path):
            os.makedirs(output_path)
        self.output_path = output_path

    def replace_variables(self, **kws):
        if len(kws) == 0:
            self.output = self.template
        else:
            self.output = Template(self.template).substitute(kws)

        return self.output

    def generate(self, **kws):
        self.output_file = generate_filename(self.type, kws)
        self.replace_variables(**kws)
        pdf = pisa.CreatePDF(
                StringIO.StringIO(self.output),
                file(self.output_file, "wb")
                )
        return not pdf.err


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="""Create one or two pdf for each student
    \n
    Utiliza "template - asistencia.html"
    Opcionalmente, si existe la columna Examen, en los casos en que tenga 'si'
    se genera un pdf adicional utilizando "template - examen.html"

        """
        )

    parser.add_argument('students', help="""
        csv de alumnos, con al menos las columnas Curso, Nombre, Apellido
        """
        )

    parser.add_argument('-o', '--output_path', default='',
        help='folder where the pdf will be created'
        )

    parser.add_argument('-a', '--attended', default='attended_tmpl.html',
        help='html template for attended'
        )

    parser.add_argument('-c', '--certified', default='certified_tmpl.html',
        help='html template for a certification'
        )

    args = parser.parse_args()
    certificates_generator(
        students_file = args.students,
        attended_tmpl = args.attended,
        certified_tmpl =args.certified,
        output_path = args.output_path
        )
