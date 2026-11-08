#!/usr/bin/env python3
"""
financial_calculator.py
Deterministic Financial Engine for Gemi (Anti-Vibe Financial AI Agent).
Strictly prevents LLM arithmetic hallucinations for:
- Compound interest & Future Value (Nominal & Inflation-Adjusted)
- Monte Carlo retirement simulation (Safe Withdrawal Rate / Trinity Study)
- Loan & mortgage amortization with early prepayment optimization
- Debt payoff optimizer (Debt Avalanche vs Debt Snowball comparison)
- Vicki Robin Life Energy Calculator (Price -> Hours of Life Worked)
- Financial Waterfall & Cashflow Health Audit
- Portfolio metrics (CAGR, StDev, Sharpe Ratio, Sortino Ratio, Max Drawdown)
"""

import argparse
import json
import math
import random
import sys


def calc_compound_interest(principal, annual_rate_pct, years, monthly_contrib=0.0, inflation_pct=0.0):
    r = annual_rate_pct / 100.0 / 12.0
    inf_r = inflation_pct / 100.0 / 12.0
    months = int(years * 12)
    
    current_balance = principal
    total_contributions = principal
    schedule = []
    
    for m in range(1, months + 1):
        interest = current_balance * r
        current_balance += interest + monthly_contrib
        total_contributions += monthly_contrib
        
        if m % 12 == 0:
            year_num = m // 12
            # Real value discount
            real_balance = current_balance / ((1.0 + inf_r) ** m) if inf_r > 0 else current_balance
            schedule.append({
                "year": year_num,
                "nominal_balance": round(current_balance, 2),
                "real_balance": round(real_balance, 2),
                "total_contributions": round(total_contributions, 2),
                "total_interest": round(current_balance - total_contributions, 2)
            })
            
    real_final = current_balance / ((1.0 + inf_r) ** months) if inf_r > 0 else current_balance
    total_interest = current_balance - total_contributions
    
    return {
        "principal": principal,
        "annual_rate_pct": annual_rate_pct,
        "years": years,
        "monthly_contribution": monthly_contrib,
        "inflation_pct": inflation_pct,
        "final_nominal_balance": round(current_balance, 2),
        "final_real_balance": round(real_final, 2),
        "total_contributions": round(total_contributions, 2),
        "total_interest_earned": round(total_interest, 2),
        "interest_to_contribution_ratio": round(total_interest / total_contributions, 2) if total_contributions > 0 else 0,
        "yearly_milestones": schedule
    }


def calc_monte_carlo(initial_portfolio, annual_withdrawal, years=30, mean_return_pct=7.0, stdev_pct=15.0, inflation_pct=3.0, num_sims=10000, seed=42):
    random.seed(seed)
    months = int(years * 12)
    monthly_mean = (mean_return_pct / 100.0) / 12.0
    monthly_stdev = (stdev_pct / 100.0) / math.sqrt(12.0)
    monthly_inf = (inflation_pct / 100.0) / 12.0
    base_monthly_withdrawal = annual_withdrawal / 12.0
    
    successful_runs = 0
    ending_balances = []
    
    for _ in range(num_sims):
        balance = initial_portfolio
        withdrawal = base_monthly_withdrawal
        survived = True
        
        for m in range(months):
            # Inflation adjust withdrawal yearly
            if m > 0 and m % 12 == 0:
                withdrawal *= (1.0 + (inflation_pct / 100.0))
                
            # Log-normal or normal return sample
            m_return = random.gauss(monthly_mean, monthly_stdev)
            balance = (balance - withdrawal) * (1.0 + m_return)
            
            if balance <= 0:
                survived = False
                ending_balances.append(0.0)
                break
                
        if survived:
            successful_runs += 1
            ending_balances.append(balance)
            
    ending_balances.sort()
    success_rate = (successful_runs / num_sims) * 100.0
    p10 = ending_balances[int(num_sims * 0.10)]
    p50 = ending_balances[int(num_sims * 0.50)]
    p90 = ending_balances[int(num_sims * 0.90)]
    initial_swr = (annual_withdrawal / initial_portfolio) * 100.0 if initial_portfolio > 0 else 0
    
    return {
        "initial_portfolio": initial_portfolio,
        "annual_withdrawal": annual_withdrawal,
        "initial_withdrawal_rate_pct": round(initial_swr, 2),
        "years": years,
        "simulations": num_sims,
        "success_rate_pct": round(success_rate, 2),
        "risk_level": "Safe (>=95%)" if success_rate >= 95 else ("Caution (85-94%)" if success_rate >= 85 else "High Risk (<85%)"),
        "percentile_ending_wealth": {
            "p10_unlucky_case": round(p10, 2),
            "p50_median_case": round(p50, 2),
            "p90_lucky_case": round(p90, 2)
        }
    }


