"""
Enhanced Script Writer for The Money Map — V2
Produces longer, more engaging scripts (~400-500 words, 3-4 minutes)
with more depth, better narrative arc, and b-roll cue markers.

Structure:
1. COLD OPEN — dramatic stat drop (5s)
2. HOOK — set the stakes (15s) [B-ROLL: thematic footage]
3. THE NUMBER — deep dive into primary metric with historical context (45s)
4. CHART WALK — narrate the chart animation (30s)
5. CONTEXT — why this matters, what caused it (30s) [B-ROLL: cause footage]
6. CONNECTED DATA — related indicators tell the full picture (40s)
7. INSIGHT — the "so what" — implications for real people (30s) [B-ROLL: impact footage]
8. CLOSE — subscribe CTA with forward-looking hook (15s)

Total: ~3.5 minutes at 150 wpm
"""
import json
import sys
import os

sys.path.insert(0, '/home/user/workspace/the-money-map')
from config.settings import FRED_SERIES


# B-roll scene descriptions for AI video generation per topic
BROLL_SCENES = {
    "personal_savings_rate": {
        "hook": "Slow cinematic shot of an American family reviewing bills at a kitchen table under warm overhead light, worried expressions, papers and calculator visible, photorealistic",
        "context": "Time-lapse of a busy shopping mall with shoppers carrying bags, escalators moving, bright retail signage, consumerism, photorealistic cinematic",
        "insight": "Close-up of an empty glass savings jar on a wooden table with a few scattered coins, soft natural light from a window, shallow depth of field, photorealistic melancholy mood"
    },
    "mortgage_rate_30yr": {
        "hook": "Aerial drone shot slowly flying over a suburban neighborhood of single-family homes at golden hour, neat rows of houses with green lawns, photorealistic cinematic",
        "context": "Close-up of hands signing a mortgage document at a desk, pen on paper, official documents and keys visible, warm office lighting, photorealistic",
        "insight": "A young couple standing outside a house with a SOLD sign, looking hopeful but uncertain, soft afternoon light, shallow depth of field, photorealistic emotional"
    },
    "national_debt": {
        "hook": "Dramatic wide shot of the U.S. Capitol building at dusk with dark storm clouds gathering overhead, American flag waving, cinematic lighting, photorealistic",
        "context": "Close-up of hundred dollar bills being printed on a high-speed printing press, crisp detail, industrial setting, photorealistic documentary style",
        "insight": "Wide shot of a massive digital debt clock display showing trillions, red numbers glowing against a dark urban building facade at night, photorealistic"
    },
    "gas_price": {
        "hook": "Close-up of a gas pump display showing price per gallon ticking upward, numbers changing, harsh fluorescent gas station lighting at night, photorealistic",
        "context": "Aerial shot of an oil refinery at sunset with steam rising from industrial towers, warm orange sky, sprawling industrial complex, photorealistic cinematic",
        "insight": "Wide shot of a long line of cars at a gas station, everyday Americans filling up their vehicles, a working-class neighborhood, daylight, photorealistic documentary"
    },
    "gdp_growth": {
        "hook": "Time-lapse of a city skyline transitioning from busy daytime activity to evening, office lights flickering on, traffic flowing, photorealistic cinematic",
        "context": "Close-up of a factory assembly line with robotic arms assembling products, sparks flying, industrial precision, cool blue lighting, photorealistic",
        "insight": "Slow-motion shot of a 'CLOSED' sign being hung in a small business storefront window, empty street outside, melancholy natural lighting, photorealistic"
    }
}


