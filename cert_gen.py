# -*- coding: utf-8 -*-

from string import Template
import csv

from xhtml2pdf import pisa
import cStringIO as StringIO

# Shortcut for dumping all logs to the screen
pisa.showLogging()

def HTML2PDF(data, filename, open=False):
    """
    Simple test showing how to create a PDF file from
    PML Source String. Also shows errors and tries to start
    the resulting PDF
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
        student["Curso"],
        student["Nombre"],
        student["Apellido"]
    )


def certificate_generator(html, type, student):
    certificado = reemplazar(base=html, **student)
    HTML2PDF(certificado, generate_filename(type, student), open=False)

def certificates_generator(input):
    alumnos = generador_csv(open(input))
    with open("template - asistencia.html") as template:
        html_asistencia = template.read()
    with open("template - examen.html") as template:
        html_examen = template.read()

    for alumno in alumnos:
        certificate_generator(html_asistencia, "Asistencia", alumno)
        if alumno["Examen"].lower()=="si":
            certificate_generator(html_examen, "Examen", alumno)

if __name__ == '__main__':
    import sys

    if (len(sys.argv) <= 1):
        print "Uso: cert_gen <alumnos.csv>"
    else:
        print("Procesando %s" % sys.argv[1])
        certificates_generator(sys.argv[1])
