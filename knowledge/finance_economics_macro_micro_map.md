# Finance, Financial Planning, and Economics Map

Extends `holistic_financial_agent_intelligence.md` and `financial_market_and_etf_intelligence.md`.

**Disclaimer:** educational and product-design reference, not investment, tax, or legal advice. All numbers must be computed deterministically; never let an LLM invent rates or returns.

---

## 1. Scope

| Layer | Core question | App relevance |
|---|---|---|
| Personal finance | How does an individual survive and build wealth? | Budgeting, debt, savings, insurance, retirement |
| Corporate finance | How does a business create and measure value? | SME cashflow, invoicing, unit economics, valuation |
| Microeconomics | How do people and firms choose under scarcity? | Pricing, incentives, market fit |
| Macroeconomics | How do inflation, rates, growth, and policy shape everything? | Portfolio, lending, forecasting, risk |
| Behavioral finance | Why do smart people make bad money decisions? | UX nudges, defaults, guardrails |

## 2. Personal finance

### Four pillars (already in `holistic_financial_agent_intelligence.md`)

1. **Defense** — cashflow, emergency fund, debt payoff, insurance.
2. **Offense** — income growth, leverage (labor, capital, code, media), side business.
3. **Wealth** — low-cost diversified investing, asset allocation, rebalancing, tax efficiency.
4. **Macro awareness** — inflation, rates, currency, cycles.

### Order of operations (Financial Waterfall)

1. Cover basic needs and avoid new high-interest debt.
2. Build 1-month cash buffer → 3–6 months emergency fund.
3. Capture employer match / tax-advantaged accounts.
4. Pay high-interest debt (avalanche by rate; snowball for behavior).
5. Insure catastrophic risk (health, disability, term life if dependents).
6. Invest surplus in a diversified portfolio aligned to horizon.
7. Increase income and optionality.

### Key formulas

- Emergency runway = liquid assets ÷ monthly essential expenses.
- Savings rate = (income − expenses) ÷ income.
- Debt avalanche: order by interest rate descending; snowball: order by balance ascending.
- Real return ≈ nominal return − inflation (exact: (1+n)/(1+i)−1).
- Compound future value = PV × (1+r)^n; monthly contributions use annuity formula.
- Safe withdrawal rate: 3–4% of portfolio per year (Trinity study; not a guarantee).
- Insurance need ≈ income replacement + debts + education − existing assets.

### Behavioral guardrails

- Default to automatic transfers on payday.
- Separate accounts by purpose (mental accounting can be useful if explicit).
- Pre-commit to spending limits; remove friction for saving, add friction for impulse spending.
- Show progress, not shame; loss aversion cuts both ways.

## 3. Corporate finance and unit economics

| Metric | Formula | Meaning |
|---|---|---|
| Gross margin | (Revenue − COGS) ÷ Revenue | Product economics |
| CAC | Sales + marketing spend ÷ new customers | Acquisition cost |
| LTV | ARPU × gross margin × retention months | Lifetime value |
| LTV/CAC | LTV ÷ CAC | ≥3 is a common healthy target |
| Payback | CAC ÷ monthly gross profit per customer | Months to recover acquisition |
| Burn | Monthly cash outflow | Runway = cash ÷ net burn |
| Break-even | Fixed costs ÷ (price − variable cost) | Units or revenue needed |
| NPV | Σ CF_t ÷ (1+r)^t − initial investment | Value creation |
| IRR | r where NPV = 0 | Project return |
| WACC | weighted cost of debt and equity | Discount rate |
| Rule of 40 | growth % + profit margin % | SaaS health heuristic |

### Valuation basics

- Multiples: revenue, EBITDA, earnings — only meaningful with comparable peers.
- DCF: forecast free cash flow, discount at WACC, add terminal value; run sensitivity.
- Early-stage: team, market, traction, moat, unit economics; valuation is negotiation, not physics.

## 4. Microeconomics

- **Supply and demand:** equilibrium, shifts vs movements, shortage/surplus.
- **Elasticity:** price elasticity = %ΔQ ÷ %ΔP; affects pricing and tax incidence.
- **Consumer choice:** utility, budget constraint, marginal substitution.
- **Production:** fixed vs variable costs, marginal cost, economies of scale/scope.
- **Market structures:** perfect competition, monopolistic competition, oligopoly, monopoly.
- **Information asymmetry:** adverse selection, moral hazard, signaling, screening.
- **Externalities:** negative (pollution) and positive (education); Pigouvian taxes/subsidies.
- **Game theory:** Nash equilibrium, prisoner's dilemma, coordination games.

**Product use:** pricing tiers, freemium limits, referral incentives, marketplace liquidity, incentive design.

## 5. Macroeconomics

| Variable | What it measures | App impact |
|---|---|---|
| GDP | Output and growth | Demand, hiring, SME revenue |
| Inflation (CPI/PPI) | Price level change | Pricing, wages, real returns |
| Unemployment | Labor slack | Consumer confidence, wage pressure |
| Policy rate | Central bank cost of money | Loan rates, valuations, FX |
| Bond yields | Market expectations | Mortgage, portfolio duration |
| Exchange rate | Relative currency price | Import costs, travel, remittances |
| Fiscal balance | Government spending vs revenue | Taxes, subsidies, public demand |
| Current account | Trade + income flows | Currency pressure |

