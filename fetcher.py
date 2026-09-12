"""
Data Fetcher and In-Memory Cache for Stock Data with Multi-Timeframe + Custom Period Support.

Supports:
- Candle Intervals: 15m, 1h, 1d, 1wk, 1mo
- Historical Windows: 1mo, 3mo, 6mo, 1y, 2y, 5y (overrides default period per timeframe)
"""

import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
import yfinance as yf
import pandas as pd

from sectors import SECTOR_STOCKS, get_all_tickers, get_sector_map
from analyzer import calculate_technical_indicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("marketindex.fetcher")

# Default configs for each candle interval (period = fallback if no user override)
TIMEFRAME_CONFIG: Dict[str, Dict[str, str]] = {
    "15m": {"period": "5d",  "interval": "15m", "label": "15m Intraday"},
    "1h":  {"period": "1mo", "interval": "1h",  "label": "1 Hour"},
    "1d":  {"period": "1y",  "interval": "1d",  "label": "Daily (1D)"},
    "1wk": {"period": "2y",  "interval": "1wk", "label": "Weekly (1W)"},
    "1mo": {"period": "5y",  "interval": "1mo", "label": "Monthly (1M)"},
}

# Valid historical window choices exposed to the user
VALID_PERIODS = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}

# Minimum candles required before we accept a series as usable
MIN_CANDLES = 15


def _cache_key(timeframe: str, period: str) -> str:
    """Composite cache key: e.g. '1d|1y', '1d|6mo'."""
    return f"{timeframe}|{period}"


