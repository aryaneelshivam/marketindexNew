"""
FastAPI Server for Stock Technical Analysis, Fundamental Research & Sector Screener.
Optimized for standalone deployment on Vercel Serverless and containerized runtimes.

Provides:
- Sector Categorization (Finance & Banking, FMCG, IT, Automobile, Healthcare & Pharma, Oil Gas & Energy, Metals & Infra)
- Full Technical Indicator Suite (SMA, EMA, ADX, RSI, MACD, ATR, OBV, Volume, Support & Resistance)
- 100-Point Weighted Technical Health Scoring Model
- In-depth Company Fundamentals & Valuation Ratios
- Multi-Timeframe & Historical Window Selection
- RESTful JSON API with OpenAPI/Swagger Documentation
- CSV Export
"""

import io
import csv
import logging
from typing import Optional
from fastapi import FastAPI, Query, BackgroundTasks, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sectors import SECTOR_STOCKS, get_all_tickers
from fetcher import market_cache, VALID_PERIODS, TIMEFRAME_CONFIG
from fundamentals import get_stock_fundamentals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("marketindex.main")

app = FastAPI(
    title="MarketIndex Pro - Technical & Fundamental Screener API",
    description=(
        "Institutional-grade stock technical analysis, scoring, and fundamental analysis API "
        "covering top Indian equities (NSE) across 7 sectors."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS for universal integration (web apps, mobile apps, bots)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="API Root & Discovery")
async def root_discovery(request: Request):
    """
    Root discovery endpoint providing service status, available documentation links,
    and a catalogue of API endpoints.
    """
    base_url = str(request.base_url).rstrip("/")
    return {
        "service": "MarketIndex Pro Screener API",
        "status": "operational",
        "version": "2.0.0",
        "documentation": {
            "swagger_ui": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc",
            "openapi_schema": f"{base_url}/openapi.json"
        },
        "endpoints": {
            "sectors": f"{base_url}/api/sectors",
            "timeframes": f"{base_url}/api/timeframes",
            "periods": f"{base_url}/api/periods",
            "stocks": f"{base_url}/api/stocks?timeframe=1d&period=1y&sector=All",
            "single_stock": f"{base_url}/api/stock/{{symbol}}?timeframe=1d&period=1y",
            "fundamentals": f"{base_url}/api/stock/{{symbol}}/fundamentals",
            "cache_status": f"{base_url}/api/status?timeframe=1d&period=1y",
            "rescan": f"{base_url}/api/scan (POST)",
            "export_csv": f"{base_url}/api/export?timeframe=1d&period=1y&sector=All"
        }
    }


@app.get("/api/sectors", summary="List Industry Sectors")
async def get_sectors():
    """Returns available sectors, stock counts, and constituent tickers."""
    sectors_data = []
    for sector, stocks in SECTOR_STOCKS.items():
        sectors_data.append({
            "sector": sector,
            "count": len(stocks),
            "stocks": stocks
        })
    return sectors_data


@app.get("/api/timeframes", summary="List Candle Timeframes")
async def get_timeframes():
    """Returns available analysis timeframes (candle intervals)."""
    return [
        {"id": "15m", "label": "15 Min",  "badge": "15m", "description": "Intraday Scalping"},
        {"id": "1h",  "label": "1 Hour",  "badge": "1H",  "description": "Short-Term Hourly Swing"},
        {"id": "1d",  "label": "Daily",   "badge": "1D",  "description": "Daily Swing & Trend (Default)"},
        {"id": "1wk", "label": "Weekly",  "badge": "1W",  "description": "Positional Multi-Week Trend"},
        {"id": "1mo", "label": "Monthly", "badge": "1M",  "description": "Long-Term Macro Trend"},
    ]


@app.get("/api/periods", summary="List Historical Windows")
async def get_periods():
    """Returns available historical data lookback windows (period)."""
    return [
        {"id": "1mo",  "label": "1 Month",   "description": "Last 30 days of data"},
        {"id": "3mo",  "label": "3 Months",  "description": "Last 3 months of data"},
        {"id": "6mo",  "label": "6 Months",  "description": "Last 6 months of data"},
        {"id": "1y",   "label": "1 Year",    "description": "Last 1 year of data (default)"},
        {"id": "2y",   "label": "2 Years",   "description": "Last 2 years of data"},
        {"id": "5y",   "label": "5 Years",   "description": "Last 5 years of data"},
    ]


@app.get("/api/stocks", summary="Technical Screener Matrix")
async def get_stocks(
    sector: Optional[str] = Query("All", description="Sector name filter or 'All'"),
    timeframe: str = Query("1d",  description="Candle interval: 15m, 1h, 1d, 1wk, 1mo"),
    period: Optional[str] = Query(None, description="Historical window: 1mo, 3mo, 6mo, 1y, 2y, 5y"),
    search: Optional[str] = Query(None, description="Filter by ticker symbol or company name"),
    force: bool = Query(False, description="Force live re-fetch from market source")
):
    """
    Returns full tabular technical analysis dataset for the selected timeframe + period.
    Includes 100-point Technical Health Score, SMA, EMA, ADX, RSI, MACD, ATR, OBV, Volume, and Pivot Levels.
    """
    tf = timeframe.lower().strip()
    pd_val = period.lower().strip() if period else None
    data = market_cache.get_data(sector_filter=sector, timeframe=tf, period=pd_val, force_refresh=force)

    # Server-side search filter
    if search:
        s_lower = search.lower().strip()
        data = [
            item for item in data
            if s_lower in item["symbol"].lower() or s_lower in item.get("name", "").lower()
        ]

    bullish_count = len([x for x in data if "Bullish" in x.get("trend_verdict", "")])
    bearish_count = len([x for x in data if "Bearish" in x.get("trend_verdict", "")])
    status = market_cache.cache_status(tf, pd_val)

    return {
        "summary": {
            "timeframe":     tf,
            "period":        pd_val or TIMEFRAME_CONFIG.get(tf, {}).get("period", "1y"),
            "total_stocks":  len(data),
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "last_updated":  status["last_updated"],
            "is_updating":   status["is_updating"],
        },
        "data": data
    }


@app.get("/api/stock/{symbol}", summary="Single Stock Technical & Chart Data")
async def get_single_stock(
    symbol: str,
    timeframe: str = Query("1d",  description="Candle interval: 15m, 1h, 1d, 1wk, 1mo"),
    period: Optional[str] = Query(None, description="Historical window: 1mo, 3mo, 6mo, 1y, 2y, 5y")
):
    """
    Returns deep-dive technical indicators, complete OHLCV candles, and computed indicator series
    (EMA 20/50, SMA 50/200, RSI 14, MACD line/signal/hist, Volume 20D average) for charting.
    """
    tf     = timeframe.lower().strip()
    pd_val = period.lower().strip() if period else None
    stock  = market_cache.get_single_stock(symbol, timeframe=tf, period=pd_val)
    if not stock:
        return JSONResponse(status_code=404, content={"error": f"Symbol '{symbol}' not found or loading"})
    return stock


@app.get("/api/stock/{symbol}/fundamentals", summary="Detailed Company Fundamentals")
@app.get("/api/fundamentals/{symbol}", summary="Detailed Company Fundamentals (Alias)")
async def get_fundamentals(symbol: str):
    """
    Returns comprehensive institutional fundamentals for a given ticker symbol:
    - Valuation: P/E, Forward P/E, PEG, P/B, P/S, EV/EBITDA, EV/Revenue
    - Profitability: ROE, ROA, Operating Margin, Net Margin, Gross Margin, EBITDA
    - Balance Sheet: Total Debt, Total Cash, Net Debt, Debt/Equity, Current & Quick Ratios
    - Growth & Cash Flows: Revenue & Earnings Growth YoY, Operating & Free Cash Flow
    - Dividends: Yield, Rate, Payout Ratio, Ex-Dividend Date
    - Share Stats & Beta: Trailing/Forward EPS, Beta, Insider & Institutional Holdings
    - Analyst Targets: Recommendation Consensus, Target Mean/High/Low, Upside %
    - Company Profile: Sector, Industry, Website, Full Business Summary
    """
    data = get_stock_fundamentals(symbol)
    if not data:
        return JSONResponse(status_code=404, content={"error": f"Fundamentals not found for symbol '{symbol}'"})
    return data


@app.post("/api/scan", summary="Trigger Background Market Scan")
async def trigger_scan(
    background_tasks: BackgroundTasks,
    timeframe: str = Query("1d",  description="Candle interval to refresh: 15m, 1h, 1d, 1wk, 1mo"),
    period: Optional[str] = Query(None, description="Historical window: 1mo, 3mo, 6mo, 1y, 2y, 5y")
):
    """Triggers asynchronous re-scan and technical calculations for a given timeframe+period combo."""
    tf     = timeframe.lower().strip()
    pd_val = period.lower().strip() if period else None
    status = market_cache.cache_status(tf, pd_val)

    if status["is_updating"]:
        return {"status": "already_updating", "message": f"Scan for '{status['key']}' is already in progress."}

    background_tasks.add_task(market_cache.refresh_sync, timeframe=tf, period=pd_val)
    return {"status": "started", "key": status["key"], "message": f"Background scan triggered for {status['key']}."}


@app.get("/api/status", summary="Cache & Scan Status")
async def get_status(
    timeframe: str = Query("1d"),
    period: Optional[str] = Query(None)
):
    """Returns the current cache freshness and scanning status for a timeframe+period combo."""
    tf     = timeframe.lower().strip()
    pd_val = period.lower().strip() if period else None
    return market_cache.cache_status(tf, pd_val)


@app.get("/api/export", summary="Export CSV Matrix")
async def export_csv(
    sector: Optional[str] = Query("All"),
    timeframe: str = Query("1d"),
    period: Optional[str] = Query(None)
):
    """Exports technical analysis tabular dataset to a CSV file for the selected timeframe+period."""
    tf     = timeframe.lower().strip()
    pd_val = period.lower().strip() if period else None
    stocks = market_cache.get_data(sector_filter=sector, timeframe=tf, period=pd_val)

    output = io.StringIO()
    writer = csv.writer(output)

    # Write CSV Header
    headers = [
        "Ticker", "Company Name", "Sector", "Timeframe", "Exchange", "CMP (INR)", "Change (INR)", "Change (%)",
        "Technical Score (/100)", "Technical Grade",
        "EMA 20", "EMA 50", "SMA 50", "SMA 200", "Trend Verdict",
        "ADX (14)", "+DI", "-DI", "ADX Strength Label",
        "RSI (14)", "RSI Status", "MACD Line", "MACD Signal", "MACD Hist", "MACD Signal Verdict",
        "ATR (14)", "ATR (%)",
        "Current Volume", "20D Avg Volume", "Volume Ratio", "Volume Verdict", "OBV Trend",
        "Central Pivot", "S1", "S2", "S3", "R1", "R2", "R3",
        "Nearest Support", "Support Distance (%)", "Nearest Resistance", "Resistance Distance (%)",
        "52W High", "52W Low", "% from 52W High"
    ]
    writer.writerow(headers)

    for s in stocks:
        writer.writerow([
            s.get("symbol"), s.get("name"), s.get("sector"), tf.upper(), s.get("exchange"),
            s.get("cmp"), s.get("change"), s.get("pct_change"),
            s.get("technical_score"), s.get("technical_grade"),
            s.get("ema20"), s.get("ema50"), s.get("sma50"), s.get("sma200"), s.get("trend_verdict"),
            s.get("adx"), s.get("plus_di"), s.get("minus_di"), s.get("adx_label"),
            s.get("rsi"), s.get("rsi_status"), s.get("macd"), s.get("macd_signal"), s.get("macd_hist"), s.get("macd_status"),
            s.get("atr"), s.get("atr_pct"),
            s.get("volume"), s.get("volume_20d_avg"), s.get("vol_ratio"), s.get("vol_verdict"), s.get("obv_trend"),
            s.get("pivot"), s.get("s1"), s.get("s2"), s.get("s3"), s.get("r1"), s.get("r2"), s.get("r3"),
            s.get("nearest_support"), s.get("support_dist_pct"), s.get("nearest_resistance"), s.get("resistance_dist_pct"),
            s.get("high_52w"), s.get("low_52w"), s.get("pct_from_52w_high")
        ])

    output.seek(0)
    period_tag = pd_val or TIMEFRAME_CONFIG.get(tf, {}).get("period", "1y")
    filename = f"market_technical_{tf}_{period_tag}_{sector.lower().replace(' ', '_')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)