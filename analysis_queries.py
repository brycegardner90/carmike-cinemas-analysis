import sqlite3

conn = sqlite3.connect("/home/claude/carmike_analysis/carmike_cinemas.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

separator = lambda title: print(f"\n{'─'*60}\n📊 {title}\n{'─'*60}")

# ── 1. Full revenue timeline ──────────────────────────────────
separator("Revenue Timeline: Full Company History")
rows = c.execute("""
    SELECT year, revenue_mil, data_quality
    FROM annual_financials
    ORDER BY year
""").fetchall()
for r in rows:
    flag = "~" if r['data_quality'] != 'confirmed' else " "
    print(f"  {r['year']}: ${r['revenue_mil']:>7.1f}M  {flag}")

# ── 2. Revenue during Bryce's employment window ───────────────
separator("Revenue During Bryce's Employment (Aug 2008 – Dec 2013)")
rows = c.execute("""
    SELECT f.year, f.revenue_mil, f.net_income_mil, f.total_debt_mil
    FROM annual_financials f
    WHERE f.year BETWEEN 2008 AND 2013
    ORDER BY f.year
""").fetchall()
for r in rows:
    ni = f"${r['net_income_mil']:>7.1f}M" if r['net_income_mil'] is not None else "       N/A"
    td = f"${r['total_debt_mil']:>6.1f}M" if r['total_debt_mil'] is not None else "      N/A"
    print(f"  {r['year']} | Rev: ${r['revenue_mil']:>6.1f}M | Net Income: {ni} | Debt: {td}")

# ── 3. Revenue growth: pre-employment vs during employment ────
separator("Revenue Context: Before, During, After Employment")
c.execute("""
    SELECT
        CASE
            WHEN year < 2008  THEN '1. Pre-employment'
            WHEN year <= 2013 THEN '2. During employment'
            ELSE                   '3. Post-employment'
        END AS period,
        COUNT(*) as data_points,
        MIN(revenue_mil) as min_rev,
        MAX(revenue_mil) as max_rev,
        AVG(revenue_mil) as avg_rev
    FROM annual_financials
    GROUP BY period
    ORDER BY period
""")
for r in c.fetchall():
    print(f"  {r['period']}: {r['data_points']} pts | "
          f"Min ${r['min_rev']:.1f}M | Max ${r['max_rev']:.1f}M | Avg ${r['avg_rev']:.1f}M")

# ── 4. Debt vs Revenue during confirmed years ─────────────────
separator("Debt Load vs Revenue (Where Both Available)")
rows = c.execute("""
    SELECT year, revenue_mil, total_debt_mil,
           ROUND(total_debt_mil / revenue_mil, 2) AS debt_to_revenue_ratio
    FROM annual_financials
    WHERE total_debt_mil IS NOT NULL
    ORDER BY year
""").fetchall()
for r in rows:
    bar = "█" * int(r['debt_to_revenue_ratio'] * 10)
    print(f"  {r['year']}: Rev ${r['revenue_mil']:>6.1f}M | Debt ${r['total_debt_mil']:>5.1f}M | "
          f"Ratio {r['debt_to_revenue_ratio']:.2f}x  {bar}")

# ── 5. Screen count growth trajectory ────────────────────────
separator("Screen Count Growth (Boom → Peak → Bankruptcy → Recovery)")
rows = c.execute("""
    SELECT year, screen_count, theater_count
    FROM theater_scale
    ORDER BY year
""").fetchall()
for r in rows:
    tc = str(r['theater_count']) if r['theater_count'] else "N/A"
    bar = "▓" * (r['screen_count'] // 100)
    print(f"  {r['year']}: {r['screen_count']:>5} screens | {tc:>4} theaters  {bar}")

# ── 6. Key events during Bryce's tenure ──────────────────────
separator("Key Events During Bryce's Employment (2008–2013)")
rows = c.execute("""
    SELECT year, event_label, event_type
    FROM key_events
    WHERE year BETWEEN 2008 AND 2013
    ORDER BY year
""").fetchall()
for r in rows:
    print(f"  {r['year']} [{r['event_type']:12}] {r['event_label']}")

# ── 7. Full event timeline by type ───────────────────────────
separator("All Key Events by Type")
rows = c.execute("""
    SELECT event_type, COUNT(*) as count,
           GROUP_CONCAT(year, ', ') as years
    FROM key_events
    GROUP BY event_type
    ORDER BY count DESC
""").fetchall()
for r in rows:
    print(f"  {r['event_type']:15} ({r['count']} events): {r['years']}")

# ── 8. Revenue per screen (efficiency metric) ─────────────────
separator("Revenue Per Screen Efficiency (Where Both Tables Overlap)")
rows = c.execute("""
    SELECT f.year, f.revenue_mil, t.screen_count,
           ROUND(f.revenue_mil * 1000000 / t.screen_count, 0) AS rev_per_screen
    FROM annual_financials f
    JOIN theater_scale t ON f.year = t.year
    ORDER BY f.year
""").fetchall()
for r in rows:
    print(f"  {r['year']}: ${r['rev_per_screen']:>9,.0f} per screen "
          f"({r['screen_count']} screens, ${r['revenue_mil']}M total)")

conn.close()
print("\n✅ All analysis queries complete.")
