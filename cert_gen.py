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


def generador_csv(csv_file):
    reader = csv.DictReader(csv_file)
    try:
        for row in reader:
            yield row
    except csv.Error as e:
        sys.exit('line %d: %s' % (reader.line_num, e))


def generate_filename(type, output_path, student):
    path = output_path + (
            '/' if len(output_path) > 0 and output_path[-1] != '/' else ''
            )
    return "%sKleer - Certificado %s %s - %s %s.pdf" % (
        path,
        type,
        student[_COURSE_NAME],
        student[_FIRST_NAME],
        student[_LAST_NAME]
    )


def sanitize_dict(d):
    return {k.strip():v for (k, v) in d.iteritems()}


def all_students_certificates(students, attended_cert, certified_cert):
    """
    Generate one or two pdf for each student
    Expect
        a iterable with a dict for each student
        two html templates
    """
    for student in students:
        clean_s = sanitize_dict(student)
        attended_cert.generate(**clean_s)
        if _TOOK_EXAM in clean_s and clean_s[_TOOK_EXAM].lower() == "si":
            certified_cert.generate(**clean_s)


def certificates_generator(
        students_file,
        attended_tmpl,
        certified_tmpl,
        output_path
        ):

    print("Procesando %s con path %s" % (students_file, output_path))
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
    all_students_certificates(students, attended_cert, certified_cert)


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
        output_file = generate_filename(self.type, self.output_path, kws)
        self.replace_variables(**kws)
        pdf = pisa.CreatePDF(
                StringIO.StringIO(self.output),
                file(output_file, "wb")
                )
        return output_file if not pdf.err else None


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