def generate_enhanced_script(story_pkg):
    """Generate a longer, more cinematic script with b-roll cues."""
    primary = story_pkg['primary']
    related = story_pkg.get('related', [])
    
    name = primary['name']
    val = primary['latest_value']
    unit = primary['unit']
    yoy = primary['yoy_pct']
    prev = primary['prev_year_value']
    date = primary['latest_date']
    key = primary['key']
    
    # Format values
    def fmt(v, u):
        if u == '%': return f"{v:.1f} percent"
        if u in ('$', '$/gallon'): return f"${v:,.2f}"
        if u == 'millions $':
            return f"${v/1e6:.1f} trillion" if v >= 1e6 else f"${v/1000:,.0f} billion"
        if u == 'billions $':
            return f"${v/1000:.1f} trillion" if v >= 1000 else f"${v:,.0f} billion"
        if u == 'index': return f"{v:,.1f}"
        if u == 'thousands':
            return f"{v/1000:,.1f} million" if v >= 1000 else f"{v:,.0f} thousand"
        return f"{v:,.1f}"
    
    display = fmt(val, unit)
    prev_display = fmt(prev, unit)
    direction = "dropped" if yoy < 0 else "risen"
    dir_word = "decline" if yoy < 0 else "increase"
    abs_yoy = abs(yoy)
    
    # Build related metrics text
    related_lines = []
    for i, r in enumerate(related[:3]):
        rname = r['name']
        rval = fmt(r['latest_value'], r.get('unit', ''))
        ryoy = r.get('yoy_pct')
        if ryoy is not None:
            rdir = "up" if ryoy > 0 else "down"
            related_lines.append(
                f"{rname} is currently at {rval}... that's {rdir} {abs(ryoy):.1f} percent year over year."
            )
        else:
            related_lines.append(f"{rname} is currently at {rval}.")
    
    related_block = " ".join(related_lines) if related_lines else ""
    
    # Topic-specific insight paragraphs
    insights = {
        "personal_savings_rate": (
            f"Here's what this really means for everyday Americans. When the savings rate drops to {display}, "
            f"it means the average household is saving just {display} of every dollar they earn after taxes. "
            f"For a family earning $83,000 a year, that's roughly $250 a month going into savings. "
            f"One car repair. One medical bill. One unexpected layoff... and there's no cushion. "
            f"The last time the savings rate was this low for an extended period, it preceded the 2008 financial crisis. "
            f"That doesn't mean a crash is coming tomorrow. But it does mean that the American consumer... "
            f"the engine of 70 percent of GDP... is running on fumes."
        ),
        "mortgage_rate_30yr": (
            f"Let's put this in real dollar terms. On a $400,000 home, the difference between last year's rate "
            f"and today's rate saves a buyer roughly $200 per month on their mortgage payment. "
            f"That's $72,000 over the life of the loan. But here's the catch... while rates have come down, "
            f"home prices haven't followed. Sellers see lower rates and hold firm on asking prices. "
            f"So the monthly payment might be lower, but the sticker price is still near record highs. "
            f"For first-time buyers, the math is better than it was a year ago, but it's still historically expensive "
            f"to buy a home in America."
        ),
        "national_debt": (
            f"To put this in perspective, {display} divided among every American means each person... "
            f"including children... owes roughly $112,000. A family of four carries $448,000 in national debt. "
            f"Now, government debt isn't like personal debt. Countries don't pay it off the same way you pay off a credit card. "
            f"But the interest payments alone are now over $1 trillion per year... more than we spend on defense. "
            f"Every dollar going to interest is a dollar not going to infrastructure, education, or healthcare. "
            f"And with rates still elevated, that interest bill is only growing."
        ),
        "gas_price": (
            f"Cheaper gas sounds like good news, and for your wallet, it is. The average American drives about "
            f"13,500 miles per year. At current prices versus last year, that saves roughly $150 to $200 annually. "
            f"But falling gas prices often signal something deeper. They can reflect weakening global demand... "
            f"meaning the world economy is slowing down. Oil prices are a leading indicator. "
            f"When demand for energy drops, it usually means factories are producing less, shipping is declining, "
            f"and consumers are pulling back. So while you're paying less at the pump... the reason you're paying less "
            f"might not be something to celebrate."
        ),
        "gdp_growth": (
            f"GDP growth at {display} is technically still positive... the economy is still expanding. "
            f"But the trajectory matters more than the number itself. A year ago we were growing at {prev_display}. "
            f"That deceleration is significant. At this pace, the economy is barely keeping up with population growth. "
            f"Historically, when GDP growth drops below 1.5 percent, the probability of entering a recession "
            f"within the next 12 months rises sharply. We're not there yet. But the margin of safety is razor thin. "
            f"One external shock... a trade war, a banking stress event, an oil spike... could tip the balance."
        ),
    }
    
    insight_text = insights.get(key, 
        f"When {name.lower()} moves this significantly, it sends ripple effects through the entire economy. "
        f"This isn't just a number on a chart. It affects real decisions... what people buy, where they live, "
        f"how they plan for retirement. The trend we're seeing right now has historically preceded "
        f"major economic shifts. Whether that pattern holds this time remains to be seen."
    )
    
    # Build the full script with section markers
    script = (
        f"[COLD_OPEN]\n"
        f"{display}.\n\n"
        
        f"[HOOK]\n"
        f"{name} just {direction} {abs_yoy:.1f} percent in a single year. "
        f"That's one of the most dramatic shifts we've seen in recent economic data. "
        f"In this episode, we're going to break down exactly what's happening, "
        f"what's driving it, and what it means for you. Let's follow the data.\n\n"
        
        f"[THE_NUMBER]\n"
        f"Right now, {name.lower()} stands at {display}. "
        f"One year ago, it was at {prev_display}. "
        f"That's a {abs_yoy:.1f} percent {dir_word} in twelve months. "
        f"To understand why that matters, you have to see the full picture. "
        f"This chart shows the complete history.\n\n"
        
        f"[CHART_WALK]\n"
        f"Watch how {name.lower()} has moved over the past decade. "
        f"You can see periods of stability... periods of gradual change... "
        f"and then these sharp inflection points where everything accelerates. "
        f"The move we're seeing now is one of those inflection points. "
        f"The data is moving faster than at almost any point in the last ten years.\n\n"
        
        f"[CONTEXT]\n"
        f"But {name.lower()} doesn't exist in isolation. "
        f"To understand the full story, we need to look at what's connected. "
        f"{related_block}\n\n"
        
        f"[CONNECTED_DATA]\n"
        f"When you put these numbers side by side, a clear picture emerges. "
        f"These aren't random fluctuations. They're interconnected forces... "
        f"each one reinforcing the others. "
        f"And together, they tell a story that's more complex than any single headline.\n\n"
        
        f"[INSIGHT]\n"
        f"{insight_text}\n\n"
        
        f"[CLOSE]\n"
        f"That's the story behind {name.lower()} right now. "
        f"The data doesn't lie... and it often tells us things months before the headlines catch up. "
        f"If you want to see more data-driven breakdowns like this, subscribe and turn on notifications. "
        f"Every week, we track the numbers that actually shape the American economy. "
        f"I'm The Money Map. See you in the next one."
    )
    
    # Clean script (remove section markers for voiceover)
    clean_script = "\n".join(
        line for line in script.split("\n") 
        if not line.startswith("[") or not line.endswith("]")
    ).strip()
    # Remove empty lines from marker removal
    while "\n\n\n" in clean_script:
        clean_script = clean_script.replace("\n\n\n", "\n\n")
    
    # Generate title
    if abs_yoy > 20:
        drama = "dramatic"
    elif abs_yoy > 10:
        drama = "significant" 
    else:
        drama = "notable"
    
    # Custom titles per topic
    titles = {
        "personal_savings_rate": "Americans Are Going Broke — The Savings Crisis Nobody Talks About",
        "mortgage_rate_30yr": "Mortgage Rates Just Hit 6% — What This Really Means For Home Buyers",
        "national_debt": "The U.S. Just Added $2.2 Trillion In Debt — Here's Where It's Going",
        "gas_price": "Gas Is Under $3 A Gallon — But That Might Be Bad News",
        "gdp_growth": "GDP Growth Just Collapsed 26% — Is A Recession Coming?",
    }
    title = titles.get(key, f"{name} Just Made A {drama.title()} Move — Here's What The Data Shows")
    
    # YouTube description
    description = (
        f"📊 {name} just {direction} {abs_yoy:.1f}% year-over-year to {display}.\n\n"
        f"In this episode of The Money Map, we break down what's really happening with "
        f"{name.lower()}, how it connects to "
        + ", ".join(r['name'].lower() for r in related[:3])
        + f", and what it means for ordinary Americans.\n\n"
        f"All data sourced from FRED (Federal Reserve Economic Data) — "
        f"the same data the Fed uses.\n\n"
        f"Timestamps:\n"
        f"0:00 — The Number\n"
        f"0:20 — What's Happening\n"
        f"0:50 — The Full Chart\n"
        f"1:30 — Connected Indicators\n"
        f"2:20 — What This Means For You\n"
        f"3:10 — The Takeaway\n\n"
        f"🔔 Subscribe for weekly data-driven economic analysis.\n\n"
        f"#economy #data #finance #themoneymap #economics #personalfinance"
    )
    
    tags = [
        "economy", "economics", "data", "finance", "money",
        name.lower().replace(" ", ""), "federal reserve", "FRED data",
        "personal finance", "economic analysis", "the money map",
        "data visualization", "economic data", "recession",
        "inflation", "interest rates"
    ]
    
    word_count = len(clean_script.split())
    est_duration = int(word_count / 2.5)  # ~150 wpm = 2.5 wps
    
    # Get b-roll prompts
    broll = BROLL_SCENES.get(key, {
        "hook": f"Cinematic establishing shot related to {name.lower()}, dramatic lighting, photorealistic",
        "context": f"Documentary-style footage related to the causes of changes in {name.lower()}, photorealistic",
        "insight": f"Emotional footage showing the human impact of {name.lower()} changes, photorealistic"
    })
    
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "script": clean_script,
        "script_with_markers": script,
        "sections": {
            "cold_open": script.split("[HOOK]")[0].replace("[COLD_OPEN]\n", "").strip(),
            "hook": script.split("[HOOK]\n")[1].split("\n\n[THE_NUMBER]")[0].strip(),
            "the_number": script.split("[THE_NUMBER]\n")[1].split("\n\n[CHART_WALK]")[0].strip(),
            "chart_walk": script.split("[CHART_WALK]\n")[1].split("\n\n[CONTEXT]")[0].strip(),
            "context": script.split("[CONTEXT]\n")[1].split("\n\n[CONNECTED_DATA]")[0].strip(),
            "connected_data": script.split("[CONNECTED_DATA]\n")[1].split("\n\n[INSIGHT]")[0].strip(),
            "insight": script.split("[INSIGHT]\n")[1].split("\n\n[CLOSE]")[0].strip(),
            "close": script.split("[CLOSE]\n")[1].strip(),
        },
        "broll_prompts": broll,
        "word_count": word_count,
        "estimated_duration_sec": est_duration,
        "primary_metric": {
            "key": key,
            "name": name,
            "series_id": primary['series_id'],
            "unit": unit,
            "latest_value": val,
            "latest_date": date,
            "yoy_change": primary.get('yoy_change'),
            "yoy_pct": yoy,
            "prev_year_value": prev,
            "score": primary.get('score'),
            "tags": primary.get('tags', []),
        },
    }


if __name__ == "__main__":
    from scripts.story_discovery import build_story_package
    pkg = build_story_package("/home/user/workspace/the-money-map/data/latest_data.json")
    result = generate_enhanced_script(pkg)
    print(f"Title: {result['title']}")
    print(f"Words: {result['word_count']}")
    print(f"Duration: ~{result['estimated_duration_sec']}s ({result['estimated_duration_sec']//60}m{result['estimated_duration_sec']%60}s)")
    print(f"\nSections:")
    for k, v in result['sections'].items():
        wc = len(v.split())
        print(f"  {k}: {wc} words")
    print(f"\nB-roll prompts:")
    for k, v in result['broll_prompts'].items():
        print(f"  {k}: {v[:80]}...")
