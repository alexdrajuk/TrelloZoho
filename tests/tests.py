import unittest


from zohotrello import utils
from zohotrello import settings
from zohotrello.zoho_api import ZohoAPI


class UtilsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('Start utils testing')

    @classmethod
    def tearDownClass(cls):
        print('Finish utils testing')

    def test_is_expense_leisure(self):
        self.assertTrue(utils.is_expense('leisure::50::велик'))

    def test_is_not_expense(self):
        self.assertFalse(utils.is_expense('хрень::50::помидоры'))

    def test_is_exchange(self):
        self.assertTrue(utils.is_exchange('exchange::$100-2650'))

    def test_is_not_exchange(self):
        self.assertFalse(utils.is_exchange('meals::200'))

    def test_is_assistant_transfer(self):
        self.assertTrue(utils.is_assistant_transfer('Anna::1400'))

    def test_is_not_assistant_transfer(self):
        self.assertFalse(utils.is_assistant_transfer('Meals::2000'))

    def test_is_expense_paid_by_ukrsib(self):
        self.assertEqual(
            utils.extract_comment_entities('meals::200::ukrsib').get('card'), 'ukrsib'
        )

    def test_is_expense_has_note(self):
        self.assertEqual(
            utils.extract_comment_entities('meals::200::Сильпо').get('note'), 'Сильпо'
        )

    def test_is_expense_paid_by_ukrsib_and_has_note(self):
        comment_entities = utils.extract_comment_entities('meals::200::ukrsib::Сильпо')
        self.assertTrue(
            comment_entities.get('card') == 'ukrsib' and comment_entities.get('note') == 'Сильпо'
        )

    def test_is_usd_amount(self):
        self.assertTrue(utils.is_usd_amount('$350'))

    def test_is_not_usd_amount(self):
        self.assertFalse(utils.is_usd_amount('350'))

    def test_is_eur_amount(self):
        self.assertTrue(utils.is_eur_amount('350eur'))

    def test_is_not_eur_amount(self):
        self.assertFalse(utils.is_eur_amount('$350'))


class ZohoSimpleAPITests(unittest.TestCase):
    zoho_api = ZohoAPI(
        client_id=settings.ZOHO_CLIENT_ID,
        client_secret=settings.ZOHO_CLIENT_SECRET,
        redirect_uri=settings.ZOHO_REDIRECT_URI,
        refresh_token=settings.ZOHO_REFRESH_TOKEN,
        organization_id=settings.ZOHO_ORGANIZATION_ID
    )

    @classmethod
    def setUpClass(cls):
        print('Start ZOHO Simple API Testing testing')

    @classmethod
    def tearDownClass(cls):
        print('Finish ZOHO Simple API Testing')

    def test_get_expense_account_by_name(self):
        account = self.__class__.zoho_api.get_expense_account_by_name("Automobile Expense")
        self.assertEqual(account.get("account_name"), "Automobile Expense")

    def test_get_currency_by_code(self):
        currency = self.__class__.zoho_api.get_currency_by_code('UAH')
        self.assertEqual(currency.get('currency_code'), 'UAH')


class ZohoExternalAPITests(unittest.TestCase):
    zoho_api = ZohoAPI(
        client_id=settings.ZOHO_CLIENT_ID,
        client_secret=settings.ZOHO_CLIENT_SECRET,
        redirect_uri=settings.ZOHO_REDIRECT_URI,
        refresh_token=settings.ZOHO_REFRESH_TOKEN,
        organization_id=settings.ZOHO_ORGANIZATION_ID
    )

    @classmethod
    def setUpClass(cls):
        print('Start ZOHO External API Testing testing')

    @classmethod
    def tearDownClass(cls):
        print('Finish ZOHO External ZOHO API Testing')

    def test_get_expense_account_by_name(self):
        account = self.__class__.zoho_api.get_expense_account_by_name("Automobile Expense")
        self.assertEqual(account.get("account_name"), "Automobile Expense")


if __name__ == "__main__":
    unittest.main()
