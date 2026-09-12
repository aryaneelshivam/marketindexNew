"""
Fundamentals Analysis Module.
Fetches and structures detailed company fundamentals including:
- Company Profile & Market Cap
- Valuation Metrics (P/E, Forward P/E, PEG, P/B, P/S, EV/EBITDA, EV/Sales)
- Profitability & Margins (ROE, ROA, Operating Margin, Net Margin, Gross Margin)
- Balance Sheet & Financial Health (Debt, Cash, Debt/Equity, Current & Quick Ratios)
- Growth & Cash Flows (Revenue Growth YoY, Earnings Growth YoY, Operating Cash Flow, Free Cash Flow)
- Dividends & Payouts (Yield, Rate, Payout Ratio, Ex-Dividend Date)
- Shareholding & Beta (Beta, Insider %, Institutional %)
- Analyst Price Targets & Consensus (Mean Target, Upside %, Recommendation)
"""

import time
import logging
from typing import Dict, Any, Optional
import yfinance as yf

logger = logging.getLogger("marketindex.fundamentals")

# In-memory cache for fundamentals (TTL: 1 hour)
FUNDAMENTALS_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TIMESTAMPS: Dict[str, float] = {}
CACHE_TTL = 3600  # 1 hour


def format_currency_amount(val: Optional[float], currency: str = "INR") -> str:
    """Formats large currency amounts into Crores (for INR) or Billions (for USD)."""
    if val is None or val == 0:
        return "--"
    
    prefix = "₹" if currency == "INR" else ("$" if currency == "USD" else "")
    
    if currency == "INR":
        abs_val = abs(val)
        if abs_val >= 1e7:
            # 1 Crore = 10,000,000
            cr = val / 1e7
            if abs(cr) >= 100000:
                return f"{prefix}{cr/100000:.2f} Lk Cr"
            return f"{prefix}{cr:,.2f} Cr"
        elif abs_val >= 1e5:
            return f"{prefix}{val/1e5:.2f} Lakh"
        return f"{prefix}{val:,.2f}"
    else:
        abs_val = abs(val)
        if abs_val >= 1e9:
            return f"{prefix}{val/1e9:.2f}B"
        elif abs_val >= 1e6:
            return f"{prefix}{val/1e6:.2f}M"
        return f"{prefix}{val:,.2f}"


