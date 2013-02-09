# -*- coding: utf-8 -*-

import os.path
import unittest
import shutil

from cert_gen import generador_csv
from cert_gen import generate_filename, certificates_generator
from cert_gen import all_students_certificates

from cert_gen import Certificate


class TestGeneradorCertificaciones(unittest.TestCase):

    def test_generador_csv(self):
        a, b = '1,2,3', '4,5,6'
        for r, e in zip(
            generador_csv(['a,b,c', a, b]),
            ({'a': '1', 'b': '2', 'c': '3'}, {'a': '4', 'b': '5', 'c': '6'})
            ):
            self.assertEqual(r, e)

    def test_genera_nombres(self):
        filename = generate_filename(
            "Asistencia",
            {
                "Apellido": u"Perez",
                "Nombre": "Juan",
                "Curso": "Introduccion a Scrum"
            }
        )
        self.assertEqual(
            filename,
            u"Kleer - Certificado Asistencia Introduccion a Scrum" +
            " - Juan Perez.pdf"
            )

    def test_no_tiene_columna_examen(self):
        students = [{'Curso': '', 'Nombre': '', 'Apellido': ''}]
        attendance_tmpl, certification_tmpl = '', ''
        all_students_certificates(students, attendance_tmpl, certification_tmpl)
        self.assertTrue(True)

### Unit Tests ####


class TestCertificate(unittest.TestCase):
    def setUp(self):
        self.certificate = Certificate()
        self.HTMLTEST = """
    <html><body>
    <p>Hello <strong style="color: #f00;">World</strong>
    <hr>
    <table border="1" style="background: #eee; padding: 0.5em;">
        <tr>
            <td>$Amount</td>
            <td>$Description</td>
            <td>Total</td>
        </tr>
        <tr>
            <td>1</td>
            <td>Good weather</td>
            <td>0 EUR</td>
        </tr>
        <tr style="font-weight: bold">
            <td colspan="2" align="right">Sum</td>
            <td>0 EUR</td>
        </tr>
    </table>
    </body></html>
    """

    def test_replace_one_variable(self):
        certificate = Certificate()
        certificate.template = "Are you $nombre?"
        modified = certificate.replace_variables(nombre="Juan")
        self.assertEqual("Are you Juan?", modified)

    def test_unknow_variable_raise_exception(self):
        certificate = Certificate()
        certificate.template = "Hola $nombre"
        with self.assertRaises(KeyError):
            certificate.replace_variables(pepe="Juan")

    def test_replace_2_variables(self):
        certificate = Certificate()
        certificate.template = "$que $nombre"
        modified = certificate.replace_variables(nombre="Juan", que="Hi")
        self.assertEqual("Hi Juan", modified)

    def test_generate_create_a_pdf(self):
        self.certificate.template = self.HTMLTEST
        out = "test.pdf"
        self.certificate.output_file = out
        if os.path.isfile(out):
            os.remove(out)
        ok = self.certificate.generate()
        self.assertTrue(ok)
        self.assertTrue(os.path.isfile(out))

    def test_make_output_dir(self):
        folder = "here"
        if os.path.exists(folder):
            shutil.rmtree(folder)
        Certificate(output_path=folder)
        self.assertTrue(os.path.isdir(folder))

    def test_read_templates_file(self):
        attended = "attended_tmpl.html"
        certificate = Certificate(template=attended)
        self.assertIn('<html>', certificate.template)


### Integration Tests ####


class IntegrationTest(unittest.TestCase):

    def test_integracion_basica(self):
        input = "input.csv"
        out = ("Kleer - Certificado Asistencia " +
            "Introduccion a Scrum - Juan Perez.pdf")
        attended = "attended_tmpl.html"
        certified = "certified_tmpl.html"
        output_path = ''
        if os.path.isfile(out):
            os.remove(out)

        certificates_generator(input, attended, certified, output_path)
        self.assertTrue(os.path.isfile(out), out)


if __name__ == '__main__':
    unittest.main()
