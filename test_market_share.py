import unittest
from datahandler import modifyMonthlyData2020, importMonthlyData


class MyTestCase(unittest.TestCase):
    def test_monthly_market_share(self):
        monthlyNEW, monthlyOLD = importMonthlyData()
        monthlydata = modifyMonthlyData2020(monthlyNEW, monthlyOLD)
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
