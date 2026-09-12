# MarketIndex Pro API

An institutional-grade, headless **FastAPI** backend service for real-time technical analysis, 100-point multi-factor technical scoring, and in-depth fundamental research across 85+ top Indian equities (NSE) organized across 7 major sectors.

[![Hosted on Vercel](https://img.shields.io/badge/Hosted%20on-Vercel-black?style=flat&logo=vercel)](https://marketindex-new.vercel.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌐 Live Service & Interactive Documentation

- **Production Base URL**: `https://marketindex-new.vercel.app`
- **Interactive Swagger UI**: [`https://marketindex-new.vercel.app/docs`](https://marketindex-new.vercel.app/docs)
- **ReDoc API Reference**: [`https://marketindex-new.vercel.app/redoc`](https://marketindex-new.vercel.app/redoc)
- **OpenAPI 3.1 JSON Schema**: [`https://marketindex-new.vercel.app/openapi.json`](https://marketindex-new.vercel.app/openapi.json)

---

## 📑 Table of Contents

1. [Key Features](#-key-features)
2. [API Reference & Endpoints](#-api-reference--endpoints)
   - [1. Root & Discovery](#1-root--discovery)
   - [2. List Sectors](#2-list-sectors)
   - [3. List Candle Timeframes](#3-list-candle-timeframes)
   - [4. List Historical Windows (Period)](#4-list-historical-windows-period)
   - [5. Technical Screener Matrix](#5-technical-screener-matrix)
   - [6. Single Stock Deep-Dive & Chart Series](#6-single-stock-deep-dive--chart-series)
   - [7. Detailed Company Fundamentals](#7-detailed-company-fundamentals)
   - [8. Trigger Market Re-Scan](#8-trigger-market-re-scan)
   - [9. Cache Freshness Status](#9-cache-freshness-status)
   - [10. Export Screener Matrix to CSV](#10-export-screener-matrix-to-csv)
3. [100-Point Weighted Technical Scoring Model](#-100-point-weighted-technical-scoring-model)
4. [Technical Analysis Methodology](#-technical-analysis-methodology)
5. [Universe & Sector Taxonomy](#-universe--sector-taxonomy)
6. [Quickstart Code Examples](#-quickstart-code-examples)
7. [Local Development](#-local-development)
8. [Vercel Deployment Guide](#-vercel-deployment-guide)

---

## 🚀 Key Features

- **7 Industry Sectors Covered**: Finance & Banking, FMCG, IT, Automobile, Healthcare & Pharma, Oil, Gas & Energy, Metals & Infra (85+ National Stock Exchange bluechip & high-beta tickers).
- **6 Core Technical Dimensions**: Trend Direction (EMA/SMA), Trend Strength (Wilder's ADX, +DI/-DI), Momentum (RSI 14, MACD 12/26/9), Volatility (ATR 14, ATR %), Volume Flow (Volume Ratio, OBV), and Price Structure (Floor Pivot S1–S3 / R1–R3, 52W High/Low).
- **Calibrated 100-Point Technical Health Score**: Institutional multi-pillar model assigning weights to Trend (30%), Momentum (25%), Strength (15%), Volume (15%), and Structure (15%).
- **Deep Fundamental Analysis**: Valuation multiples (P/E, Forward P/E, PEG, P/B, EV/EBITDA), margins (ROE, ROA, Operating/Net Margin), solvency (Debt, Cash, Debt/Equity), cash flows, dividends, and Wall Street / Dalal Street analyst price targets and upside potential.
- **Dual Lookback Controls**: Independent parameters for Candle Intervals (`timeframe`) and Historical Windows (`period`).
- **Chart-Ready Output**: Returns full OHLCV candlestick series alongside computed indicator series (EMA 20/50, SMA 50/200, RSI, MACD line/signal/hist, 20D volume average).
- **CORS Enabled**: Built-in `CORSMiddleware` with universal origins (`*`) allowing seamless consumption from React, Vue, Next.js, Flutter, or iOS/Android frontends.

---

## 📡 API Reference & Endpoints

### 1. Root & Discovery
Returns system status, documentation URLs, and a catalog of all API endpoints.

- **Method**: `GET`
- **Path**: `/`
- **Parameters**: None

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/"
```

#### Example Response (200 OK):
```json
{
  "service": "MarketIndex Pro Screener API",
  "status": "operational",
  "version": "2.0.0",
  "documentation": {
    "swagger_ui": "https://marketindex-new.vercel.app/docs",
    "redoc": "https://marketindex-new.vercel.app/redoc",
    "openapi_schema": "https://marketindex-new.vercel.app/openapi.json"
  },
  "endpoints": {
    "sectors": "https://marketindex-new.vercel.app/api/sectors",
    "timeframes": "https://marketindex-new.vercel.app/api/timeframes",
    "periods": "https://marketindex-new.vercel.app/api/periods",
    "stocks": "https://marketindex-new.vercel.app/api/stocks?timeframe=1d&period=1y&sector=All",
    "single_stock": "https://marketindex-new.vercel.app/api/stock/{symbol}?timeframe=1d&period=1y",
    "fundamentals": "https://marketindex-new.vercel.app/api/stock/{symbol}/fundamentals",
    "cache_status": "https://marketindex-new.vercel.app/api/status?timeframe=1d&period=1y",
    "rescan": "https://marketindex-new.vercel.app/api/scan (POST)",
    "export_csv": "https://marketindex-new.vercel.app/api/export?timeframe=1d&period=1y&sector=All"
  }
}
```

---

### 2. List Sectors
Returns all 7 industry sectors, stock counts, and constituent NSE symbols.

- **Method**: `GET`
- **Path**: `/api/sectors`
- **Parameters**: None

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/sectors"
```

#### Example Response (200 OK):
```json
[
  {
    "sector": "Finance & Banking",
    "count": 15,
    "stocks": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "BAJFINANCE.NS", "..."]
  },
  {
    "sector": "IT",
    "count": 12,
    "stocks": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "PERSISTENT.NS", "..."]
  }
]
```

---

### 3. List Candle Timeframes
Returns all supported candlestick intervals for technical calculations.

- **Method**: `GET`
- **Path**: `/api/timeframes`
- **Parameters**: None

#### Supported Values:
| `id` | Label | Description |
| :--- | :--- | :--- |
| `15m` | 15 Min | Intraday scalping & fast momentum breakouts |
| `1h` | 1 Hour | Short-term hourly swing trading |
| `1d` | Daily *(Default)* | Classic multi-day swing trading benchmark |
| `1wk` | Weekly | Positional multi-week trend following |
| `1mo` | Monthly | Long-term macro cycle analysis |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/timeframes"
```

---

### 4. List Historical Windows (Period)
Returns all supported historical lookback data windows for screening and price history.

- **Method**: `GET`
- **Path**: `/api/periods`
- **Parameters**: None

#### Supported Values:
| `id` | Label | Description |
| :--- | :--- | :--- |
| `1mo` | 1 Month | Last 30 calendar days |
| `3mo` | 3 Months | Last quarter of price data |
| `6mo` | 6 Months | Last half-year of price data |
| `1y` | 1 Year *(Default)* | Standard 1-year trailing window |
| `2y` | 2 Years | Medium-term historical lookback |
| `5y` | 5 Years | Multi-year historical lookback |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/periods"
```

---

### 5. Technical Screener Matrix
Retrieves the complete tabular technical analysis dataset and 100-point scores across all constituent stocks.

- **Method**: `GET`
- **Path**: `/api/stocks`

#### Query Parameters:
| Parameter | Type | Default | Options / Format | Description |
| :--- | :--- | :--- | :--- | :--- |
| `sector` | `string` | `"All"` | `All`, `Finance & Banking`, `FMCG`, `IT`, `Automobile`, `Healthcare & Pharma`, `Oil Gas & Energy`, `Metals & Infra` | Sector filter |
| `timeframe` | `string` | `"1d"` | `15m`, `1h`, `1d`, `1wk`, `1mo` | Candlestick interval |
| `period` | `string` | `"1y"` | `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y` | Historical lookback window |
| `search` | `string` | `null` | Any text (e.g. `TCS`, `Tata`, `Bank`) | Filter by ticker or company name |
| `force` | `boolean`| `false`| `true`, `false` | Force live re-fetch bypassing memory cache |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/stocks?sector=IT&timeframe=1d&period=6mo"
```

#### Example Response (200 OK):
```json
{
  "summary": {
    "timeframe": "1d",
    "period": "6mo",
    "total_stocks": 12,
    "bullish_count": 8,
    "bearish_count": 2,
    "last_updated": 1741804200.5,
    "is_updating": false
  },
  "data": [
    {
      "symbol": "INFY.NS",
      "name": "Infosys Limited",
      "sector": "IT",
      "exchange": "NSE",
      "cmp": 1845.30,
      "change": 18.25,
      "pct_change": 1.00,
      "technical_score": 88.0,
      "technical_grade": "Elite Bullish",
      "grade_badge": "score-elite",
      "score_breakdown": {
        "trend": { "score": 30.0, "max": 30, "label": "Strong Uptrend (Above All Key MAs)" },
        "strength": { "score": 15.0, "max": 15, "label": "Strong Trend (+DI > -DI & ADX >= 25)" },
        "momentum": { "score": 25.0, "max": 25, "label": "Bullish Momentum (RSI 55-68 & MACD Bullish)" },
        "volume": { "score": 8.0, "max": 15, "label": "Moderate Volume" },
        "structure": { "score": 10.0, "max": 15, "label": "Above Central Pivot & Near 52W High" }
      },
      "sma20": 1820.40,
      "sma50": 1780.15,
      "sma200": 1650.80,
      "ema20": 1832.10,
      "ema50": 1795.50,
      "trend_verdict": "Strong Bullish",
      "trend_color": "bull",
      "adx": 28.4,
      "plus_di": 29.1,
      "minus_di": 14.2,
      "adx_label": "Strong Bullish Trend",
      "rsi": 62.4,
      "rsi_status": "Bullish",
      "macd": 14.85,
      "macd_signal": 11.20,
      "macd_hist": 3.65,
      "macd_status": "Bullish Expansion",
      "atr": 28.50,
      "atr_pct": 1.54,
      "volume": 4521000,
      "volume_20d_avg": 3890000,
      "vol_ratio": 1.16,
      "vol_verdict": "Above Average",
      "obv": 128500000,
      "obv_trend": "Accumulation / Rising",
      "pivot": 1838.00,
      "r1": 1855.20,
      "s1": 1828.10,
      "r2": 1872.40,
      "s2": 1810.90,
      "r3": 1889.60,
      "s3": 1793.80,
      "nearest_support": "S1 (1828.10)",
      "support_dist_pct": 0.93,
      "nearest_resistance": "R1 (1855.20)",
      "resistance_dist_pct": 0.54,
      "high_52w": 1991.45,
      "low_52w": 1358.35,
      "pct_from_52w_high": -7.34,
      "pct_from_52w_low": 35.85,
      "timeframe": "1d",
      "period": "6mo"
    }
  ]
}
```

---

### 6. Single Stock Deep-Dive & Chart Series
Retrieves deep-dive technical metrics, complete historical OHLCV candlestick points, and computed indicator series for charting.

- **Method**: `GET`
- **Path**: `/api/stock/{symbol}`

#### Path Parameters:
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `symbol` | `string` | NSE ticker symbol including suffix (e.g. `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`) |

#### Query Parameters:
| Parameter | Type | Default | Options | Description |
| :--- | :--- | :--- | :--- | :--- |
| `timeframe` | `string` | `"1d"` | `15m`, `1h`, `1d`, `1wk`, `1mo` | Candle interval |
| `period` | `string` | `"1y"` | `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y` | Historical window |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/stock/RELIANCE.NS?timeframe=1d&period=3mo"
```

#### Key Elements in Response:
- **`candles`**: Array of `{ date, open, high, low, close, volume }` objects.
- **`chart_data`**: Parallel synchronized time series arrays:
  - `dates`: ISO date strings.
  - `ema20`: 20-period Exponential Moving Average series.
  - `ema50`: 50-period Exponential Moving Average series.
  - `sma50`: 50-period Simple Moving Average series.
  - `sma200`: 200-period Simple Moving Average series.
  - `rsi`: 14-period Relative Strength Index series.
  - `macd_line`: MACD Fast line (12-26 EMA).
  - `macd_signal`: MACD Signal line (9 EMA of MACD).
  - `macd_hist`: MACD Histogram (MACD line - Signal line).
  - `volume`: Raw volume per candle.
  - `vol_avg`: 20-period Volume Moving Average series.

---

### 7. Detailed Company Fundamentals
Retrieves comprehensive institutional fundamental data, financial ratios, balance sheet metrics, dividends, and analyst consensus targets.

- **Method**: `GET`
- **Path**: `/api/stock/{symbol}/fundamentals` *(or `/api/fundamentals/{symbol}`)*

#### Path Parameters:
| Parameter | Type | Description |
| :--- | :--- | :--- |
| `symbol` | `string` | NSE ticker symbol (e.g. `TCS.NS`, `INFY.NS`) |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/stock/TCS.NS/fundamentals"
```

#### Example Response (200 OK):
```json
{
  "symbol": "TCS.NS",
  "name": "Tata Consultancy Services Limited",
  "currency": "INR",
  "cmp": 3950.00,
  "company_profile": {
    "sector": "Technology",
    "industry": "Information Technology Services",
    "country": "India",
    "website": "https://www.tcs.com",
    "employees": 601546,
    "summary": "Tata Consultancy Services Limited provides information technology (IT) services, consulting, and business solutions worldwide..."
  },
  "valuation": {
    "market_cap": 14290000000000,
    "market_cap_fmt": "₹14.29 Lakh Cr",
    "trailing_pe": 30.45,
    "forward_pe": 26.80,
    "peg_ratio": 2.85,
    "price_to_book": 13.80,
    "price_to_sales": 5.80,
    "enterprise_value": 14120000000000,
    "enterprise_value_fmt": "₹14.12 Lakh Cr",
    "ev_to_ebitda": 21.40,
    "ev_to_revenue": 5.75
  },
  "profitability": {
    "return_on_equity": 0.495,
    "return_on_equity_fmt": "49.5%",
    "return_on_assets": 0.285,
    "return_on_assets_fmt": "28.5%",
    "operating_margins": 0.245,
    "operating_margins_fmt": "24.5%",
    "profit_margins": 0.198,
    "profit_margins_fmt": "19.8%",
    "gross_margins": 0.412,
    "gross_margins_fmt": "41.2%",
    "ebitda": 624500000000,
    "ebitda_fmt": "₹62,450 Cr"
  },
  "balance_sheet": {
    "total_cash": 125000000000,
    "total_cash_fmt": "₹12,500 Cr",
    "total_debt": 8500000000,
    "total_debt_fmt": "₹850 Cr",
    "net_debt": -116500000000,
    "net_debt_fmt": "Net Cash: ₹11,650 Cr",
    "debt_to_equity": 8.5,
    "current_ratio": 2.45,
    "quick_ratio": 2.10,
    "book_value": 286.20
  },
  "growth_and_cashflow": {
    "revenue_growth_yoy": 0.076,
    "revenue_growth_fmt": "7.6%",
    "earnings_growth_yoy": 0.082,
    "earnings_growth_fmt": "8.2%",
    "operating_cash_flow": 482000000000,
    "operating_cash_flow_fmt": "₹48,200 Cr",
    "free_cash_flow": 441000000000,
    "free_cash_flow_fmt": "₹44,100 Cr",
    "trailing_eps": 129.70,
    "forward_eps": 147.40
  },
  "dividends": {
    "dividend_yield": 0.021,
    "dividend_yield_fmt": "2.10%",
    "dividend_rate": 83.00,
    "payout_ratio": 0.64,
    "payout_ratio_fmt": "64.0%",
    "ex_dividend_date": "2024-10-18"
  },
  "shareholding_and_beta": {
    "beta": 0.72,
    "promoter_holding": 0.718,
    "promoter_holding_fmt": "71.8%",
    "institutional_holding": 0.201,
    "institutional_holding_fmt": "20.1%"
  },
  "analyst_targets": {
    "recommendation": "BUY",
    "target_mean": 4350.00,
    "target_high": 4800.00,
    "target_low": 3600.00,
    "potential_upside_pct": 10.13,
    "analyst_count": 42
  }
}
```

---

### 8. Trigger Market Re-Scan
Asynchronously triggers re-fetching and recalculation of all technical metrics for a given timeframe + period combination.

- **Method**: `POST`
- **Path**: `/api/scan`

#### Query Parameters:
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `timeframe` | `string` | `"1d"` | Candle interval (`15m`, `1h`, `1d`, `1wk`, `1mo`) |
| `period` | `string` | `null` | Historical lookback (`1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`) |

#### Example Request:
```bash
curl -X POST "https://marketindex-new.vercel.app/api/scan?timeframe=1d&period=1y"
```

#### Example Response (200 OK):
```json
{
  "status": "started",
  "key": "1d|1y",
  "message": "Background scan triggered for 1d|1y."
}
```

---

### 9. Cache Freshness Status
Returns the status, timestamp, and update state for a given timeframe + period combination.

- **Method**: `GET`
- **Path**: `/api/status`

#### Query Parameters:
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `timeframe` | `string` | `"1d"` | Candle interval |
| `period` | `string` | `null` | Historical window |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/status?timeframe=1d&period=1y"
```

#### Example Response (200 OK):
```json
{
  "key": "1d|1y",
  "is_updating": false,
  "total_cached": 85,
  "last_updated": 1741804500.2
}
```

---

### 10. Export Screener Matrix to CSV
Downloads the full technical analysis tabular dataset as a standard CSV spreadsheet file.

- **Method**: `GET`
- **Path**: `/api/export`

#### Query Parameters:
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `sector` | `string` | `"All"` | Filter by sector |
| `timeframe` | `string` | `"1d"` | Candle interval |
| `period` | `string` | `null` | Historical lookback window |

#### Example Request:
```bash
curl -X GET "https://marketindex-new.vercel.app/api/export?sector=IT&timeframe=1d&period=1y" -o it_stocks.csv
```

---

## 🎯 100-Point Weighted Technical Scoring Model

Every stock is evaluated using a proprietary institutional multi-factor technical scoring algorithm totaling **100 points** across 5 distinct pillars:

| Pillar | Weight | Underlying Technical Indicators | Point Logic & Scoring Breakdown |
| :--- | :---: | :--- | :--- |
| **1. Trend Direction** | **30%** | SMA 200, SMA 50, EMA 20, EMA 50 | - CMP > 200 SMA: **10 pts** (Macro bull regime)<br>- CMP > 50 SMA: **7 pts** (Intermediate bull regime)<br>- EMA 20 > EMA 50: **7 pts** (Short-term bull momentum alignment)<br>- CMP > 20 EMA: **6 pts** (Active price leading moving averages) |
| **2. Trend Strength** | **15%** | Wilder's ADX (14) with +DI & -DI | - Strong Bullish (`+DI > -DI` & `ADX >= 25`): **15 pts**<br>- Developing Bullish (`+DI > -DI` & `ADX 20–25`): **11 pts**<br>- Low-volatility Consolidation (`ADX < 20`): **6–7 pts**<br>- Strong Bearish (`-DI > +DI` & `ADX >= 25`): **1 pt** |
| **3. Momentum** | **25%** | RSI (14) & MACD (12, 26, 9) | **RSI (13 pts max)**:<br>- Sweet spot `55 <= RSI <= 68`: **13 pts**<br>- Mild bull `50 <= RSI < 55`: **10 pts**<br>- Strong momentum `68 < RSI <= 75`: **9 pts**<br>- Overbought `RSI > 75`: **5 pts**<br>- Oversold `RSI < 30`: **2 pts**<br><br>**MACD (12 pts max)**:<br>- MACD line > Signal & > 0: **12 pts**<br>- Bullish cross below zero line: **9 pts**<br>- Bullish above zero but declining: **5 pts**<br>- Bearish line < Signal: **1 pt** |
| **4. Volume Flow** | **15%** | Volume Surge Ratio & On-Balance Volume (OBV) | **Volume Ratio (8 pts max)**:<br>- Green candle with volume surge `>= 1.5x`: **8 pts**<br>- Above-average volume `>= 1.0x`: **6 pts**<br>- Low-volume pullback (healthy consolidation): **5 pts**<br>- High-volume selloff: **1 pt**<br><br>**OBV Trend (7 pts max)**:<br>- Accumulation / Rising 20D slope: **7 pts**<br>- Neutral OBV slope: **4 pts**<br>- Distribution / Falling 20D slope: **1 pt** |
| **5. Price Structure** | **15%** | Floor Pivot Points & 52-Week Proximity | - CMP > Central Floor Pivot ($P$): **6 pts**<br>- Near support cushion (>= 1.5% from nearest support): **4 pts**<br>- 52-Week High proximity (Within 10% of 52W High: **5 pts**, 10–20%: **4 pts**, >35% drawdown: **0 pts**) |
| **Total** | **100%** | **Combined Technical Health Score** | **Max Score: 100 Points** |

### Score Classification & Rating Grades:
- **80 – 100**: 🟢 **Elite Bullish** (`score-elite`) — Maximum technical alignment across all indicators.
- **65 – 79**: 🟢 **Bullish** (`score-bullish`) — Solid uptrend with constructive momentum and volume backing.
- **45 – 64**: 🟡 **Neutral** (`score-neutral`) — Range-bound consolidation or mixed technical signals.
- **30 – 44**: 🟠 **Bearish** (`score-bearish`) — Corrective trend, trading below intermediate moving averages.
- **0 – 29**: 🔴 **Strong Sell** (`score-strong-sell`) — Breakdown across major moving averages with high-volume selling.

---

## 📊 Technical Analysis Methodology

### Moving Averages & Trend Verdicts
- **SMA 20, 50, 200**: Evaluates classic medium- and long-term trend baselines.
- **EMA 20, 50**: Detects rapid momentum shifts.
- **Trend Classification**:
  - `Strong Bullish`: `CMP > EMA20 > EMA50 > SMA200`
  - `Bullish`: `CMP > EMA20` and `CMP > SMA50`
  - `Neutral`: Price oscillating between 20 EMA and 50 SMA
  - `Bearish`: `CMP < EMA20` and `CMP < SMA50`
  - `Strong Bearish`: `CMP < EMA20 < EMA50 < SMA200`

### Wilder's ADX (Average Directional Index)
- Computed using 14-period Wilder smoothing on True Range, $+DM$, and $-DM$.
- Quantifies trend velocity independent of direction.

### Relative Strength Index (RSI 14)
- Smoothed using Wilder's exponential moving average ($alpha = 1/14$).
- Identifies oversold ($\le 30$), neutral ($30 - 55$), bullish expansion ($55 - 70$), and overbought ($\ge 70$) regimes.

### MACD (Moving Average Convergence Divergence)
- Fast EMA: 12 periods | Slow EMA: 26 periods | Signal Line: 9-period EMA of MACD line.
- Evaluates histogram delta to identify momentum accelerations and divergences.

### Average True Range (ATR 14) & ATR %
- $TR = \max(H - L, |H - C_{\text{prev}}|, |L - C_{\text{prev}}|)$
- $\text{ATR \%} = (\text{ATR} / \text{CMP}) \times 100$ (normalized volatility benchmark).

### Floor Pivot Points (Standard)
- $P = (H + L + C) / 3$
- $R_1 = (2 \times P) - L \quad|\quad S_1 = (2 \times P) - H$
- $R_2 = P + (H - L) \quad|\quad S_2 = P - (H - L)$
- $R_3 = H + 2 \times (P - L) \quad|\quad S_3 = L - 2 \times (H - P)$
- Dynamic calculation of the closest support/resistance level and percentage cushion to price.

---

## 🏢 Universe & Sector Taxonomy

The API analyzes 85+ prominent NSE constituents categorized into 7 sectors:

| Sector | Count | Sample Stocks (NSE Symbols) |
| :--- | :---: | :--- |
| **Finance & Banking** | 15 | `HDFCBANK.NS`, `ICICIBANK.NS`, `SBIN.NS`, `KOTAKBANK.NS`, `AXISBANK.NS`, `BAJFINANCE.NS`, `BAJAJFINSV.NS`, `CHOLAFIN.NS`, `HDFCLIFE.NS`, `SBILIFE.NS`, `PNB.NS`, `BANKBARODA.NS` |
| **FMCG** | 12 | `ITC.NS`, `HINDUNILVR.NS`, `NESTLEIND.NS`, `BRITANNIA.NS`, `TATACONSUM.NS`, `DABUR.NS`, `MARICO.NS`, `GODREJCP.NS`, `VBL.NS`, `COLPAL.NS`, `PGHH.NS`, `EMAMILTD.NS` |
| **IT** | 12 | `TCS.NS`, `INFY.NS`, `HCLTECH.NS`, `WIPRO.NS`, `TECHM.NS`, `LTIM.NS`, `PERSISTENT.NS`, `COFORGE.NS`, `MPHASIS.NS`, `OFSS.NS`, `KPITTECH.NS`, `TATAELXSI.NS` |
| **Automobile** | 12 | `TATAMOTORS.NS`, `M&M.NS`, `MARUTI.NS`, `BAJAJ-AUTO.NS`, `EICHERMOT.NS`, `HEROMOTOCO.NS`, `TVSMOTOR.NS`, `BHARATFORG.NS`, `ASHOKLEY.NS`, `BOSCHLTD.NS`, `MRF.NS` |
| **Healthcare & Pharma** | 12 | `SUNPHARMA.NS`, `CIPLA.NS`, `DRREDDY.NS`, `DIVISLAB.NS`, `APOLLOHOSP.NS`, `LUPIN.NS`, `AUROPHARMA.NS`, `TORNTPHARM.NS`, `MANKIND.NS`, `BIOCON.NS`, `MAXHEALTH.NS` |
| **Oil, Gas & Energy** | 12 | `RELIANCE.NS`, `ONGC.NS`, `NTPC.NS`, `POWERGRID.NS`, `BPCL.NS`, `IOC.NS`, `COALINDIA.NS`, `GAIL.NS`, `TATAPOWER.NS`, `ADANIGREEN.NS`, `ADANIPOWER.NS`, `OIL.NS` |
| **Metals & Infra** | 12 | `TATASTEEL.NS`, `JSWSTEEL.NS`, `HINDALCO.NS`, `VEDL.NS`, `LT.NS`, `ULTRACEMCO.NS`, `GRASIM.NS`, `ADANIENT.NS`, `AMBUJACEM.NS`, `JINDALSTEL.NS`, `SHREECEM.NS`, `NMDC.NS` |

---

## 💻 Quickstart Code Examples

### Python (`requests`)
```python
import requests

BASE_URL = "https://marketindex-new.vercel.app"

# 1. Fetch top IT stocks sorted by Technical Health Score
response = requests.get(f"{BASE_URL}/api/stocks", params={
    "sector": "IT",
    "timeframe": "1d",
    "period": "1y"
})
data = response.json()

for stock in data["data"][:5]:
    print(f"{stock['symbol']} | Score: {stock['technical_score']}/100 ({stock['technical_grade']}) | RSI: {stock['rsi']}")

# 2. Fetch single stock fundamentals
fund_resp = requests.get(f"{BASE_URL}/api/stock/TCS.NS/fundamentals")
fundamentals = fund_resp.json()
print("Market Cap:", fundamentals["valuation"]["market_cap_fmt"])
print("Consensus Target:", fundamentals["analyst_targets"]["target_mean"])
print("Potential Upside:", fundamentals["analyst_targets"]["potential_upside_pct"], "%")
```

### JavaScript / TypeScript (`fetch`)
```javascript
const BASE_URL = "https://marketindex-new.vercel.app";

async function getTopStocks() {
  const res = await fetch(`${BASE_URL}/api/stocks?sector=Finance%20%26%20Banking&timeframe=1d&period=6mo`);
  const { summary, data } = await res.json();
  
  console.log(`Total analyzed: ${summary.total_stocks} | Bullish: ${summary.bullish_count}`);
  
  data.forEach(stock => {
    console.log(`${stock.symbol} => CMP: ₹${stock.cmp} | Score: ${stock.technical_score}`);
  });
}

getTopStocks();
```

---

## 🛠️ Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/marketindexNew.git
   cd marketindexNew
   ```

2. **Create a virtual environment & install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run the local development server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Access locally**:
   - API Root: `http://127.0.0.1:8000`
   - Swagger Documentation: `http://127.0.0.1:8000/docs`

---

## ☁️ Vercel Deployment Guide

The repository includes pre-configured [`vercel.json`](./vercel.json) and [`api/index.py`](./api/index.py).

### Deploy with Vercel CLI:
```bash
npm i -g vercel
vercel --prod
```

### Deploy via GitHub:
1. Push code to your GitHub repository.
2. Go to [vercel.com/new](https://vercel.com/new).
3. Import the repository and click **Deploy**.
4. Vercel automatically detects `vercel.json`, builds with `@vercel/python`, and installs `requirements.txt`.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
