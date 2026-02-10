import json
import os
from datetime import datetime

class TradingEngine:
    def __init__(self, state_path):
        self.state_path = state_path
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                return json.load(f)
        return {
            "portfolio": {"CASH": 100000.0},
            "history": [],
            "stats": {"totalValue": 100000.0, "profit": 0.0}
        }

    def _save_state(self):
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=2)

    def execute_trade(self, asset, amount, price, type="BUY"):
        if type == "BUY":
            cost = amount * price
            if self.state["portfolio"]["CASH"] >= cost:
                self.state["portfolio"]["CASH"] -= cost
                self.state["portfolio"][asset] = self.state["portfolio"].get(asset, 0) + amount
            else:
                return False, "Insufficient CASH"
        elif type == "SELL":
            if self.state["portfolio"].get(asset, 0) >= amount:
                gain = amount * price
                self.state["portfolio"]["CASH"] += gain
                self.state["portfolio"][asset] -= amount
            else:
                return False, f"Insufficient {asset}"
        
        self.state["history"].append({
            "asset": asset,
            "type": type,
            "amount": amount,
            "price": price,
            "timestamp": datetime.now().isoformat()
        })
        self._save_state()
        return True, "Trade Success"

if __name__ == "__main__":
    # Smoke test
    engine = TradingEngine('state.json')
    success, msg = engine.execute_trade("BTC", 0.5, 43000.0, "BUY")
    print(msg)