def calc_amortization(principal, annual_rate_pct, years, extra_monthly=0.0):
    r = annual_rate_pct / 100.0 / 12.0
    total_months = int(years * 12)
    
    if r == 0:
        base_monthly_pmt = principal / total_months
    else:
        base_monthly_pmt = principal * (r * ((1.0 + r) ** total_months)) / (((1.0 + r) ** total_months) - 1.0)
        
    # Standard schedule
    std_total_interest = (base_monthly_pmt * total_months) - principal
    
    # Accelerated schedule with extra payment
    acc_balance = principal
    acc_months = 0
    acc_total_interest = 0.0
    total_monthly_pmt = base_monthly_pmt + extra_monthly
    
    while acc_balance > 0 and acc_months < total_months * 2:
        acc_months += 1
        interest_charge = acc_balance * r
        acc_total_interest += interest_charge
        principal_pmt = total_monthly_pmt - interest_charge
        
        if acc_balance <= principal_pmt:
            acc_balance = 0.0
            break
        else:
            acc_balance -= principal_pmt
            
    interest_saved = std_total_interest - acc_total_interest
    months_saved = total_months - acc_months
    
    return {
        "principal": principal,
        "annual_rate_pct": annual_rate_pct,
        "loan_term_years": years,
        "standard_monthly_payment": round(base_monthly_pmt, 2),
        "standard_total_interest": round(std_total_interest, 2),
        "standard_total_paid": round(principal + std_total_interest, 2),
        "extra_monthly_principal": extra_monthly,
        "accelerated_monthly_payment": round(total_monthly_pmt, 2),
        "accelerated_months_to_payoff": acc_months,
        "accelerated_years_to_payoff": round(acc_months / 12.0, 1),
        "accelerated_total_interest": round(acc_total_interest, 2),
        "interest_saved": round(interest_saved, 2),
        "time_saved_months": months_saved,
        "time_saved_years": round(months_saved / 12.0, 1)
    }


def calc_debt_payoff(debts, extra_monthly_budget=0.0):
    """
    debts = [{"name": "Card A", "balance": 10000000, "rate": 24.0, "min_payment": 300000}, ...]
    Compares Debt Avalanche (highest APR first) vs Debt Snowball (smallest balance first).
    """
    def simulate_strategy(sort_key, reverse=True):
        sim_debts = [dict(d) for d in debts]
        months = 0
        total_interest = 0.0
        payoff_order = []
        
        while any(d["balance"] > 0 for d in sim_debts) and months < 360:
            months += 1
            available_extra = extra_monthly_budget
            
            # Sort active debts according to strategy
            active_debts = [d for d in sim_debts if d["balance"] > 0]
            active_debts.sort(key=sort_key, reverse=reverse)
            
            # Step 1: Accrue monthly interest & pay minimums
            freed_up_minimums = 0.0
            for d in active_debts:
                r_m = (d["rate"] / 100.0) / 12.0
                m_interest = d["balance"] * r_m
                total_interest += m_interest
                d["balance"] += m_interest
                
                # Pay minimum
                pmt = min(d["min_payment"], d["balance"])
                d["balance"] -= pmt
                if d["balance"] == 0:
                    freed_up_minimums += d["min_payment"]
                    payoff_order.append({"month": months, "debt": d["name"]})
                    
            # Step 2: Apply extra budget + freed up minimums to target debt
            total_snowball = available_extra + freed_up_minimums
            active_debts = [d for d in sim_debts if d["balance"] > 0]
            if active_debts and total_snowball > 0:
                active_debts.sort(key=sort_key, reverse=reverse)
                target = active_debts[0]
                extra_pmt = min(total_snowball, target["balance"])
                target["balance"] -= extra_pmt
                if target["balance"] == 0 and not any(p["debt"] == target["name"] for p in payoff_order):
                    payoff_order.append({"month": months, "debt": target["name"]})
                    
        return {
            "months_to_debt_free": months,
            "years_to_debt_free": round(months / 12.0, 1),
            "total_interest_paid": round(total_interest, 2),
            "payoff_sequence": payoff_order
        }
        
    # Avalanche: Sort by interest rate descending
    avalanche_res = simulate_strategy(lambda x: x["rate"], reverse=True)
    # Snowball: Sort by current balance ascending
    snowball_res = simulate_strategy(lambda x: x["balance"], reverse=False)
    
    interest_difference = snowball_res["total_interest_paid"] - avalanche_res["total_interest_paid"]
    
    return {
        "total_debts_count": len(debts),
        "total_initial_balance": sum(d["balance"] for d in debts),
        "extra_monthly_budget": extra_monthly_budget,
        "debt_avalanche_optimal_math": avalanche_res,
        "debt_snowball_behavioral_win": snowball_res,
        "math_savings_with_avalanche": round(interest_difference, 2),
        "recommendation": (
            "Choose Debt Avalanche for maximum mathematical efficiency (saves {:.2f} in interest). "
            "Choose Debt Snowball if quick behavioral psychological wins are needed to sustain motivation."
        ).format(interest_difference)
    }


