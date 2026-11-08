#!/usr/bin/env python3
"""
financial_mcp_server.py
Zero-Dependency Fast MCP stdio Server for Institutional Financial Operations.
Provides deterministic calculation tools to prevent LLM financial hallucinations.
Works with Antigravity, Claude Desktop, Cursor, Windsurf, and VS Code.
"""

import sys
import json
import math
import os

# Import computation logic from financial_calculator
from financial_calculator import (
    calc_compound_interest,
    calc_monte_carlo,
    calc_amortization,
    calc_debt_payoff,
    calc_life_energy,
    calc_waterfall_audit,
    calc_portfolio_metrics
)

SERVER_NAME = "financial-engine"
SERVER_VERSION = "1.0.0"
SUPPORTED_PROTOCOLS = ["2024-11-05", "2025-03-26", "2025-06-18"]

TOOLS = [
    {
        "name": "finance_compound_interest",
        "description": "Calculate deterministic compound interest, future value (nominal and inflation-adjusted), and yearly wealth accumulation milestones.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "principal": {"type": "number", "description": "Initial capital invested"},
                "rate": {"type": "number", "description": "Annual expected interest/return rate in percent (e.g. 8.0)"},
                "years": {"type": "number", "description": "Investment time horizon in years"},
                "monthly_contribution": {"type": "number", "description": "Monthly recurrent capital addition", "default": 0.0},
                "inflation": {"type": "number", "description": "Annual inflation rate in percent for real purchasing power adjustment", "default": 0.0}
            },
            "required": ["principal", "rate", "years"]
        }
    },
    {
        "name": "finance_monte_carlo",
        "description": "Simulate retirement portfolio longevity using 10,000 Monte Carlo runs. Computes survival probability and 10th/50th/90th percentile ending wealth under the Trinity 4% rule.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "portfolio": {"type": "number", "description": "Initial nest egg / portfolio size"},
                "annual_withdrawal": {"type": "number", "description": "Annual withdrawal cash amount"},
                "years": {"type": "integer", "description": "Retirement horizon in years", "default": 30},
                "mean_return": {"type": "number", "description": "Expected annual mean return in %", "default": 7.0},
                "stdev": {"type": "number", "description": "Annual portfolio volatility standard deviation in %", "default": 15.0},
                "inflation": {"type": "number", "description": "Annual inflation rate in %", "default": 3.0},
                "sims": {"type": "integer", "description": "Number of stochastic runs", "default": 10000}
            },
            "required": ["portfolio", "annual_withdrawal"]
        }
    },
    {
        "name": "finance_amortization",
        "description": "Calculate loan/mortgage monthly payments (P&I), total interest, and savings from extra monthly principal payments.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "principal": {"type": "number", "description": "Total loan principal borrowed"},
                "rate": {"type": "number", "description": "Annual interest rate in percent (e.g. 7.5)"},
                "years": {"type": "number", "description": "Loan term in years"},
                "extra_monthly": {"type": "number", "description": "Extra monthly principal prepayments to accelerate payoff", "default": 0.0}
            },
            "required": ["principal", "rate", "years"]
        }
    },
    {
        "name": "finance_debt_payoff",
        "description": "Evaluate multiple debt liabilities. Compares Debt Avalanche (highest APR first, mathematically optimal) vs Debt Snowball (smallest balance first, psychological wins).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "debts": {
                    "type": "array",
                    "description": "List of active debts with name, balance, APR rate, and minimum monthly payment",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "balance": {"type": "number"},
                            "rate": {"type": "number"},
                            "min_payment": {"type": "number"}
                        },
                        "required": ["name", "balance", "rate", "min_payment"]
                    }
                },
                "extra_monthly_budget": {
                    "type": "number",
                    "description": "Additional discretionary cash allocated each month above minimum payments",
                    "default": 0.0
                }
            },
            "required": ["debts"]
        }
    },
    {
        "name": "finance_life_energy",
        "description": "Convert purchase cost into hours/days of irreplaceable life energy based on Vicki Robin's 'Your Money or Your Life' real hourly wage formula.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_price": {"type": "number", "description": "Price of the prospective item or service"},
                "gross_income": {"type": "number", "description": "User income amount"},
                "income_period": {"type": "string", "enum": ["monthly", "annual"], "default": "monthly"},
                "work_hours_per_week": {"type": "number", "default": 40.0},
                "tax_rate_pct": {"type": "number", "default": 15.0},
                "weekly_commute_hours": {"type": "number", "default": 5.0},
                "weekly_work_expenses": {"type": "number", "default": 0.0}
            },
            "required": ["item_price", "gross_income"]
        }
    },
    {
        "name": "finance_waterfall_audit",
        "description": "Audit personal financial health against the 4-Stage Financial Waterfall (Emergency Buffer -> Core Insurance -> Toxic Debt Eradication -> Asset Allocation) and Ramit Sethi Conscious Spending targets.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "monthly_income": {"type": "number", "description": "Net monthly household cash inflow"},
                "monthly_expenses": {"type": "number", "description": "Essential monthly living expenses"},
                "emergency_fund": {"type": "number", "description": "Current liquid cash reserve in money market/savings"},
                "debt_payments": {"type": "number", "description": "Total monthly debt servicing commitments", "default": 0.0},
                "high_interest_debt": {"type": "number", "description": "Outstanding balance of consumer debt with >10% APR", "default": 0.0},
                "has_basic_insurance": {"type": "boolean", "description": "Whether user has health and term life protection", "default": True}
            },
            "required": ["monthly_income", "monthly_expenses", "emergency_fund"]
        }
    },
    {
        "name": "finance_portfolio_metrics",
        "description": "Compute historical portfolio statistics: Compound Annual Growth Rate (CAGR), Annual Volatility (StDev), Sharpe Ratio, Sortino Ratio, and Maximum Historical Drawdown.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "annual_returns": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "List of annual decimal returns, e.g. [0.15, -0.05, 0.22, 0.08]"
                },
                "risk_free_rate": {
                    "type": "number",
                    "description": "Annual risk-free benchmark rate (e.g. 0.04 for 4%)",
                    "default": 0.04
                }
            },
            "required": ["annual_returns"]
        }
    }
]


