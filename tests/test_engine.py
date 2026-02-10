import unittest
import os
import json
from core.engine import TradingEngine

class TestTradingEngine(unittest.TestCase):
    def setUp(self):
        self.test_db = 'test_state.json'
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.engine = TradingEngine(self.test_db)

    def test_buy_success(self):
        success, msg = self.engine.execute_trade("BTC", 1, 40000.0, "BUY")
        self.assertTrue(success)
        self.assertEqual(self.engine.state["portfolio"]["CASH"], 60000.0)
        self.assertEqual(self.engine.state["portfolio"]["BTC"], 1)

    def test_insufficient_funds(self):
        success, msg = self.engine.execute_trade("BTC", 10, 20000.0, "BUY")
        self.assertFalse(success)
        self.assertEqual(msg, "Insufficient CASH")

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

if __name__ == '__main__':
    unittest.main()
