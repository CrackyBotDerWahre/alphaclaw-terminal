import json
import requests
from datetime import datetime

def fetch_and_update():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url)
        data = response.json()
        
        market = {
            "BTC": {"price": data["bitcoin"]["usd"], "change": round(data["bitcoin"]["usd_24h_change"], 2)},
            "ETH": {"price": data["ethereum"]["usd"], "change": round(data["ethereum"]["usd_24h_change"], 2)},
            "SOL": {"price": data["solana"]["usd"], "change": round(data["solana"]["usd_24h_change"], 2)}
        }
        
        # Update state.json
        state_path = 'state.json'
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                state = json.load(f)
        else:
            state = {"portfolio": {"CASH": 100000.0}, "history": []}
            
        state["market"] = market
        state["updated_at"] = datetime.now().isoformat()
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
        print("Market data updated with REAL prices.")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    import os
    fetch_and_update()
