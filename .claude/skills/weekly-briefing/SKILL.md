# Weekly Briefing

Generate comprehensive Monday Morning CEO Briefing that synthesizes business performance, completed work, bottlenecks, and proactive suggestions.

## Purpose

The Weekly Briefing skill **aggregates** data from across the vault, **analyzes** business performance against goals, **identifies** trends and bottlenecks, and **presents** actionable insights in a CEO-level executive summary. This skill **transforms** raw activity data into strategic business intelligence.

## Design Philosophy

- **Executive Level**: Output is concise, insight-focused
- **Data-Driven**: All assertions backed by vault data
- **Proactive**: Surfaces opportunities and warnings
- **Action-Oriented**: Includes specific recommendations

## Workflow

1. **Review** `/Business_Goals.md` for targets and metrics
2. **Analyze** `/Accounting/` for financial data
3. **Scan** `/Done/` for completed work
4. **Check** `/Needs_Action/` for pending items
5. **Parse** `/Logs/` for activity patterns
6. **Identify** bottlenecks and delays
7. **Detect** subscription and cost anomalies
8. **Generate** briefing at `/Briefings/YYYY-MM-DD_Monday_Briefing.md`
9. **Update** Dashboard with weekly summary

## Modularity

Extensible with:
- Custom metric calculations
- Trend analysis over multiple weeks
- Integration with accounting APIs
- Automated KPI tracking
- Graph generation

---

*Weekly Briefing Skill v1.0*