def get_stock_fundamentals(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves and parses deep fundamentals for a given symbol.
    Supports symbols with or without exchange suffix (e.g. 'TCS' -> 'TCS.NS').
    """
    clean_sym = symbol.strip().upper()
    cache_key = clean_sym

    # Check cache
    if cache_key in FUNDAMENTALS_CACHE:
        if (time.time() - CACHE_TIMESTAMPS.get(cache_key, 0)) < CACHE_TTL:
            return FUNDAMENTALS_CACHE[cache_key]

    # Try fetching with exact symbol, then fallback to .NS if no dot
    ticker_symbols_to_try = [clean_sym]
    if "." not in clean_sym:
        ticker_symbols_to_try.append(f"{clean_sym}.NS")

    ticker_obj = None
    info = {}
    resolved_symbol = clean_sym

    for sym in ticker_symbols_to_try:
        try:
            t = yf.Ticker(sym)
            inf = t.info
            if inf and len(inf) > 10 and (inf.get("regularMarketPrice") or inf.get("currentPrice") or inf.get("shortName")):
                ticker_obj = t
                info = inf
                resolved_symbol = sym
                break
        except Exception as e:
            logger.warning(f"Error fetching ticker {sym}: {e}")

    if not info or not ticker_obj:
        return None

    currency = info.get("currency", "INR")
    cmp = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0.0

    # Valuation Metrics
    market_cap = info.get("marketCap")
    trailing_pe = info.get("trailingPE")
    forward_pe = info.get("forwardPE")
    peg_ratio = info.get("pegRatio")
    price_to_book = info.get("priceToBook")
    price_to_sales = info.get("priceToSalesTrailing12Months")
    ev = info.get("enterpriseValue")
    ev_to_ebitda = info.get("enterpriseToEbitda")
    ev_to_revenue = info.get("enterpriseToRevenue")

    # Profitability & Margins
    roe = info.get("returnOnEquity")
    roa = info.get("returnOnAssets")
    operating_margin = info.get("operatingMargins")
    profit_margin = info.get("profitMargins")
    gross_margin = info.get("grossMargins")
    ebitda = info.get("ebitda")

    # Balance Sheet & Solvency
    total_cash = info.get("totalCash")
    total_debt = info.get("totalDebt")
    debt_to_equity = info.get("debtToEquity")
    current_ratio = info.get("currentRatio")
    quick_ratio = info.get("quickRatio")
    book_value = info.get("bookValue")
    net_debt = (total_debt - total_cash) if (total_debt is not None and total_cash is not None) else None

    # Cash Flow & Growth
    total_revenue = info.get("totalRevenue")
    rev_growth = info.get("revenueGrowth")
    earnings_growth = info.get("earningsGrowth")
    op_cashflow = info.get("operatingCashflow")
    free_cashflow = info.get("freeCashflow")

    # Dividend Metrics
    div_rate = info.get("dividendRate")
    div_yield = info.get("dividendYield")
    # yfinance sometimes gives dividendYield as percentage (1.5) or decimal (0.015)
    if div_yield is not None:
        div_yield_pct = div_yield * 100 if div_yield < 1.0 else div_yield
    else:
        div_yield_pct = None
    payout_ratio = info.get("payoutRatio")
    if payout_ratio is not None:
        payout_ratio_pct = payout_ratio * 100 if payout_ratio <= 1.0 else payout_ratio
    else:
        payout_ratio_pct = None

    # Share Stats & Ownership
    shares_out = info.get("sharesOutstanding")
    float_shares = info.get("floatShares")
    beta = info.get("beta")
    insider_pct = info.get("heldPercentInsiders")
    inst_pct = info.get("heldPercentInstitutions")

    # Analyst Targets & Recommendation
    target_mean = info.get("targetMeanPrice")
    target_high = info.get("targetHighPrice")
    target_low = info.get("targetLowPrice")
    target_median = info.get("targetMedianPrice")
    recommendation = info.get("recommendationKey")
    analyst_count = info.get("numberOfAnalystOpinions")

    upside_pct = None
    if target_mean and cmp and cmp > 0:
        upside_pct = round(((target_mean - cmp) / cmp) * 100, 2)

    data = {
        "symbol": resolved_symbol,
        "name": info.get("shortName") or info.get("longName") or resolved_symbol,
        "currency": currency,
        "cmp": round(float(cmp), 2) if cmp else None,
        "company_profile": {
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "website": info.get("website"),
            "country": info.get("country"),
            "employees": info.get("fullTimeEmployees"),
            "summary": info.get("longBusinessSummary"),
        },
        "market_cap": {
            "raw": market_cap,
            "formatted": format_currency_amount(market_cap, currency)
        },
        "valuation": {
            "trailing_pe": round(trailing_pe, 2) if trailing_pe is not None else None,
            "forward_pe": round(forward_pe, 2) if forward_pe is not None else None,
            "peg_ratio": round(peg_ratio, 2) if peg_ratio is not None else None,
            "price_to_book": round(price_to_book, 2) if price_to_book is not None else None,
            "price_to_sales": round(price_to_sales, 2) if price_to_sales is not None else None,
            "enterprise_value_raw": ev,
            "enterprise_value": format_currency_amount(ev, currency),
            "ev_to_ebitda": round(ev_to_ebitda, 2) if ev_to_ebitda is not None else None,
            "ev_to_revenue": round(ev_to_revenue, 2) if ev_to_revenue is not None else None,
        },
        "profitability_and_margins": {
            "roe_pct": round(roe * 100, 2) if roe is not None else None,
            "roa_pct": round(roa * 100, 2) if roa is not None else None,
            "operating_margin_pct": round(operating_margin * 100, 2) if operating_margin is not None else None,
            "profit_margin_pct": round(profit_margin * 100, 2) if profit_margin is not None else None,
            "gross_margin_pct": round(gross_margin * 100, 2) if gross_margin is not None else None,
            "ebitda_raw": ebitda,
            "ebitda": format_currency_amount(ebitda, currency),
        },
        "balance_sheet": {
            "total_cash_raw": total_cash,
            "total_cash": format_currency_amount(total_cash, currency),
            "total_debt_raw": total_debt,
            "total_debt": format_currency_amount(total_debt, currency),
            "net_debt": format_currency_amount(net_debt, currency) if net_debt is not None else "--",
            "debt_to_equity": round(debt_to_equity, 2) if debt_to_equity is not None else None,
            "current_ratio": round(current_ratio, 2) if current_ratio is not None else None,
            "quick_ratio": round(quick_ratio, 2) if quick_ratio is not None else None,
            "book_value_per_share": round(book_value, 2) if book_value is not None else None,
        },
        "growth_and_cashflows": {
            "total_revenue_raw": total_revenue,
            "total_revenue": format_currency_amount(total_revenue, currency),
            "revenue_growth_yoy_pct": round(rev_growth * 100, 2) if rev_growth is not None else None,
            "earnings_growth_yoy_pct": round(earnings_growth * 100, 2) if earnings_growth is not None else None,
            "operating_cashflow_raw": op_cashflow,
            "operating_cashflow": format_currency_amount(op_cashflow, currency),
            "free_cashflow_raw": free_cashflow,
            "free_cashflow": format_currency_amount(free_cashflow, currency),
        },
        "dividends": {
            "dividend_rate": round(div_rate, 2) if div_rate is not None else None,
            "dividend_yield_pct": round(div_yield_pct, 2) if div_yield_pct is not None else None,
            "payout_ratio_pct": round(payout_ratio_pct, 2) if payout_ratio_pct is not None else None,
            "ex_dividend_date": info.get("exDividendDate"),
        },
        "share_stats": {
            "trailing_eps": round(info.get("trailingEps"), 2) if info.get("trailingEps") is not None else None,
            "forward_eps": round(info.get("forwardEps"), 2) if info.get("forwardEps") is not None else None,
            "beta": round(beta, 2) if beta is not None else None,
            "shares_outstanding": shares_out,
            "float_shares": float_shares,
            "insider_holding_pct": round(insider_pct * 100, 2) if insider_pct is not None else None,
            "institutional_holding_pct": round(inst_pct * 100, 2) if inst_pct is not None else None,
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "50d_average": info.get("fiftyDayAverage"),
            "200d_average": info.get("twoHundredDayAverage"),
        },
        "analyst_estimates": {
            "recommendation": (recommendation.replace("_", " ").title() if recommendation else "--"),
            "target_mean_price": round(target_mean, 2) if target_mean is not None else None,
            "target_high_price": round(target_high, 2) if target_high is not None else None,
            "target_low_price": round(target_low, 2) if target_low is not None else None,
            "target_median_price": round(target_median, 2) if target_median is not None else None,
            "upside_downside_pct": upside_pct,
            "number_of_analysts": analyst_count,
        }
    }

    # Cache result
    FUNDAMENTALS_CACHE[cache_key] = data
    CACHE_TIMESTAMPS[cache_key] = time.time()
    return data
