import json
import os
import sys
from datetime import datetime

def update_without_requests():
    # Preisdaten wurden via curl in temp_price.json geladen
    temp_file = 'temp_price.json'
    state_path = 'state.json'
    
    if not os.path.exists(temp_file):
        print("Error: temp_price.json not found")
        return

    with open(temp_file, 'r') as f:
        data = json.load(f)
    
    market = {
        "BTC": {"price": data["bitcoin"]["usd"], "change": round(data["bitcoin"]["usd_24h_change"], 2)},
        "ETH": {"price": data["ethereum"]["usd"], "change": round(data["ethereum"]["usd_24h_change"], 2)},
        "SOL": {"price": data["solana"]["usd"], "change": round(data["solana"]["usd_24h_change"], 2)}
    }
    
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            state = json.load(f)
    else:
        state = {"portfolio": {"CASH": 100000.0}, "history": []}
        
    state["market"] = market
    state["updated_at"] = datetime.now().isoformat()
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    print("Market data updated with REAL prices via core bridge.")

if __name__ == "__main__":
    update_without_requests()
