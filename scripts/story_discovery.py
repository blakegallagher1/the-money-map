"""
Module 2: Story Discovery — Analyzes fresh data to find the most compelling narrative.
Scores each potential story by viral potential, then picks the best one.
"""
import json
import os
from datetime import datetime
from typing import List, Tuple

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import FRED_SERIES


def analyze_data(data_path: str) -> dict:
    """Load fresh data and score every series for story potential."""
    with open(data_path) as f:
        raw = json.load(f)
    
    stories = []
    data = raw["data"]
    
    for key, d in data.items():
        if d.get("yoy_pct") is None:
            continue
        
        abs_pct = abs(d["yoy_pct"])
        score = 0
        tags = []
        
        if abs_pct > 20:
            score += 40
            tags.append("dramatic_change")
        elif abs_pct > 10:
            score += 30
            tags.append("significant_change")
        elif abs_pct > 5:
            score += 20
            tags.append("notable_change")
        elif abs_pct > 2:
            score += 10
            tags.append("moderate_change")
        
        high_interest = ["median_home_price", "mortgage_rate_30yr", "gas_price", 
                        "unemployment_rate", "cpi", "personal_savings_rate",
                        "rent_cpi", "credit_card_delinquency", "national_debt",
                        "student_loan_debt", "median_income", "consumer_confidence"]
        if key in high_interest:
            score += 25
            tags.append("high_public_interest")
        
        medium_interest = ["case_shiller", "housing_starts", "building_permits",
                          "labor_force_participation", "fed_funds_rate", "auto_loan_debt",
                          "home_ownership_rate", "rental_vacancy", "consumer_spending"]
        if key in medium_interest:
            score += 15
            tags.append("medium_public_interest")
        
        consumer_bad_when_up = ["cpi", "cpi_food", "cpi_energy", "gas_price", 
                                "rent_cpi", "credit_card_delinquency", "national_debt",
                                "student_loan_debt", "mortgage_rate_30yr"]
        consumer_bad_when_down = ["median_income", "personal_savings_rate", 
                                  "home_ownership_rate", "labor_force_participation",
                                  "consumer_confidence"]
        
        if (key in consumer_bad_when_up and d["yoy_pct"] > 5) or \
           (key in consumer_bad_when_down and d["yoy_pct"] < -5):
            score += 15
            tags.append("consumer_pain_point")
        
        try:
            data_date = datetime.strptime(d["latest_date"], "%Y-%m-%d")
            days_old = (datetime.now() - data_date).days
            if days_old < 30:
                score += 10
                tags.append("very_fresh")
            elif days_old < 90:
                score += 5
                tags.append("recent")
        except:
            pass
        
        stories.append({
            "key": key,
            "name": d["name"],
            "series_id": d["series_id"],
            "unit": d["unit"],
            "latest_value": d["latest_value"],
            "latest_date": d["latest_date"],
            "yoy_change": d["yoy_change"],
            "yoy_pct": d["yoy_pct"],
            "prev_year_value": d["prev_year_value"],
            "score": score,
            "tags": tags,
        })
    
    stories.sort(key=lambda x: x["score"], reverse=True)
    return {"stories": stories, "top_story": stories[0] if stories else None}


def find_related_series(primary_key: str, all_data: dict) -> List[dict]:
    """Find 2-3 related series that add context to the primary story."""
    relations = {
        "median_home_price": ["mortgage_rate_30yr", "housing_starts", "home_ownership_rate", "case_shiller"],
        "mortgage_rate_30yr": ["median_home_price", "housing_starts", "fed_funds_rate"],
        "gas_price": ["cpi_energy", "cpi", "consumer_confidence"],
        "unemployment_rate": ["initial_claims", "job_openings", "labor_force_participation"],
        "cpi": ["cpi_food", "cpi_energy", "fed_funds_rate", "gas_price"],
        "personal_savings_rate": ["consumer_spending", "consumer_credit", "median_income"],
        "rent_cpi": ["rental_vacancy", "median_home_price", "median_income"],
        "credit_card_delinquency": ["consumer_credit", "fed_funds_rate", "personal_savings_rate"],
        "national_debt": ["fed_funds_rate", "treasury_10yr", "gdp_growth"],
        "student_loan_debt": ["consumer_credit", "credit_card_delinquency", "median_income"],
        "median_income": ["cpi", "unemployment_rate", "personal_savings_rate"],
        "consumer_confidence": ["unemployment_rate", "cpi", "gas_price", "personal_savings_rate"],
        "fed_funds_rate": ["treasury_10yr", "mortgage_rate_30yr", "cpi"],
        "housing_starts": ["building_permits", "median_home_price", "mortgage_rate_30yr"],
        "case_shiller": ["median_home_price", "mortgage_rate_30yr", "rent_cpi"],
        "home_ownership_rate": ["median_home_price", "mortgage_rate_30yr", "median_income"],
        "gdp_growth": ["consumer_spending", "unemployment_rate", "consumer_confidence"],
        "labor_force_participation": ["unemployment_rate", "median_income", "job_openings"],
        "auto_loan_debt": ["consumer_credit", "credit_card_delinquency"],
        "building_permits": ["housing_starts", "median_home_price"],
        "rental_vacancy": ["rent_cpi", "median_home_price"],
        "consumer_spending": ["personal_savings_rate", "consumer_credit", "cpi"],
    }
    
    related_keys = relations.get(primary_key, [])
    related = []
    for rk in related_keys[:3]:
        if rk in all_data:
            related.append(all_data[rk])
    return related


def build_story_package(data_path: str) -> dict:
    """Full pipeline: analyze data → pick best story → gather context → return package."""
    with open(data_path) as f:
        raw = json.load(f)
    
    analysis = analyze_data(data_path)
    top = analysis["top_story"]
    
    if not top:
        raise ValueError("No stories found in data")
    
    related = find_related_series(top["key"], raw["data"])
    
    package = {
        "primary": top,
        "related": related,
        "all_ranked": analysis["stories"][:10],
        "generated_at": datetime.now().isoformat(),
    }
    
    return package


if __name__ == "__main__":
    pkg = build_story_package("/home/user/workspace/the-money-map/data/latest_data.json")
    print(f"\n🎯 TOP STORY: {pkg['primary']['name']}")
    print(f"   Latest: {pkg['primary']['latest_value']} {pkg['primary']['unit']}")
    print(f"   YoY Change: {pkg['primary']['yoy_pct']:+.1f}%")
    print(f"   Score: {pkg['primary']['score']}")
    print(f"   Tags: {', '.join(pkg['primary']['tags'])}")
    print(f"\n📊 Related Context:")
    for r in pkg['related']:
        print(f"   - {r['name']}: {r['latest_value']} ({r.get('yoy_pct', 'N/A')}% YoY)")
    print(f"\n📋 Top 5 Ranked Stories:")
    for s in pkg['all_ranked'][:5]:
        print(f"   [{s['score']}] {s['name']}: {s['yoy_pct']:+.1f}%")
