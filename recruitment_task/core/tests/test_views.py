from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone

from core.models import Investor, Project


def set_up_test_case_data(self):

        self.good_project = Project.objects.create(
            name='good_project', 
            description='description', 
            amount=500,
            delivery_date=
                    timezone.now() + timezone.timedelta(days=20)
            )

        self.bad_project = Project.objects.create(
                name='bad_project', 
                description='description', 
                amount=10000,
                delivery_date=
                        timezone.now() + timezone.timedelta(days=365)
                )

        self.good_investor = Investor.objects.create(
                name='good_investor',
                total_amount=100000,
                individual_amount=1000,
                project_delivery_deadline=
                        timezone.now() + timezone.timedelta(days=22)
                )   

        self.bad_investor = Investor.objects.create(
                name='bad_investor',
                total_amount=1,
                individual_amount=1,
                project_delivery_deadline=
                        timezone.now() + timezone.timedelta(days=1)
                )   


class InvestorDetailsViewTestCase(TestCase):
    @staticmethod
    def _get_url(investor_id):
        return f'/investors/{investor_id}/'

    def setUp(self) -> None:
        set_up_test_case_data(self)
    
        
        self.client = APIClient()

    def test_get(self):

        url = self._get_url(self.good_investor.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        investor_data = response.data

        self.assertEqual(investor_data['id'], self.good_investor.id)
        self.assertEqual(investor_data['name'], self.good_investor.name)
        self.assertEqual(investor_data['matching_projects'], [self.good_project.id])


class ProjectDetailsViewTestCase(TestCase):
    @staticmethod
    def _get_url(investor_id):
        return f'/projects/{investor_id}/'

    def setUp(self) -> None:
        set_up_test_case_data(self)
        
        self.client = APIClient()

    def test_get(self):
        url = self._get_url(self.good_project.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project_data = response.data

        self.assertEqual(project_data['id'], self.good_project.id)
        self.assertEqual(project_data['name'], self.good_project.name)
        self.assertEqual(
                project_data['matching_investors'],
                [self.good_investor.id]
                )


class InvestingTestCase(TestCase):

    @staticmethod
    def _get_url(investor_id, project_id):
        return f'/investors/{investor_id}/invest/{project_id}/'


    def setUp(self) -> None:
        set_up_test_case_data(self)
    
    def test_investing(self):
        
        good_url = self._get_url(self.good_investor.id, self.good_project.id)
        bad_url = self._get_url(self.good_investor.id, self.bad_project.id)
        good_response = self.client.post(good_url)
        bad_response = self.client.post(bad_url)

        invested_good_project = Project.objects.get(id = self.good_project.id)
        invested_bad_project = Project.objects.get(id = self.bad_project.id)
        invested_good_investor = Investor.objects.get(id = self.good_investor.id)

        self.assertTrue(invested_good_project.funded)
        self.assertFalse(invested_bad_project.funded)
        
        self.assertEqual(
                invested_good_project.funded_by.id,
                self.good_investor.id
                )
        self.assertEqual(
                invested_good_investor.remaining_amount,
                self.good_investor.total_amount - self.good_project.amount
                )
        
        self.assertEqual(good_response.status_code, 200)   
        self.assertEqual(bad_response.status_code, 400)   
