import sqlite3
import json
import os
from datetime import datetime

class AlphaDB:
    def __init__(self, db_path='trading.db'):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                            asset TEXT PRIMARY KEY,
                            amount REAL DEFAULT 0,
                            avg_price REAL DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS trades (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            asset TEXT,
                            type TEXT,
                            amount REAL,
                            price REAL,
                            ts DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_data (
                            asset TEXT PRIMARY KEY,
                            price REAL,
                            change_24h REAL,
                            last_update DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Initial funding
        cursor.execute("INSERT OR IGNORE INTO portfolio (asset, amount, avg_price) VALUES ('CASH', 100000.0, 1.0)")
        self.conn.commit()

    def get_portfolio(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT asset, amount, avg_price FROM portfolio")
        return {row[0]: {"amount": row[1], "avg_price": row[2]} for row in cursor.fetchall()}

    def update_market(self, asset, price, change):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO market_data (asset, price, change_24h) VALUES (?, ?, ?)", (asset, price, change))
        self.conn.commit()

    def execute_trade(self, asset, amount, price, side='BUY'):
        cursor = self.conn.cursor()
        portfolio = self.get_portfolio()
        cash = portfolio.get('CASH', {'amount': 0})['amount']
        
        if side == 'BUY':
            cost = amount * price
            if cash < cost: return False, "Insufficient funds"
            new_cash = cash - cost
            current_asset = portfolio.get(asset, {'amount': 0, 'avg_price': 0})
            new_amount = current_asset['amount'] + amount
            new_avg = ((current_asset['amount'] * current_asset['avg_price']) + cost) / new_amount
            cursor.execute("UPDATE portfolio SET amount = ? WHERE asset = 'CASH'", (new_cash,))
            cursor.execute("INSERT OR REPLACE INTO portfolio (asset, amount, avg_price) VALUES (?, ?, ?)", (asset, new_amount, new_avg))
        else:
            current_asset = portfolio.get(asset, {'amount': 0})
            if current_asset['amount'] < amount: return False, f"Insufficient {asset}"
            gain = amount * price
            new_cash = cash + gain
            new_amount = current_asset['amount'] - amount
            cursor.execute("UPDATE portfolio SET amount = ? WHERE asset = 'CASH'", (new_cash,))
            cursor.execute("UPDATE portfolio SET amount = ? WHERE asset = ?", (new_amount, asset))

        cursor.execute("INSERT INTO trades (asset, type, amount, price) VALUES (?, ?, ?, ?)", (asset, side, amount, price))
        self.conn.commit()
        return True, "Success"

    def export_state_json(self, output_path='state.json'):
        cursor = self.conn.cursor()
        cursor.execute("SELECT asset, amount, avg_price FROM portfolio")
        portfolio = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT asset, type, amount, price, ts FROM trades ORDER BY ts DESC LIMIT 20")
        history = [{"asset": r[0], "type": r[1], "amount": r[2], "price": r[3], "ts": r[4]} for r in cursor.fetchall()]
        cursor.execute("SELECT asset, price, change_24h FROM market_data")
        market = {row[0]: {"price": row[1], "change": row[2]} for row in cursor.fetchall()}
        
        state = {
            "portfolio": portfolio,
            "history": history,
            "market": market,
            "updated_at": datetime.now().isoformat()
        }
        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2)
