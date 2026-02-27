"""
Module 3: Script Writer — Generates an engaging, data-driven narration script.
Each script follows a proven YouTube structure: Hook → Context → Data Deep-Dive → Insight → Call-to-Action.
"""
import json
import os
from datetime import datetime


def format_number(value: float, unit: str) -> str:
    """Format numbers for spoken narration."""
    if unit == "$":
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:.1f} trillion"
        if value >= 1_000_000:
            return f"${value/1_000_000:.1f} trillion"
        if value >= 1_000:
            return f"${value:,.0f}"
        return f"${value:.2f}"
    if unit == "billions $":
        if value >= 1000:
            return f"${value/1000:.1f} trillion"
        if value >= 1:
            return f"${value:,.0f} billion"
        return f"${value:.2f} billion"
    if unit == "millions $":
        if value >= 1_000_000:
            return f"${value/1_000_000:.1f} trillion"
        if value >= 1_000:
            return f"${value/1000:,.0f} billion"
        return f"${value:,.0f} million"
    if unit == "%":
        return f"{value:.1f} percent"
    if unit == "$/gallon":
        return f"${value:.2f} per gallon"
    if unit == "thousands":
        return f"{value:,.0f} thousand"
    if unit == "index":
        return f"{value:.1f}"
    return f"{value:,.1f}"


def format_pct_change(pct: float) -> str:
    """Format percentage change for narration."""
    abs_pct = abs(pct)
    if abs_pct > 20:
        intensity = "plummeted" if pct < 0 else "surged"
    elif abs_pct > 10:
        intensity = "dropped significantly" if pct < 0 else "jumped significantly"
    elif abs_pct > 5:
        intensity = "fell" if pct < 0 else "rose"
    else:
        intensity = "declined" if pct < 0 else "increased"
    return f"{intensity} {abs_pct:.1f} percent"


