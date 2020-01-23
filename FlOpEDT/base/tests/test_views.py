import unittest
import base.models as models

from django.test import Client, SimpleTestCase
from django.urls import reverse


class IndexViewTest(unittest.TestCase):
    
    def setUp(self):
        # Every test needs a client.
        self.client = Client()
        models.Department.objects.all().delete()

    def test_first_department_creation(self):
        # Issue a GET request.
        count_before = models.Department.objects.count()
        response = self.client.get('/')
        count_after =  models.Department.objects.count()
        
        self.assertEqual(count_before, 0)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], reverse('base:edt'))
        self.assertEqual(count_after, 1)

    def test_single_department_redirection(self):
        self.d1 = models.Department.objects.create(name="departement1", abbrev="d1")
        response = self.client.get('/')
        self.assertEqual(response['location'], reverse('base:edt', kwargs={'department': self.d1.abbrev}))
        self.assertEqual(response.status_code, 302)

    def test_mnay_department_redirection(self):
        self.d1 = models.Department.objects.create(name="departement1", abbrev="d1")
        self.d2 = models.Department.objects.create(name="departement2", abbrev="d2")
        response = self.client.get('/')
        self.assertEqual(response.content.decode(), "NOT IMPLEMENTED YET")