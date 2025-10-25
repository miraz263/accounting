from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Company, Account, JournalEntry, JournalLine
from rest_framework.test import APIClient

User = get_user_model()

class LedgerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u','u@x.com','pwd')
        self.company = Company.objects.create(name='C1')
        self.acc1 = Account.objects.create(company=self.company, code='1000', name='Cash', type='asset')
        self.acc2 = Account.objects.create(company=self.company, code='2000', name='Sales', type='income')
        self.client = APIClient()
        res = self.client.post('/api/token/', {'username':'u','password':'pwd'}, format='json')
        self.token = res.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # একটি balanced journal তৈরি
        payload = {
            "company": self.company.id,
            "date": "2025-10-25",
            "narration":"Test Entry",
            "lines":[
                {"account": self.acc1.id, "debit":"100.00", "credit":"0"},
                {"account": self.acc2.id, "debit":"0", "credit":"100.00"}
            ]
        }
        self.client.post('/api/journal-entries/', payload, format='json')

    def test_ledger_api(self):
        res = self.client.get(f'/api/ledger/{self.acc1.id}/')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(float(data[0]['debit']), 100.00)
        self.assertEqual(float(data[0]['credit']), 0.00)
        self.assertEqual(data[0]['narration'], "Test Entry")