def calc_life_energy(item_price, gross_income, income_period="monthly", work_hours_week=40, tax_rate_pct=15.0, weekly_commute_hours=5.0, weekly_work_costs=0.0):
    """
    Vicki Robin 'Your Money or Your Life' Life Energy Formula.
    Converts purchase price into actual hours of human life exchanged.
    """
    if income_period == "annual":
        annual_gross = gross_income
    else:
        annual_gross = gross_income * 12.0
        
    net_annual = annual_gross * (1.0 - (tax_rate_pct / 100.0))
    annual_work_costs = weekly_work_costs * 52.0
    true_net_annual = net_annual - annual_work_costs
    
    annual_work_hours = work_hours_week * 52.0
    annual_commute_hours = weekly_commute_hours * 52.0
    total_life_hours_invested = annual_work_hours + annual_commute_hours
    
    real_hourly_wage = true_net_annual / total_life_hours_invested if total_life_hours_invested > 0 else 0
    life_hours_cost = item_price / real_hourly_wage if real_hourly_wage > 0 else 0
    work_days_cost = life_hours_cost / 8.0
    
    return {
        "item_price": item_price,
        "gross_income": gross_income,
        "income_period": income_period,
        "true_net_annual_income": round(true_net_annual, 2),
        "total_life_hours_dedicated_yearly": round(total_life_hours_invested, 1),
        "nominal_hourly_wage": round(annual_gross / annual_work_hours, 2),
        "real_hourly_wage": round(real_hourly_wage, 2),
        "life_energy_cost_hours": round(life_hours_cost, 1),
        "life_energy_cost_working_days": round(work_days_cost, 1),
        "psychological_nudge": (
            f"Buying this item costs you {round(life_hours_cost, 1)} hours ({round(work_days_cost, 1)} working days) "
            f"of your irreplaceable life energy."
        )
    }


def calc_waterfall_audit(monthly_income, monthly_expenses, emergency_fund, debt_payments=0.0, high_interest_debt=0.0, has_basic_insurance=True):
    """
    Financial Waterfall & Conscious Spending Health Check:
    Stage 1: Emergency buffer (3-6 mo expenses)
    Stage 2: Core Insurance Protection (Health / Term Life)
    Stage 3: High-interest debt eradication (>10% APR)
    Stage 4: Wealth Building & Long-term asset allocation
    """
    runway_months = emergency_fund / monthly_expenses if monthly_expenses > 0 else 0
    dti_ratio = (debt_payments / monthly_income) * 100.0 if monthly_income > 0 else 0
    free_cashflow = monthly_income - monthly_expenses - debt_payments
    
    stage = 4
    bottlenecks = []
    
    if runway_months < 3.0:
        stage = min(stage, 1)
        bottlenecks.append(f"Emergency Fund inadequate ({round(runway_months, 1)} months vs 3-6 months minimum).")
    if not has_basic_insurance:
        stage = min(stage, 2)
        bottlenecks.append("Lacking basic medical/life protection; catastrophic event could wipe out savings.")
    if high_interest_debt > 0:
        stage = min(stage, 3)
        bottlenecks.append(f"Carrying high-interest debt ({high_interest_debt:,.2f}) >10% APR which outpaces investment returns.")
        
    # Ramit Sethi Conscious Spending Target breakdown
    target_fixed = monthly_income * 0.55
    target_invest = monthly_income * 0.10
    target_savings = monthly_income * 0.10
    target_guilt_free = monthly_income * 0.25
    
    return {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "free_cashflow": round(free_cashflow, 2),
        "emergency_runway_months": round(runway_months, 1),
        "debt_to_income_pct": round(dti_ratio, 2),
        "current_waterfall_stage": stage,
        "stage_label": {
            1: "Stage 1: Liquid Emergency Fund Buffer",
            2: "Stage 2: Foundation Risk Protection (Insurance)",
            3: "Stage 3: High-Interest Debt Liquidation",
            4: "Stage 4: Long-Term Asset Allocation & Wealth Accumulation"
        }[stage],
        "bottlenecks": bottlenecks,
        "conscious_spending_ideal_split": {
            "fixed_costs_50_to_60_pct": round(target_fixed, 2),
            "investments_10_pct": round(target_invest, 2),
            "savings_goals_5_to_10_pct": round(target_savings, 2),
            "guilt_free_spending_20_to_35_pct": round(target_guilt_free, 2)
        },
        "advisory_directive": (
            "PROHIBIT risky or speculative investments until Stages 1-3 are cleared." if stage < 4
            else "APPROVED for long-term equity/ETF indexing and portfolio allocation."
        )
    }


