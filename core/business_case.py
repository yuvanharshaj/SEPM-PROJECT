"""Business Case, Cost-Benefit Analysis & Economic Feasibility.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 4:
    Project Evaluation, Economic Feasibility, Cost-Benefit Analysis,
    Cash Flow Forecasting, Net Present Value (NPV), Return on Investment (ROI),
    Payback Period.

Formulas:
    1. Net Cash Flow at Year t:
       NCF_t = Benefit_t - RecurringCost_t

    2. Discounted Cash Flow at Year t:
       DCF_t = NCF_t / ((1 + r)^t)  where r is the discount rate (e.g. 0.10 for 10%)

    3. Net Present Value (NPV):
       NPV = -Initial_Investment + sum_{t=1}^N (DCF_t)

    4. Return on Investment (ROI):
       Total_Net_Benefit = sum_{t=1}^N (NCF_t) - Initial_Investment
       ROI (%) = (Total_Net_Benefit / Initial_Investment) * 100

    5. Discounted ROI (%):
       Discounted_ROI (%) = (NPV / Initial_Investment) * 100

    6. Payback Period (Undiscounted & Discounted):
       Year where cumulative net cash flow turns non-negative, with linear interpolation:
       Payback = Year_{t-1} + (Remaining_Deficit / CashFlow_t)
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class CashFlowYear:
    year: int
    benefit: float
    recurring_cost: float
    net_cash_flow: float
    discount_factor: float
    discounted_cash_flow: float
    cumulative_cash_flow: float
    cumulative_discounted: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "benefit": round(self.benefit, 2),
            "recurring_cost": round(self.recurring_cost, 2),
            "net_cash_flow": round(self.net_cash_flow, 2),
            "discount_factor": round(self.discount_factor, 4),
            "discounted_cash_flow": round(self.discounted_cash_flow, 2),
            "cumulative_cash_flow": round(self.cumulative_cash_flow, 2),
            "cumulative_discounted": round(self.cumulative_discounted, 2),
        }


@dataclass
class BusinessCaseResult:
    initial_investment: float
    discount_rate_pct: float
    years: int
    yearly_flows: List[CashFlowYear]
    total_benefits: float
    total_recurring_costs: float
    net_profit: float
    npv: float
    roi_pct: float
    discounted_roi_pct: float
    payback_period_years: Optional[float]
    discounted_payback_years: Optional[float]
    is_financially_viable: bool
    summary_verdict: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "initial_investment": round(self.initial_investment, 2),
            "discount_rate_pct": round(self.discount_rate_pct, 2),
            "years": self.years,
            "total_benefits": round(self.total_benefits, 2),
            "total_recurring_costs": round(self.total_recurring_costs, 2),
            "net_profit": round(self.net_profit, 2),
            "npv": round(self.npv, 2),
            "roi_pct": round(self.roi_pct, 2),
            "discounted_roi_pct": round(self.discounted_roi_pct, 2),
            "payback_period_years": round(self.payback_period_years, 2) if self.payback_period_years is not None else None,
            "discounted_payback_years": round(self.discounted_payback_years, 2) if self.discounted_payback_years is not None else None,
            "is_financially_viable": self.is_financially_viable,
            "summary_verdict": self.summary_verdict,
            "yearly_flows": [yf.to_dict() for yf in self.yearly_flows],
        }


def _calculate_payback(cumulative_series: List[float], annual_flows: List[float]) -> Optional[float]:
    """Calculate payback year with linear interpolation."""
    # Year 0 is -initial_investment
    for i in range(1, len(cumulative_series)):
        if cumulative_series[i] >= 0:
            deficit_before = abs(cumulative_series[i - 1])
            flow_this_year = annual_flows[i]
            if flow_this_year > 0:
                fraction = deficit_before / flow_this_year
                return (i - 1) + min(1.0, max(0.0, fraction))
            return float(i)
    return None


def evaluate_business_case(
    initial_investment: float,
    annual_benefits: List[float],
    annual_costs: List[float] | float = 0.0,
    discount_rate_pct: float = 10.0,
) -> BusinessCaseResult:
    """Perform comprehensive Cost-Benefit Analysis (NPV, ROI, Payback).

    Args:
        initial_investment: Capital expenditure / upfront dev cost (> 0).
        annual_benefits: List of projected benefits per year.
        annual_costs: List of recurring maintenance/operational costs per year, or single scalar.
        discount_rate_pct: Annual discount rate as a percentage (e.g. 10.0 for 10%).

    Returns:
        BusinessCaseResult with yearly cash flows and executive evaluation.
    """
    if initial_investment <= 0:
        raise ValueError(f"Initial investment must be positive, got {initial_investment}")

    n_years = len(annual_benefits)
    if n_years == 0:
        raise ValueError("Must provide at least one year of projected benefits")

    if isinstance(annual_costs, (int, float)):
        costs_list = [float(annual_costs)] * n_years
    else:
        costs_list = [float(c) for c in annual_costs]
        if len(costs_list) < n_years:
            costs_list.extend([costs_list[-1] if costs_list else 0.0] * (n_years - len(costs_list)))
        elif len(costs_list) > n_years:
            costs_list = costs_list[:n_years]

    r = discount_rate_pct / 100.0

    # Year 0 Baseline
    year_zero = CashFlowYear(
        year=0,
        benefit=0.0,
        recurring_cost=initial_investment,
        net_cash_flow=-initial_investment,
        discount_factor=1.0,
        discounted_cash_flow=-initial_investment,
        cumulative_cash_flow=-initial_investment,
        cumulative_discounted=-initial_investment,
    )

    flows: List[CashFlowYear] = [year_zero]
    cum_undisc = -initial_investment
    cum_disc = -initial_investment
    total_benefits = sum(annual_benefits)
    total_costs = sum(costs_list)

    undisc_annual = [-initial_investment]
    disc_annual = [-initial_investment]

    for yr in range(1, n_years + 1):
        ben = float(annual_benefits[yr - 1])
        cost = float(costs_list[yr - 1])
        ncf = ben - cost
        dfactor = 1.0 / ((1.0 + r) ** yr)
        dcf = ncf * dfactor

        cum_undisc += ncf
        cum_disc += dcf

        undisc_annual.append(ncf)
        disc_annual.append(dcf)

        flows.append(
            CashFlowYear(
                year=yr,
                benefit=ben,
                recurring_cost=cost,
                net_cash_flow=ncf,
                discount_factor=dfactor,
                discounted_cash_flow=dcf,
                cumulative_cash_flow=cum_undisc,
                cumulative_discounted=cum_disc,
            )
        )

    # Net Present Value = cumulative discounted cash flow at final year
    npv = cum_disc

    # Net Profit = sum of net cash flows - initial investment
    net_profit = sum(f.net_cash_flow for f in flows[1:]) - initial_investment

    # Simple ROI (%)
    roi_pct = (net_profit / initial_investment) * 100.0

    # Discounted ROI (%)
    discounted_roi_pct = (npv / initial_investment) * 100.0

    cum_undisc_list = [f.cumulative_cash_flow for f in flows]
    cum_disc_list = [f.cumulative_discounted for f in flows]

    payback_undisc = _calculate_payback(cum_undisc_list, undisc_annual)
    payback_disc = _calculate_payback(cum_disc_list, disc_annual)

    is_viable = npv > 0 and roi_pct > 0

    if is_viable:
        verdict = (
            f"Financially VIABLE: Generates positive NPV of {npv:,.2f} at a {discount_rate_pct:.1f}% "
            f"discount rate with an ROI of {roi_pct:.1f}%. Capital investment is recovered in "
            f"{f'{payback_undisc:.2f} years' if payback_undisc else 'N/A'} "
            f"(discounted payback: {f'{payback_disc:.2f} years' if payback_disc else 'exceeds project lifespan'})."
        )
    else:
        verdict = (
            f"Financially HIGH-RISK / UNVIABLE: Generates negative NPV of {npv:,.2f}. "
            f"Returns fail to overcome the {discount_rate_pct:.1f}% cost of capital over {n_years} years."
        )

    return BusinessCaseResult(
        initial_investment=initial_investment,
        discount_rate_pct=discount_rate_pct,
        years=n_years,
        yearly_flows=flows,
        total_benefits=total_benefits,
        total_recurring_costs=total_costs,
        net_profit=net_profit,
        npv=npv,
        roi_pct=roi_pct,
        discounted_roi_pct=discounted_roi_pct,
        payback_period_years=payback_undisc,
        discounted_payback_years=payback_disc,
        is_financially_viable=is_viable,
        summary_verdict=verdict,
    )