class MarketDataCache:
    def __init__(self, ttl_seconds: int = 900):
        self.ttl_seconds = ttl_seconds
        # Keys are composite: "<interval>|<period>" e.g. "1d|1y", "1d|6mo"
        self.cached_results: Dict[str, List[Dict[str, Any]]] = {}
        self.last_updated:   Dict[str, float] = {}
        self.is_updating:    Dict[str, bool]  = {}
        self.sector_map = get_sector_map()

    def _resolve(self, timeframe: str, period: Optional[str]) -> Tuple[str, str, str]:
        """Returns (tf, resolved_period, cache_key) after validating/normalising inputs."""
        tf = timeframe if timeframe in TIMEFRAME_CONFIG else "1d"
        default_period = TIMEFRAME_CONFIG[tf]["period"]
        resolved_period = period if (period and period in VALID_PERIODS) else default_period
        key = _cache_key(tf, resolved_period)
        return tf, resolved_period, key

    def is_stale(self, timeframe: str = "1d", period: Optional[str] = None) -> bool:
        _, _, key = self._resolve(timeframe, period)
        last_t = self.last_updated.get(key, 0)
        cache_len = len(self.cached_results.get(key, []))
        return (time.time() - last_t) > self.ttl_seconds or cache_len == 0

    def get_data(
        self,
        sector_filter: Optional[str] = None,
        timeframe: str = "1d",
        period: Optional[str] = None,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """Returns cached stock analysis for the given timeframe + period combo."""
        tf, resolved_period, key = self._resolve(timeframe, period)

        if (self.is_stale(tf, resolved_period) or force_refresh) and not self.is_updating.get(key, False):
            self.refresh_sync(timeframe=tf, period=resolved_period)

        data = self.cached_results.get(key, [])
        if not sector_filter or sector_filter == "All":
            return data
        return [item for item in data if item.get("sector") == sector_filter]

    def refresh_sync(self, timeframe: str = "1d", period: Optional[str] = None):
        """Fetches all tickers and calculates indicators concurrently."""
        tf, resolved_period, key = self._resolve(timeframe, period)
        interval = TIMEFRAME_CONFIG[tf]["interval"]

        self.is_updating[key] = True
        logger.info(
            f"Starting market refresh — interval={interval}, period={resolved_period} "
            f"(key={key})..."
        )
        start_time = time.time()
        tickers = get_all_tickers()
        results: List[Dict[str, Any]] = []

        def fetch_worker(symbol: str):
            try:
                ticker_obj = yf.Ticker(symbol)
                hist = ticker_obj.history(
                    period=resolved_period,
                    interval=interval,
                    auto_adjust=False
                )
                if hist is None or hist.empty or len(hist) < MIN_CANDLES:
                    return None

                info = self.sector_map.get(symbol, {"name": symbol, "sector": "General", "exchange": "NSE"})
                analysis = calculate_technical_indicators(hist, symbol, info)
                if analysis:
                    analysis["timeframe"] = tf
                    analysis["period"]    = resolved_period
                return analysis
            except Exception as e:
                logger.warning(f"Error analyzing {symbol} [{tf}/{resolved_period}]: {e}")
                return None

        with ThreadPoolExecutor(max_workers=16) as executor:
            future_to_symbol = {executor.submit(fetch_worker, sym): sym for sym in tickers}
            for future in as_completed(future_to_symbol):
                res = future.result()
                if res:
                    results.append(res)

        # Sort by technical score (highest first), then pct_change
        results.sort(key=lambda x: (-x.get("technical_score", 0), -x.get("pct_change", 0)))

        self.cached_results[key] = results
        self.last_updated[key]   = time.time()
        self.is_updating[key]    = False
        logger.info(
            f"Refreshed [{key}] {len(results)}/{len(tickers)} stocks "
            f"in {time.time() - start_time:.2f}s"
        )

    def refresh_all_sync(self):
        """Default refresh at startup — uses daily interval, 1-year window."""
        self.refresh_sync(timeframe="1d", period="1y")

    def get_single_stock(
        self,
        symbol: str,
        timeframe: str = "1d",
        period: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves detailed technical data + full OHLCV + indicator series for charting.
        If the symbol isn't cached yet, fetches it live.
        """
        tf, resolved_period, key = self._resolve(timeframe, period)
        interval = TIMEFRAME_CONFIG[tf]["interval"]

        # Try to find cached analysis first
        cached_item = None
        for item in self.cached_results.get(key, []):
            if item["symbol"] == symbol:
                cached_item = item
                break

        try:
            ticker_obj = yf.Ticker(symbol)
            hist = ticker_obj.history(
                period=resolved_period,
                interval=interval,
                auto_adjust=False
            )
            if hist is None or hist.empty:
                return cached_item  # fallback to cached summary without chart data

            # --- Build OHLCV candles ---
            is_intraday = "m" in tf or "h" in tf
            candles = []
            for idx, row in hist.iterrows():
                date_str = idx.strftime("%Y-%m-%d %H:%M") if is_intraday else idx.strftime("%Y-%m-%d")
                candles.append({
                    "date":   date_str,
                    "open":   round(float(row["Open"]),  2),
                    "high":   round(float(row["High"]),  2),
                    "low":    round(float(row["Low"]),   2),
                    "close":  round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
                })

            # --- Compute indicator series for charting ---
            close  = hist["Close"].astype(float)
            volume = hist["Volume"].astype(float)

            def _series(s: pd.Series) -> list:
                """Convert a pandas series to a rounded list, NaN → None."""
                return [round(v, 4) if pd.notna(v) else None for v in s]

            # Moving average overlays
            ema20_s  = close.ewm(span=20,  adjust=False).mean()
            ema50_s  = close.ewm(span=50,  adjust=False).mean()
            sma200_s = close.rolling(window=200).mean()
            sma50_s  = close.rolling(window=50).mean()

            # RSI (14)
            delta     = close.diff()
            gain      = delta.clip(lower=0)
            loss      = (-delta).clip(lower=0)
            avg_gain  = gain.ewm(alpha=1/14, adjust=False).mean()
            avg_loss  = loss.ewm(alpha=1/14, adjust=False).mean()
            rs        = avg_gain / avg_loss.replace(0, float('nan'))
            rsi_s     = 100 - (100 / (1 + rs))

            # MACD (12/26/9)
            exp12      = close.ewm(span=12, adjust=False).mean()
            exp26      = close.ewm(span=26, adjust=False).mean()
            macd_line  = exp12 - exp26
            macd_sig_s = macd_line.ewm(span=9, adjust=False).mean()
            macd_hist_s = macd_line - macd_sig_s

            # Volume 20-period moving average
            vol_avg_s = volume.rolling(window=20).mean()

            chart_data = {
                "dates":      [c["date"] for c in candles],
                "ema20":      _series(ema20_s),
                "ema50":      _series(ema50_s),
                "sma50":      _series(sma50_s),
                "sma200":     _series(sma200_s),
                "rsi":        _series(rsi_s),
                "macd_line":  _series(macd_line),
                "macd_signal":_series(macd_sig_s),
                "macd_hist":  _series(macd_hist_s),
                "volume":     [int(v) if pd.notna(v) else 0 for v in volume],
                "vol_avg":    _series(vol_avg_s),
            }

            res = dict(cached_item) if cached_item else {
                "symbol": symbol,
                "name":   self.sector_map.get(symbol, {}).get("name", symbol),
                "sector": self.sector_map.get(symbol, {}).get("sector", "General"),
                "timeframe": tf,
                "period": resolved_period,
            }
            res["candles"]    = candles
            res["chart_data"] = chart_data
            return res

        except Exception as e:
            logger.warning(f"Error fetching single stock chart data for {symbol}: {e}")
            return cached_item


    def cache_status(self, timeframe: str = "1d", period: Optional[str] = None) -> Dict[str, Any]:
        """Returns cache metadata for a given timeframe+period combo."""
        _, _, key = self._resolve(timeframe, period)
        return {
            "key":          key,
            "is_updating":  self.is_updating.get(key, False),
            "total_cached": len(self.cached_results.get(key, [])),
            "last_updated": self.last_updated.get(key, 0),
        }


# Global Singleton Cache Instance
market_cache = MarketDataCache(ttl_seconds=900)