def send(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def reply(req_id, result):
    send({"jsonrpc": "2.0", "id": req_id, "result": result})


def reply_error(req_id, code, message):
    send({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def execute_tool(name, args):
    if name == "finance_compound_interest":
        return calc_compound_interest(
            principal=args.get("principal", 0.0),
            annual_rate_pct=args.get("rate", 0.0),
            years=args.get("years", 1.0),
            monthly_contrib=args.get("monthly_contribution", 0.0),
            inflation_pct=args.get("inflation", 0.0)
        )
    elif name == "finance_monte_carlo":
        return calc_monte_carlo(
            initial_portfolio=args.get("portfolio", 0.0),
            annual_withdrawal=args.get("annual_withdrawal", 0.0),
            years=args.get("years", 30),
            mean_return_pct=args.get("mean_return", 7.0),
            stdev_pct=args.get("stdev", 15.0),
            inflation_pct=args.get("inflation", 3.0),
            num_sims=args.get("sims", 10000)
        )
    elif name == "finance_amortization":
        return calc_amortization(
            principal=args.get("principal", 0.0),
            annual_rate_pct=args.get("rate", 0.0),
            years=args.get("years", 1.0),
            extra_monthly=args.get("extra_monthly", 0.0)
        )
    elif name == "finance_debt_payoff":
        return calc_debt_payoff(
            debts=args.get("debts", []),
            extra_monthly_budget=args.get("extra_monthly_budget", 0.0)
        )
    elif name == "finance_life_energy":
        return calc_life_energy(
            item_price=args.get("item_price", 0.0),
            gross_income=args.get("gross_income", 0.0),
            income_period=args.get("income_period", "monthly"),
            work_hours_week=args.get("work_hours_per_week", 40.0),
            tax_rate_pct=args.get("tax_rate_pct", 15.0),
            weekly_commute_hours=args.get("weekly_commute_hours", 5.0),
            weekly_work_costs=args.get("weekly_work_expenses", 0.0)
        )
    elif name == "finance_waterfall_audit":
        return calc_waterfall_audit(
            monthly_income=args.get("monthly_income", 0.0),
            monthly_expenses=args.get("monthly_expenses", 0.0),
            emergency_fund=args.get("emergency_fund", 0.0),
            debt_payments=args.get("debt_payments", 0.0),
            high_interest_debt=args.get("high_interest_debt", 0.0),
            has_basic_insurance=args.get("has_basic_insurance", True)
        )
    elif name == "finance_portfolio_metrics":
        return calc_portfolio_metrics(
            annual_returns=args.get("annual_returns", []),
            risk_free_rate=args.get("risk_free_rate", 0.04)
        )
    else:
        raise ValueError(f"Unknown tool: {name}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception as e:
            continue
            
        req_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params", {})
        
        if method == "initialize":
            req_ver = params.get("protocolVersion")
            proto = req_ver if req_ver in SUPPORTED_PROTOCOLS else SUPPORTED_PROTOCOLS[0]
            reply(req_id, {
                "protocolVersion": proto,
                "capabilities": {
                    "tools": {"listChanged": False}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                },
                "instructions": (
                    "Deterministic Financial Calculation & Fiduciary Advisory Engine. "
                    "Use these tools strictly for compound interest, Monte Carlo retirement, "
                    "amortization, debt payoff comparison, life energy conversions, and waterfall audits. "
                    "Never guess or compute financial math inside natural language."
                )
            })
        elif method in ("notifications/initialized", "notifications/cancelled"):
            continue
        elif method == "ping":
            reply(req_id, {})
        elif method == "tools/list":
            reply(req_id, {"tools": TOOLS})
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                data = execute_tool(tool_name, tool_args)
                reply(req_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(data, indent=2)
                        }
                    ],
                    "isError": False
                })
            except Exception as err:
                reply(req_id, {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing {tool_name}: {err}"
                        }
                    ],
                    "isError": True
                })
        else:
            if req_id is not None:
                reply_error(req_id, -32601, f"Method not found: {method}")


if __name__ == "__main__":
    main()