def calc_portfolio_metrics(annual_returns, risk_free_rate=0.04):
    """
    Calculates CAGR, StDev, Sharpe Ratio, Sortino Ratio, and Max Drawdown from annual returns.
    annual_returns = [0.15, -0.05, 0.22, 0.08, -0.12]
    """
    n = len(annual_returns)
    if n == 0:
        return {}
        
    cum_wealth = 1.0
    wealth_index = [1.0]
    for r in annual_returns:
        cum_wealth *= (1.0 + r)
        wealth_index.append(cum_wealth)
        
    cagr = (cum_wealth ** (1.0 / n)) - 1.0
    mean_ret = sum(annual_returns) / n
    variance = sum((r - mean_ret) ** 2 for r in annual_returns) / (n - 1) if n > 1 else 0.0
    stdev = math.sqrt(variance)
    
    downside_var = sum((r - risk_free_rate) ** 2 for r in annual_returns if r < risk_free_rate) / (n - 1) if n > 1 else 0.0
    downside_stdev = math.sqrt(downside_var)
    
    sharpe = (mean_ret - risk_free_rate) / stdev if stdev > 0 else 0.0
    sortino = (mean_ret - risk_free_rate) / downside_stdev if downside_stdev > 0 else 0.0
    
    # Max Drawdown
    peak = wealth_index[0]
    max_dd = 0.0
    for w in wealth_index:
        if w > peak:
            peak = w
        dd = (w - peak) / peak
        if dd < max_dd:
            max_dd = dd
            
    return {
        "periods_count": n,
        "cumulative_return_pct": round((cum_wealth - 1.0) * 100.0, 2),
        "cagr_pct": round(cagr * 100.0, 2),
        "annualized_volatility_pct": round(stdev * 100.0, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "max_drawdown_pct": round(max_dd * 100.0, 2),
        "risk_free_rate_used": risk_free_rate
    }


def main():
    parser = argparse.ArgumentParser(description="Deterministic Financial Calculator Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcommand: compound
    p_comp = subparsers.add_parser("compound", help="Compound interest and future value calculation")
    p_comp.add_argument("--principal", type=float, required=True, help="Initial principal")
    p_comp.add_argument("--rate", type=float, required=True, help="Annual interest rate in %% (e.g. 8.0)")
    p_comp.add_argument("--years", type=float, required=True, help="Investment horizon in years")
    p_comp.add_argument("--monthly-contrib", type=float, default=0.0, help="Monthly contribution")
    p_comp.add_argument("--inflation", type=float, default=0.0, help="Annual inflation rate in %%")
    p_comp.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Subcommand: monte-carlo
    p_mc = subparsers.add_parser("monte-carlo", help="Monte Carlo retirement simulation & safe withdrawal")
    p_mc.add_argument("--portfolio", type=float, required=True, help="Initial portfolio balance")
    p_mc.add_argument("--annual-withdrawal", type=float, required=True, help="Annual withdrawal amount")
    p_mc.add_argument("--years", type=int, default=30, help="Retirement duration in years (default: 30)")
    p_mc.add_argument("--mean-return", type=float, default=7.0, help="Expected annual mean return in %%")
    p_mc.add_argument("--stdev", type=float, default=15.0, help="Annual volatility in %%")
    p_mc.add_argument("--inflation", type=float, default=3.0, help="Annual inflation in %%")
    p_mc.add_argument("--sims", type=int, default=10000, help="Number of simulation runs (default: 10000)")
    p_mc.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Subcommand: amortization
    p_am = subparsers.add_parser("amortization", help="Mortgage/loan amortization & prepayment savings")
    p_am.add_argument("--principal", type=float, required=True, help="Loan principal amount")
    p_am.add_argument("--rate", type=float, required=True, help="Annual interest rate in %% (e.g. 7.5)")
    p_am.add_argument("--years", type=float, required=True, help="Loan term in years")
    p_am.add_argument("--extra-monthly", type=float, default=0.0, help="Extra monthly principal payment")
    p_am.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Subcommand: debt-payoff
    p_dp = subparsers.add_parser("debt-payoff", help="Avalanche vs Snowball debt payoff optimizer")
    p_dp.add_argument("--debts-json", type=str, required=True, help="JSON list of debts [{'name': 'A', 'balance': 5000, 'rate': 20.0, 'min_payment': 150}]")
    p_dp.add_argument("--extra-budget", type=float, default=0.0, help="Extra monthly snowball/avalanche budget")
    p_dp.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Subcommand: life-energy
    p_le = subparsers.add_parser("life-energy", help="Vicki Robin Life Energy price converter")
    p_le.add_argument("--price", type=float, required=True, help="Price of the item or purchase")
    p_le.add_argument("--gross-income", type=float, required=True, help="Gross income")
    p_le.add_argument("--period", choices=["monthly", "annual"], default="monthly", help="Income period")
    p_le.add_argument("--hours-week", type=float, default=40.0, help="Weekly work hours")
    p_le.add_argument("--tax-rate", type=float, default=15.0, help="Effective tax rate in %%")
    p_le.add_argument("--commute-hours", type=float, default=5.0, help="Weekly commute hours")
    p_le.add_argument("--work-costs", type=float, default=0.0, help="Weekly work related costs")
    p_le.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Subcommand: waterfall-audit
    p_wf = subparsers.add_parser("waterfall-audit", help="Financial Waterfall & Health Check")
    p_wf.add_argument("--monthly-income", type=float, required=True, help="Total monthly net income")
    p_wf.add_argument("--monthly-expenses", type=float, required=True, help="Essential monthly living expenses")
    p_wf.add_argument("--emergency-fund", type=float, required=True, help="Current liquid emergency fund cash")
    p_wf.add_argument("--debt-payments", type=float, default=0.0, help="Monthly debt repayment commitments")
    p_wf.add_argument("--high-interest-debt", type=float, default=0.0, help="High interest (>10%% APR) debt balance")
    p_wf.add_argument("--has-insurance", action="store_true", default=True, help="Has basic health/term insurance")
    p_wf.add_argument("--no-insurance", dest="has_insurance", action="store_false")
    p_wf.add_argument("--json", action="store_true", help="Output raw JSON")
    
    # Subcommand: portfolio-metrics
    p_pm = subparsers.add_parser("portfolio-metrics", help="Portfolio CAGR, Sharpe, Sortino, Max Drawdown")
    p_pm.add_argument("--returns", type=str, required=True, help="Comma-separated annual returns, e.g. '0.15,-0.05,0.22,0.08'")
    p_pm.add_argument("--risk-free", type=float, default=0.04, help="Risk-free rate (default: 0.04)")
    p_pm.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if args.command == "compound":
        res = calc_compound_interest(args.principal, args.rate, args.years, args.monthly_contrib, args.inflation)
    elif args.command == "monte-carlo":
        res = calc_monte_carlo(args.portfolio, args.annual_withdrawal, args.years, args.mean_return, args.stdev, args.inflation, args.sims)
    elif args.command == "amortization":
        res = calc_amortization(args.principal, args.rate, args.years, args.extra_monthly)
    elif args.command == "debt-payoff":
        try:
            debts = json.loads(args.debts_json)
        except Exception as e:
            sys.exit(f"Invalid JSON format for debts: {e}")
        res = calc_debt_payoff(debts, args.extra_budget)
    elif args.command == "life-energy":
        res = calc_life_energy(args.price, args.gross_income, args.period, args.hours_week, args.tax_rate, args.commute_hours, args.work_costs)
    elif args.command == "waterfall-audit":
        res = calc_waterfall_audit(args.monthly_income, args.monthly_expenses, args.emergency_fund, args.debt_payments, args.high_interest_debt, args.has_insurance)
    elif args.command == "portfolio-metrics":
        rets = [float(x.strip()) for x in args.returns.split(",") if x.strip()]
        res = calc_portfolio_metrics(rets, args.risk_free)
    else:
        res = {"error": "Unknown command"}
        
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
