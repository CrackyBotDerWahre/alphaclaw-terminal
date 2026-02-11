import json
import http.client
from datetime import datetime
import os

def fetch_and_update():
    try:
        conn = http.client.HTTPSConnection("api.coingecko.com")
        headers = {"User-Agent": "OpenClawAgent"}
        conn.request("GET", "/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true", headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        
        market = {
            "BTC": {"price": data["bitcoin"]["usd"], "change": round(data["bitcoin"]["usd_24h_change"], 2)},
            "ETH": {"price": data["ethereum"]["usd"], "change": round(data["ethereum"]["usd_24h_change"], 2)},
            "SOL": {"price": data["solana"]["usd"], "change": round(data["solana"]["usd_24h_change"], 2)}
        }
        
        # Update state.json at workspace root if possible, or local to script
        state_path = os.path.join(os.path.dirname(__file__), '..', 'state.json')
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
    fetch_and_update()
