import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime

def get_candidate_odds():
    # Define slugs for different races
    dem_28 = 'democratic-presidential-nominee-2028'
    rep_28 = 'republican-presidential-nominee-2028'
    pres_28 = 'presidential-election-winner-2028'
    
    all_odds = {}
    
    # Manual name mapping for known variations (case-insensitive)
    name_mapping = {
        'jd vance': 'J.D. Vance',
        'j.d. vance': 'J.D. Vance',
        'stephen smith': 'Stephen A. Smith',
        'stephen a. smith': 'Stephen A. Smith',
        'jb pritzker': 'J.B. Pritzker',
        'j.b. pritzker': 'J.B. Pritzker',
        # Add more mappings if additional variations are identified
    }
    
    # Helper to safely get market "yes" probability
    def market_yes_prob(market):
        if 'outcomePrices' in market:
            prices = json.loads(market['outcomePrices'])
            yes_price = float(prices[0])
            no_price = float(prices[1])
            last_trade = market.get('lastTradePrice', 0.0) or 0.0
            if last_trade > 0:
                return float(last_trade)
            total = yes_price + no_price
            return (yes_price / total) if total > 0 else 0.0
        return 0.0

    # Get data for each race
    for slug in [dem_28, rep_28, pres_28]:
        url = f"https://gamma-api.polymarket.com/events?slug={slug}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Extract active markets
                active_markets = [m for m in data[0].get('markets', []) if m.get('active', False)]
                
                # Get odds for each candidate
                for market in active_markets:
                    name = market.get('groupItemTitle', 'Unknown')
                    name_lower = (name or '').lower()
                    standard_name = name_mapping.get(name_lower, name)
                    yes_odds = market_yes_prob(market)
                    
                    if standard_name not in all_odds:
                        all_odds[standard_name] = {'dem_odds': 0.0, 'rep_odds': 0.0, 'pres_odds': 0.0}
                    
                    if slug == dem_28:
                        if all_odds[standard_name]['dem_odds'] == 0.0:
                            all_odds[standard_name]['dem_odds'] = yes_odds
                    elif slug == rep_28:
                        if all_odds[standard_name]['rep_odds'] == 0.0:
                            all_odds[standard_name]['rep_odds'] = yes_odds
                    else:  # pres_28
                        if all_odds[standard_name]['pres_odds'] == 0.0:
                            all_odds[standard_name]['pres_odds'] = yes_odds
    
    # Convert to DataFrame (probabilities in 0..1)
    df = pd.DataFrame.from_dict(all_odds, orient='index').fillna(0.0)

    # Identify party based on which primary probability exists
    def infer_party(row):
        d, r = row['dem_odds'], row['rep_odds']
        if d > 0 and r == 0: return 'DEM'
        if r > 0 and d == 0: return 'GOP'
        if d > 0 and r > 0:  return 'BOTH'  # very rare, but handle gracefully
        return 'NONE'

    df['party'] = df.apply(infer_party, axis=1)

    # Choose appropriate primary probability for conditional calc
    primary_prob = np.where(df['party'] == 'DEM', df['dem_odds'],
                     np.where(df['party'] == 'GOP', df['rep_odds'], np.nan))
    
    # Conditional: P(President | win primary) ≈ P(President) / P(Primary)
    # If primary prob missing/zero, result is NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        df['cond_pres_given_primary'] = df['pres_odds'] / primary_prob

    # Convert to percentages
    percent_cols = ['dem_odds', 'rep_odds', 'pres_odds', 'cond_pres_given_primary']
    df[percent_cols] = df[percent_cols] * 100.0

    # Round and sort (optional: by presidency odds)
    df = df.round({'dem_odds': 2, 'rep_odds': 2, 'pres_odds': 2, 'cond_pres_given_primary': 2})
    df = df.sort_values('pres_odds', ascending=False)

    # Rename for clarity
    df = df.rename(columns={
        'dem_odds': 'Dem Primary %',
        'rep_odds': 'GOP Primary %',
        'pres_odds': 'President %',
        'cond_pres_given_primary': 'P(President | Win Primary) %'
    })

    return df