### Frameworks

- **Business cycle:** expansion → peak → contraction → trough.
- **Monetary policy:** policy rate, reserve requirements, open market operations, liquidity.
- **Fiscal policy:** spending and taxation; multipliers and crowding out.
- **Phillips curve:** inflation–unemployment trade-off (unstable across regimes).
- **Yield curve:** normal, flat, inverted; inversion is a recession signal, not a guarantee.
- **Balance of payments:** current account + capital/financial account.
- **Purchasing power parity:** long-run exchange-rate anchor, poor short-run predictor.

## 6. Indonesia context

| Institution | Role | Link |
|---|---|---|
| Bank Indonesia (BI) | Monetary policy, BI Rate, rupiah stability | https://www.bi.go.id/ |
| OJK | Banking, capital markets, insurance, fintech supervision | https://www.ojk.go.id/ |
| BPS | Official statistics: inflation, GDP, unemployment, trade | https://www.bps.go.id/ |
| Kemenkeu | Fiscal policy, state budget, taxes | https://www.kemenkeu.go.id/ |
| IDX | Indonesian stock exchange | official IDX site |
| Sikapi Uangmu (OJK) | Financial literacy | https://sikapiuangmu.ojk.go.id/ |

**Local realities:** high financial inclusion but uneven literacy; cash-heavy SMEs; informal income; strong mobile penetration; BNPL and paylater growth; digital lending risk; rupiah volatility; subsidized fuel/electricity policy effects; tax brackets and VAT changes.

**Regulatory notes for apps:** lending requires OJK licensing; investment advice may require licensing; personal data falls under UU PDP; payment services require BI licensing. Do not assume a consumer app can custody funds or lend without permits.

## 7. Behavioral finance

| Bias | Description | App countermeasure |
|---|---|---|
| Loss aversion | Losses hurt ~2× gains | Show long-horizon outcomes; avoid panic UI |
| Anchoring | Fixating on first number | Show ranges and scenarios |
| Overconfidence | Overestimating skill | Track predictions; show base rates |
| Mental accounting | Treating money differently by label | Make buckets explicit |
| Present bias | Prefer now over later | Automatic defaults, commitment devices |
| Herding | Following the crowd | Show evidence, not hype |
| Recency | Overweighting recent events | Long-term charts, drawdown history |
| Sunk cost | Throwing good money after bad | Separate past cost from future value |

## 8. Fintech and app business models

| Model | Revenue | Key metric | Risk |
|---|---|---|---|
| Subscription | Monthly/annual fee | MRR, churn, LTV | Low willingness to pay |
| Freemium | Paid upgrades | Conversion, ARPU | Free-tier cost |
| Transaction fee | % per payment | GMV, take rate | Regulatory, fraud |
| Marketplace | Take rate + listing | Liquidity, match rate | Two-sided cold start |
| Lending | Interest + fees | Default rate, NPL | Credit and licensing risk |
| B2B SaaS | Seat/usage pricing | Retention, expansion | Long sales cycle |
| Data/analytics | Subscription | Coverage, freshness | Privacy and licensing |

## 9. App opportunities

| Problem | App shape | Must-have safeguards |
|---|---|---|
| Budgeting and cashflow | Desktop/web dashboard, mobile companion | Local-first option, no shame framing |
| Debt payoff | Planner with avalanche/snowball | Deterministic math, rate disclosure |
| Portfolio tracking | Read-only aggregator | No trading without license, risk disclosure |
| SME cashflow | Invoicing + runway forecast | Tax/VAT accuracy, data export |
| Financial literacy | Scenario simulator | Cite sources, show assumptions |
| Tax organizer | Checklist + document vault | Privacy, retention controls |
| Bill/subscription manager | Reminders + cancellation help | No dark patterns, consent |

## 10. Data sources

- Official: BI, OJK, BPS, Kemenkeu, IDX, World Bank, IMF, BIS.
- Research: NBER, SSRN/RePEc, Semantic Scholar, CFA Institute.
- Market data: use licensed APIs; free sources may be delayed or unofficial — label them.

## 11. Modeling rules

1. Never invent an interest rate, inflation rate, or return. Use a named, dated source.
2. Show nominal and real values.
3. Run base/bull/bear scenarios; show sensitivity tables.
4. Model fees and taxes explicitly.
5. Separate deterministic calculation from narrative explanation.
6. Disclose assumptions and update dates in the UI.

## 12. Verified resources

Personal/institutional: https://www.ojk.go.id/ · https://www.bi.go.id/ · https://www.bps.go.id/ · https://www.kemenkeu.go.id/ · https://sikapiuangmu.ojk.go.id/ · IDX (Indonesia Stock Exchange, official site) · https://www.cfainstitute.org/

Macro/research: https://www.worldbank.org/en/research · https://data.worldbank.org/ · https://www.bis.org/ · https://www.nber.org/ · https://ideas.repec.org/ · https://www.semanticscholar.org/ · https://ourworldindata.org/

Behavioral: https://www.behavioraleconomics.com/

Some official sites (IMF, IDX) return 403 to bots but load in a browser.