def generate_script(story_package: dict) -> dict:
    """Generate a complete narration script from a story package."""
    
    p = story_package["primary"]
    related = story_package["related"]
    
    name = p["name"]
    value = format_number(p["latest_value"], p["unit"])
    change_desc = format_pct_change(p["yoy_pct"])
    direction = "down" if p["yoy_pct"] < 0 else "up"
    
    hooks = {
        "personal_savings_rate": f"Americans are saving less money than almost any point in the last two decades. The personal savings rate just hit {value}... {change_desc} in a single year. Here's what the data actually shows.",
        "median_home_price": f"The median home price in America just hit {value}. That's {change_desc} year over year. Let's break down what's really happening in the housing market.",
        "mortgage_rate_30yr": f"Mortgage rates just moved to {value}... {change_desc} from last year. Whether you're buying, selling, or just watching, here's what the numbers tell us.",
        "gas_price": f"Gas prices are now at {value}... {change_desc} compared to a year ago. But the real story isn't at the pump. It's in what this signals about the broader economy.",
        "unemployment_rate": f"The unemployment rate sits at {value}. That's {change_desc} year over year. But the headline number hides a much more complex story.",
        "cpi": f"Inflation just printed at {value} on the consumer price index. That {change_desc} from last year. Here's what that actually means for your wallet.",
        "credit_card_delinquency": f"Credit card delinquencies just hit {value}... {change_desc} from a year ago. Americans are falling behind on their bills, and the data tells a concerning story.",
        "national_debt": f"The U.S. national debt just crossed {value}. That's {change_desc} in twelve months. Let's put that number in perspective.",
        "fed_funds_rate": f"The Federal Reserve's benchmark rate is now at {value}... {change_desc} year over year. This single number ripples through everything from your mortgage to your savings account.",
        "student_loan_debt": f"Student loan debt in America has reached {value}... {change_desc} from last year. Here's the full picture the headlines don't show you.",
        "consumer_confidence": f"Consumer confidence just dropped to {value}... {change_desc} year over year. When Americans lose confidence, spending patterns shift. Here's what the data reveals.",
        "rent_cpi": f"The cost of rent in America, measured by the Consumer Price Index, just moved to {value}... {change_desc} from last year. Here's what that means for the 44 million Americans who rent.",
    }
    
    hook = hooks.get(p["key"], 
        f"{name} just hit {value}. That's {change_desc} compared to a year ago. Here's what the data actually reveals.")
    
    year = datetime.strptime(p["latest_date"], "%Y-%m-%d").year
    prev_val = format_number(p["prev_year_value"], p["unit"]) if p.get("prev_year_value") else "a different level"
    
    context = f"To understand what's happening, let's look at the trend. A year ago, {name.lower()} stood at {prev_val}. Today it's at {value}. That {abs(p['yoy_pct']):.1f} percent {'decline' if p['yoy_pct'] < 0 else 'increase'} didn't happen overnight... it's the result of forces that have been building for months."
    
    related_segments = []
    for i, r in enumerate(related[:3]):
        r_name = r["name"]
        r_value = format_number(r["latest_value"], r["unit"])
        r_yoy = r.get("yoy_pct")
        
        if i == 0:
            connector = "And here's where it gets interesting."
        elif i == 1:
            connector = "Meanwhile,"
        else:
            connector = "On top of that,"
        
        if r_yoy is not None:
            r_change = format_pct_change(r_yoy)
            related_segments.append(
                f"{connector} {r_name.lower()} is currently at {r_value}... that's {r_change} over the same period."
            )
        else:
            related_segments.append(
                f"{connector} {r_name.lower()} currently sits at {r_value}."
            )
    
    related_narration = " ".join(related_segments)
    
    insights = {
        "personal_savings_rate": "When Americans save less and spend more, it can feel like the economy is booming on the surface. But underneath, financial resilience is eroding. If a recession hits, fewer households have a buffer. The last time the savings rate was this low, it preceded a significant economic correction.",
        "median_home_price": "Rising home prices benefit existing homeowners but create a growing divide. First-time buyers are being priced out of more markets every month. The relationship between income growth and home price growth has been diverging for years, and the gap is widening.",
        "mortgage_rate_30yr": "Mortgage rates don't just affect homebuyers. They ripple through the entire economy. Lower rates unlock refinancing, boost construction, and free up consumer spending. Higher rates do the opposite. The direction of this number in the next six months will shape the housing market for years.",
        "gas_price": "Gas prices are one of the most visible economic indicators. When they move, consumer sentiment moves with them. But gas prices are also a leading indicator of broader inflationary pressures... or relief from them.",
        "unemployment_rate": "The unemployment rate is one of the most watched numbers in economics. But it only counts people actively looking for work. The labor force participation rate tells the other half of the story... how many working-age Americans have simply stopped looking.",
        "national_debt": "The national debt isn't just an abstract number. The interest payments alone now exceed the defense budget. Every dollar spent on interest is a dollar not spent on infrastructure, education, or healthcare. And as rates change, that interest bill shifts dramatically.",
        "credit_card_delinquency": "Rising delinquencies are a canary in the coal mine. They signal that consumers have exhausted their savings cushion and are now falling behind on revolving debt. Historically, this metric leads broader economic slowdowns by six to twelve months.",
        "fed_funds_rate": "The federal funds rate is the single most powerful lever in the U.S. economy. When the Fed moves it, everything reprices... mortgages, car loans, business credit, savings accounts, and Treasury yields. Understanding where it's headed is understanding where the economy is headed.",
    }
    
    insight = insights.get(p["key"],
        f"This shift in {name.lower()} reflects deeper structural changes in the American economy. The trend isn't just a number... it represents real changes in how millions of people earn, spend, save, and plan for the future.")
    
    close = f"That's the story behind {name.lower()} right now. The data doesn't lie, and it often tells us things months before the headlines catch up. If you want to see more data-driven breakdowns like this, subscribe and turn on notifications. I publish new episodes every week, tracking the numbers that actually shape the American economy. I'm The Money Map. See you in the next one."
    
    full_script = f"{hook}\n\n{context}\n\n{related_narration}\n\n{insight}\n\n{close}"
    
    title_templates = {
        "personal_savings_rate": "Americans Are Going Broke — The Savings Crisis Nobody Talks About",
        "median_home_price": f"The Median Home Just Hit {format_number(p['latest_value'], '$')} — Here's What Happened",
        "mortgage_rate_30yr": f"Mortgage Rates Just Hit {p['latest_value']:.1f}% — What This Means For You",
        "gas_price": f"Gas Is Now {format_number(p['latest_value'], '$/gallon')} — But That's Not The Real Story",
        "unemployment_rate": f"Unemployment at {p['latest_value']:.1f}% — The Number Behind The Number",
        "cpi": "Inflation Just Changed Direction — What The Fed Won't Tell You",
        "credit_card_delinquency": "Credit Card Defaults Are Surging — Here's Why It Matters",
        "national_debt": f"The U.S. Just Added {format_number(abs(p['yoy_change']), p['unit'])} In Debt — In One Year",
        "fed_funds_rate": "The Fed Just Made A Major Move — What Happens Next",
        "consumer_confidence": "Americans Just Lost Confidence In The Economy — The Data Is Clear",
        "rent_cpi": "Rent Prices Are Doing Something We Haven't Seen In Years",
    }
    
    title = title_templates.get(p["key"],
        f"{name} Just Hit {value} — Here's What The Data Shows")
    
    description = f"📊 {name} just {change_desc} year-over-year to {value}.\n\nIn this episode of The Money Map, we break down what's really happening with {name.lower()}, how it connects to {', '.join(r['name'].lower() for r in related[:2])}, and what it means for ordinary Americans.\n\nAll data sourced from FRED (Federal Reserve Economic Data) — the same data the Fed uses.\n\n🔔 Subscribe for weekly data-driven economic analysis.\n\n#economy #data #finance #themoneymap"
    
    tags = [
        "economy", "economics", "data", "finance", "money",
        name.lower().replace(" ", ""),
        "federal reserve", "FRED data",
        "personal finance", "economic analysis",
        "the money map", "data visualization",
    ]
    
    word_count = len(full_script.split())
    est_duration_sec = word_count / 2.5
    
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "script": full_script,
        "sections": {
            "hook": hook,
            "context": context,
            "related": related_narration,
            "insight": insight,
            "close": close,
        },
        "word_count": word_count,
        "estimated_duration_sec": round(est_duration_sec),
        "primary_metric": p,
    }


if __name__ == "__main__":
    from story_discovery import build_story_package
    
    pkg = build_story_package("/home/user/workspace/the-money-map/data/latest_data.json")
    script = generate_script(pkg)
    
    print(f"📺 TITLE: {script['title']}")
    print(f"⏱  Duration: ~{script['estimated_duration_sec']}s ({script['word_count']} words)")
    print(script['script'])
    
    with open("/home/user/workspace/the-money-map/data/latest_script.json", "w") as f:
        json.dump(script, f, indent=2)
    print(f"\nSaved to data/latest_script.json")
