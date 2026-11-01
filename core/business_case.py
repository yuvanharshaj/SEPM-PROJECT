"""Business Case, Cost-Benefit Analysis & Economic Feasibility.

Syllabus Reference:
    VTU 24CS51 Software Engineering & Project Management - Module 3:
    Project Evaluation, Economic Feasibility, Cost-Benefit Analysis,
    Cash Flow Forecasting, Net Present Value (NPV), Return on Investment (ROI),
    Payback Period, Risk Evaluation via Scenarios (Expected NPV / EMV),
    and Risk-Adjusted Discount Rate (RADR).
Course Outcome:
    CO3: Formulate Project Business Case, Cash Flow Projections and Economic Feasibility.

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
       Payback = Year_{t-1} + (Remaining_Deficit_{t-1} / CashFlow_t)

    7. Scenario Risk Evaluation (Expected Monetary Value / Expected NPV):
       E(NPV) = sum(p_i * NPV_i) for i in {Optimistic, Most Likely, Pessimistic}
       Var(NPV) = sum(p_i * (NPV_i - E(NPV))^2)
       SD(NPV) = sqrt(Var(NPV))

    8. Risk-Adjusted Discount Rate (RADR):
       r_adjusted = r_base + r_risk_premium
       NPV_RADR = -Initial_Investment + sum_{t=1}^N [ NCF_t / ((1 + r_adjusted)^t) ]
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import math


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


@dataclass
class ScenarioItem:
    name: str
    probability: float
    initial_investment: float
    annual_benefits: List[float]
    annual_costs: List[float]
    npv: float
    roi_pct: float
    payback_years: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "probability": round(self.probability, 2),
            "initial_investment": round(self.initial_investment, 2),
            "annual_benefits": [round(b, 2) for b in self.annual_benefits],
            "annual_costs": [round(c, 2) for c in self.annual_costs],
            "npv": round(self.npv, 2),
            "roi_pct": round(self.roi_pct, 2),
            "payback_years": round(self.payback_years, 2) if self.payback_years is not None else None,
        }


@dataclass
class ScenarioEvaluationResult:
    scenarios: List[ScenarioItem]
    expected_npv: float
    expected_roi_pct: float
    npv_variance: float
    npv_standard_deviation: float
    risk_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expected_npv": round(self.expected_npv, 2),
            "expected_roi_pct": round(self.expected_roi_pct, 2),
            "npv_variance": round(self.npv_variance, 2),
            "npv_standard_deviation": round(self.npv_standard_deviation, 2),
            "risk_summary": self.risk_summary,
            "scenarios": [s.to_dict() for s in self.scenarios],
        }


@dataclass
class RiskAdjustedDiscountResult:
    base_discount_rate_pct: float
    risk_premium_pct: float
    adjusted_discount_rate_pct: float
    base_npv: float
    adjusted_npv: float
    npv_delta: float
    base_payback: Optional[float]
    adjusted_payback: Optional[float]
    is_viable_at_radr: bool
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_discount_rate_pct": round(self.base_discount_rate_pct, 2),
            "risk_premium_pct": round(self.risk_premium_pct, 2),
            "adjusted_discount_rate_pct": round(self.adjusted_discount_rate_pct, 2),
            "base_npv": round(self.base_npv, 2),
            "adjusted_npv": round(self.adjusted_npv, 2),
            "npv_delta": round(self.npv_delta, 2),
            "base_payback": round(self.base_payback, 2) if self.base_payback is not None else None,
            "adjusted_payback": round(self.adjusted_payback, 2) if self.adjusted_payback is not None else None,
            "is_viable_at_radr": self.is_viable_at_radr,
            "summary": self.summary,
        }


def _calculate_payback(cumulative_series: List[float], annual_flows: List[float]) -> Optional[float]:
    """Calculate payback year with linear interpolation."""
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
    """Perform comprehensive Cost-Benefit Analysis (NPV, ROI, Payback)."""
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

    npv = cum_disc
    net_profit = sum(f.net_cash_flow for f in flows[1:]) - initial_investment
    roi_pct = (net_profit / initial_investment) * 100.0
    discounted_roi_pct = (npv / initial_investment) * 100.0

    cum_undisc_list = [f.cumulative_cash_flow for f in flows]
    cum_disc_list = [f.cumulative_discounted for f in flows]

    payback_undisc = _calculate_payback(cum_undisc_list, undisc_annual)
    payback_disc = _calculate_payback(cum_disc_list, disc_annual)

    is_viable = npv > 0 and roi_pct > 0

    if is_viable:
        verdict = (
            f"Financially VIABLE: Generates positive NPV of ${npv:,.2f} at a {discount_rate_pct:.1f}% "
            f"discount rate with an ROI of {roi_pct:.1f}%. Capital investment is recovered in "
            f"{f'{payback_undisc:.2f} years' if payback_undisc else 'N/A'} "
            f"(discounted payback: {f'{payback_disc:.2f} years' if payback_disc else 'exceeds project lifespan'})."
        )
    else:
        verdict = (
            f"Financially HIGH-RISK / UNVIABLE: Generates negative NPV of ${npv:,.2f}. "
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


def evaluate_scenario_risk(
    base_investment: float,
    base_benefits: List[float],
    base_costs: List[float],
    discount_rate_pct: float = 10.0,
    optimistic_multiplier: float = 1.25,
    pessimistic_multiplier: float = 0.70,
    probabilities: Tuple[float, float, float] = (0.25, 0.50, 0.25),
) -> ScenarioEvaluationResult:
    """Evaluate financial risk across Optimistic, Most Likely, and Pessimistic scenarios.

    Args:
        base_investment: Nominal initial capital.
        base_benefits: Nominal annual cash inflows.
        base_costs: Nominal annual operating costs.
        discount_rate_pct: Base cost of capital.
        optimistic_multiplier: Benefit scaler for optimistic scenario (e.g. 1.25 for +25%).
        pessimistic_multiplier: Benefit scaler for pessimistic scenario (e.g. 0.70 for -30%).
        probabilities: Probabilities for (Optimistic, Most Likely, Pessimistic), summing to 1.0.

    Returns:
        ScenarioEvaluationResult with Expected NPV (EMV), variance, and standard deviation.
    """
    p_opt, p_likely, p_pess = probabilities
    total_p = p_opt + p_likely + p_pess
    if not math.isclose(total_p, 1.0, rel_tol=1e-3):
        p_opt, p_likely, p_pess = p_opt / total_p, p_likely / total_p, p_pess / total_p

    # 1. Optimistic Scenario: +benefit, -costs, slightly lower Capex
    opt_inv = base_investment * 0.95
    opt_bens = [b * optimistic_multiplier for b in base_benefits]
    opt_costs = [c * 0.90 for c in base_costs]
    res_opt = evaluate_business_case(opt_inv, opt_bens, opt_costs, discount_rate_pct)

    # 2. Most Likely Scenario: nominal
    res_likely = evaluate_business_case(base_investment, base_benefits, base_costs, discount_rate_pct)

    # 3. Pessimistic Scenario: -benefit, +costs, slightly higher Capex
    pess_inv = base_investment * 1.15
    pess_bens = [b * pessimistic_multiplier for b in base_benefits]
    pess_costs = [c * 1.15 for c in base_costs]
    res_pess = evaluate_business_case(pess_inv, pess_bens, pess_costs, discount_rate_pct)

    scenarios = [
        ScenarioItem(
            name="Optimistic",
            probability=p_opt,
            initial_investment=opt_inv,
            annual_benefits=opt_bens,
            annual_costs=opt_costs,
            npv=res_opt.npv,
            roi_pct=res_opt.roi_pct,
            payback_years=res_opt.payback_period_years,
        ),
        ScenarioItem(
            name="Most Likely",
            probability=p_likely,
            initial_investment=base_investment,
            annual_benefits=base_benefits,
            annual_costs=base_costs,
            npv=res_likely.npv,
            roi_pct=res_likely.roi_pct,
            payback_years=res_likely.payback_period_years,
        ),
        ScenarioItem(
            name="Pessimistic",
            probability=p_pess,
            initial_investment=pess_inv,
            annual_benefits=pess_bens,
            annual_costs=pess_costs,
            npv=res_pess.npv,
            roi_pct=res_pess.roi_pct,
            payback_years=res_pess.payback_period_years,
        ),
    ]

    expected_npv = (p_opt * res_opt.npv) + (p_likely * res_likely.npv) + (p_pess * res_pess.npv)
    expected_roi = (p_opt * res_opt.roi_pct) + (p_likely * res_likely.roi_pct) + (p_pess * res_pess.roi_pct)

    variance_npv = (
        p_opt * ((res_opt.npv - expected_npv) ** 2)
        + p_likely * ((res_likely.npv - expected_npv) ** 2)
        + p_pess * ((res_pess.npv - expected_npv) ** 2)
    )
    sd_npv = math.sqrt(variance_npv)

    if expected_npv > 0 and res_pess.npv >= 0:
        summary = f"Low Downside Risk: Expected NPV is ${expected_npv:,.2f} with all scenarios yielding positive returns."
    elif expected_npv > 0:
        summary = f"Moderate Risk: Expected NPV is positive (${expected_npv:,.2f}), but pessimistic scenario yields ${res_pess.npv:,.2f}."
    else:
        summary = f"High Downside Risk: Expected NPV is negative (${expected_npv:,.2f}). Project faces adverse return distribution."

    return ScenarioEvaluationResult(
        scenarios=scenarios,
        expected_npv=expected_npv,
        expected_roi_pct=expected_roi,
        npv_variance=variance_npv,
        npv_standard_deviation=sd_npv,
        risk_summary=summary,
    )


def evaluate_radr(
    initial_investment: float,
    annual_benefits: List[float],
    annual_costs: List[float],
    base_discount_rate_pct: float = 10.0,
    risk_premium_pct: float = 3.0,
) -> RiskAdjustedDiscountResult:
    """Evaluate business case using Risk-Adjusted Discount Rate (RADR)."""
    base_res = evaluate_business_case(initial_investment, annual_benefits, annual_costs, base_discount_rate_pct)
    adj_rate = base_discount_rate_pct + risk_premium_pct
    radr_res = evaluate_business_case(initial_investment, annual_benefits, annual_costs, adj_rate)

    delta = radr_res.npv - base_res.npv
    viable = radr_res.npv > 0

    if viable:
        summary = (
            f"Resilient: Project remains viable under RADR of {adj_rate:.1f}% "
            f"({base_discount_rate_pct:.1f}% base + {risk_premium_pct:.1f}% risk premium), "
            f"yielding NPV of ${radr_res.npv:,.2f}."
        )
    else:
        summary = (
            f"Vulnerable: Applying a {risk_premium_pct:.1f}% risk premium increases the hurdle rate to {adj_rate:.1f}%, "
            f"causing NPV to drop into negative territory (${radr_res.npv:,.2f})."
        )

    return RiskAdjustedDiscountResult(
        base_discount_rate_pct=base_discount_rate_pct,
        risk_premium_pct=risk_premium_pct,
        adjusted_discount_rate_pct=adj_rate,
        base_npv=base_res.npv,
        adjusted_npv=radr_res.npv,
        npv_delta=delta,
        base_payback=base_res.payback_period_years,
        adjusted_payback=radr_res.payback_period_years,
        is_viable_at_radr=viable,
        summary=summary,
    )
