from django.test import TestCase
from django.utils import timezone

from core.tests.test_views import set_up_test_case_data

class MatchmakingTestCase(TestCase):

    @staticmethod
    def _get_url(id, type):
        return f'/{type}/{id}/matches'


    def setUp(self) -> None:
        set_up_test_case_data(self)
    
    def test_matchmaking_for_project(self):
        
        url = self._get_url(1, 'investors')
        response = self.client.get(url)
        matches_data = response.data

        self.assertEqual(len(matches_data), 1)
        self.assertEqual(matches_data[0]['id'], self.good_investor.id)
        self.assertEqual(response.status_code, 200)   


    def test_matchmaking_for_investor(self):
    
        url = self._get_url(1, 'projects')
        response = self.client.get(url)
        matches_data = response.data

        self.assertEqual(len(matches_data), 1)
        self.assertEqual(matches_data[0]['id'], self.good_project.id)
        self.assertEqual(response.status_code, 200)   
