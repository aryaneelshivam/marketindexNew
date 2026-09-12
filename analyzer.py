"""
Technical Analysis Engine for Stock Screener.
Calculates:
- Trend Direction (SMA 20, 50, 200; EMA 20, 50; Trend Summary)
- Trend Strength (ADX 14, +DI, -DI)
- Momentum (RSI 14, MACD 12/26/9)
- Volatility (ATR 14, ATR %)
- Volume & Liquidity (OBV, 20D Avg Vol, Volume Ratio)
- Price Structure / Support & Resistance (Pivot Points, R1-R3, S1-S3, Nearest S/R, 52W Range)
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

def calculate_technical_indicators(df: pd.DataFrame, symbol: str, info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Computes all requested technical indicators for a given stock DataFrame.
    Expected columns: ['Open', 'High', 'Low', 'Close', 'Volume'].
    """
    if df is None or len(df) < 20:
        return None

    # Clean and flatten columns if multi-indexed
    if isinstance(df.columns, pd.MultiIndex):
        df = df.xs(symbol, axis=1, level=1) if symbol in df.columns.levels[1] else df.droplevel(1, axis=1)

    # Ensure required columns exist and are numeric
    req_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for c in req_cols:
        if c not in df.columns:
            return None
        df[c] = pd.to_numeric(df[c], errors='coerce')

    df = df.dropna(subset=['Close', 'High', 'Low']).copy()
    if len(df) < 20:
        return None

    close = df['Close']
    high = df['High']
    low = df['Low']
    open_p = df['Open']
    volume = df['Volume']

    cmp = float(close.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) >= 2 else cmp
    change = cmp - prev_close
    pct_change = (change / prev_close) * 100 if prev_close != 0 else 0.0

    # 1. TREND DIRECTION (SMA & EMA)
    sma20 = float(close.rolling(window=20).mean().iloc[-1]) if len(close) >= 20 else None
    sma50 = float(close.rolling(window=50).mean().iloc[-1]) if len(close) >= 50 else None
    sma200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else None

    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1]) if len(close) >= 20 else None
    ema50 = float(close.ewm(span=50, adjust=False).mean().iloc[-1]) if len(close) >= 50 else None

    # Determine Trend Direction Verdict
    trend_score = 0
    if ema20 is not None:
        trend_score += 1 if cmp > ema20 else -1
    if ema50 is not None:
        trend_score += 1 if cmp > ema50 else -1
    if sma50 is not None:
        trend_score += 1 if cmp > sma50 else -1
    if sma200 is not None:
        trend_score += 2 if cmp > sma200 else -2
    if ema20 is not None and ema50 is not None:
        trend_score += 1 if ema20 > ema50 else -1

    if trend_score >= 4:
        trend_verdict = "Strong Bullish"
        trend_color = "success"
    elif trend_score >= 1:
        trend_verdict = "Bullish"
        trend_color = "info"
    elif trend_score <= -4:
        trend_verdict = "Strong Bearish"
        trend_color = "danger"
    elif trend_score <= -1:
        trend_verdict = "Bearish"
        trend_color = "warning"
    else:
        trend_verdict = "Neutral"
        trend_color = "secondary"

    # 2. TREND STRENGTH (ADX 14, +DI, -DI)
    adx_val, plus_di, minus_di, adx_label = calculate_adx(high, low, close, period=14)

    # 3. MOMENTUM (RSI 14 & MACD)
    rsi14 = calculate_rsi(close, period=14)
    if rsi14 is not None:
        if rsi14 >= 70:
            rsi_status = "Overbought"
        elif rsi14 <= 30:
            rsi_status = "Oversold"
        elif rsi14 >= 55:
            rsi_status = "Bullish Momentum"
        elif rsi14 <= 45:
            rsi_status = "Bearish Momentum"
        else:
            rsi_status = "Neutral"
    else:
        rsi_status = "N/A"

    macd_line, macd_signal, macd_hist, macd_status = calculate_macd(close)

    # 4. VOLATILITY (ATR 14, ATR %)
    atr14, atr_pct = calculate_atr(high, low, close, period=14)

    # 5. VOLUME & LIQUIDITY (OBV, 20D Avg Vol, Volume Ratio)
    curr_volume = int(volume.iloc[-1]) if not pd.isna(volume.iloc[-1]) else 0
    vol20 = float(volume.rolling(window=20).mean().iloc[-1]) if len(volume) >= 20 else float(curr_volume)
    vol_ratio = (curr_volume / vol20) if vol20 > 0 else 1.0

    if vol_ratio >= 2.0:
        vol_verdict = "Massive Spike"
    elif vol_ratio >= 1.3:
        vol_verdict = "Above Average"
    elif vol_ratio <= 0.7:
        vol_verdict = "Low Volume"
    else:
        vol_verdict = "Normal"

    obv_val, obv_trend = calculate_obv(close, volume)

    # 6. PRICE STRUCTURE & SUPPORT / RESISTANCE (Pivot Points)
    # Using previous session's HLC for standard floor pivots
    p_high = float(high.iloc[-2]) if len(high) >= 2 else float(high.iloc[-1])
    p_low = float(low.iloc[-2]) if len(low) >= 2 else float(low.iloc[-1])
    p_close = float(close.iloc[-2]) if len(close) >= 2 else float(close.iloc[-1])

    pivot = (p_high + p_low + p_close) / 3.0
    r1 = (2 * pivot) - p_low
    s1 = (2 * pivot) - p_high
    r2 = pivot + (p_high - p_low)
    s2 = pivot - (p_high - p_low)
    r3 = p_high + 2 * (pivot - p_low)
    s3 = p_low - 2 * (p_high - pivot)

    # Find nearest Support & Resistance relative to CMP
    sr_levels = [
        ("S3", s3), ("S2", s2), ("S1", s1),
        ("Pivot", pivot),
        ("R1", r1), ("R2", r2), ("R3", r3)
    ]
    supports = [lvl for lvl in sr_levels if lvl[1] < cmp]
    resistances = [lvl for lvl in sr_levels if lvl[1] > cmp]

    nearest_support = max(supports, key=lambda x: x[1]) if supports else ("S3", s3)
    nearest_resistance = min(resistances, key=lambda x: x[1]) if resistances else ("R3", r3)

    sup_dist_pct = ((cmp - nearest_support[1]) / cmp) * 100 if cmp > 0 else 0
    res_dist_pct = ((nearest_resistance[1] - cmp) / cmp) * 100 if cmp > 0 else 0

    # 52-Week High & Low
    high_52w = float(high.tail(252).max()) if len(high) >= 252 else float(high.max())
    low_52w = float(low.tail(252).min()) if len(low) >= 252 else float(low.min())
    pct_from_52w_high = ((cmp - high_52w) / high_52w) * 100 if high_52w > 0 else 0
    pct_from_52w_low = ((cmp - low_52w) / low_52w) * 100 if low_52w > 0 else 0

    # Compute Weighted Composite Technical Score (out of 100)
    score_data = calculate_technical_score(
        cmp=cmp,
        sma200=sma200,
        sma50=sma50,
        ema50=ema50,
        ema20=ema20,
        adx_val=adx_val,
        plus_di=plus_di,
        minus_di=minus_di,
        rsi=rsi14,
        macd=macd_line,
        macd_signal=macd_signal,
        pct_change=pct_change,
        vol_ratio=vol_ratio,
        obv_trend=obv_trend,
        pivot=pivot,
        pct_from_52w_high=pct_from_52w_high
    )

    return {
        "symbol": symbol,
        "name": (info.get("name") if info else symbol.split(".")[0]),
        "sector": (info.get("sector") if info else "General"),
        "exchange": (info.get("exchange") if info else "NSE"),
        "cmp": round(cmp, 2),
        "change": round(change, 2),
        "pct_change": round(pct_change, 2),
        # Weighted Technical Composite Score (0 - 100)
        "technical_score": score_data["score"],
        "technical_grade": score_data["grade"],
        "grade_badge": score_data["grade_badge"],
        "score_breakdown": score_data["breakdown"],
        # Trend
        "sma20": round(sma20, 2) if sma20 is not None else None,
        "sma50": round(sma50, 2) if sma50 is not None else None,
        "sma200": round(sma200, 2) if sma200 is not None else None,
        "ema20": round(ema20, 2) if ema20 is not None else None,
        "ema50": round(ema50, 2) if ema50 is not None else None,
        "trend_verdict": trend_verdict,
        "trend_color": trend_color,
        # Trend Strength (ADX)
        "adx": round(adx_val, 1) if adx_val is not None else None,
        "plus_di": round(plus_di, 1) if plus_di is not None else None,
        "minus_di": round(minus_di, 1) if minus_di is not None else None,
        "adx_label": adx_label,
        # Momentum (RSI & MACD)
        "rsi": round(rsi14, 1) if rsi14 is not None else None,
        "rsi_status": rsi_status,
        "macd": round(macd_line, 2) if macd_line is not None else None,
        "macd_signal": round(macd_signal, 2) if macd_signal is not None else None,
        "macd_hist": round(macd_hist, 2) if macd_hist is not None else None,
        "macd_status": macd_status,
        # Volatility (ATR)
        "atr": round(atr14, 2) if atr14 is not None else None,
        "atr_pct": round(atr_pct, 2) if atr_pct is not None else None,
        # Volume & Liquidity
        "volume": curr_volume,
        "volume_20d_avg": int(vol20),
        "vol_ratio": round(vol_ratio, 2),
        "vol_verdict": vol_verdict,
        "obv": int(obv_val) if obv_val is not None else None,
        "obv_trend": obv_trend,
        # Price Structure / S&R
        "pivot": round(pivot, 2),
        "r1": round(r1, 2),
        "s1": round(s1, 2),
        "r2": round(r2, 2),
        "s2": round(s2, 2),
        "r3": round(r3, 2),
        "s3": round(s3, 2),
        "nearest_support": f"{nearest_support[0]} ({round(nearest_support[1], 1)})",
        "support_dist_pct": round(sup_dist_pct, 1),
        "nearest_resistance": f"{nearest_resistance[0]} ({round(nearest_resistance[1], 1)})",
        "resistance_dist_pct": round(res_dist_pct, 1),
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "pct_from_52w_high": round(pct_from_52w_high, 1),
        "pct_from_52w_low": round(pct_from_52w_low, 1),
    }


def calculate_technical_score(
    cmp: float,
    sma200: Optional[float],
    sma50: Optional[float],
    ema50: Optional[float],
    ema20: Optional[float],
    adx_val: Optional[float],
    plus_di: Optional[float],
    minus_di: Optional[float],
    rsi: Optional[float],
    macd: Optional[float],
    macd_signal: Optional[float],
    pct_change: float,
    vol_ratio: float,
    obv_trend: str,
    pivot: float,
    pct_from_52w_high: float
) -> Dict[str, Any]:
    """
    Weighted Composite Technical Scoring Model (0 - 100 Points):
    1. Trend Direction (Weight: 30%)
       - Price vs 200 SMA (Long term): 10 pts
       - Price vs 50 SMA (Medium term): 7 pts
       - EMA 20 vs EMA 50 (Cross/momentum): 7 pts
       - Price vs 20 EMA (Short term): 6 pts
    2. Trend Strength - ADX & Directional Movement (Weight: 15%)
       - +DI > -DI and ADX >= 25: 15 pts
       - +DI > -DI and 20 <= ADX < 25: 11 pts
       - +DI > -DI and ADX < 20: 7 pts
       - -DI > +DI and ADX < 20: 6 pts
       - -DI > +DI and 20 <= ADX < 25: 3 pts
       - -DI > +DI and ADX >= 25: 1 pt
    3. Momentum - RSI & MACD (Weight: 25%)
       - RSI (13 pts): Optimal bull zone (55-68) = 13 pts; (50-55) = 10 pts; (68-75) = 9 pts; (40-50) = 6 pts; Overbought (>75) = 5 pts; (30-40) = 3 pts; Oversold (<30) = 2 pts
       - MACD (12 pts): Bullish line above signal & above 0 = 12 pts; Bullish crossover below 0 = 9 pts; Pullback in uptrend = 5 pts; Bearish = 1 pt
    4. Volume & Liquidity Flow (Weight: 15%)
       - Volume surge on green candle / low volume on pullback: 8 pts
       - OBV Accumulation / Rising: 7 pts
    5. Price Structure & Support / Resistance (Weight: 15%)
       - Price above Central Pivot: 6 pts
       - Support cushion: 4 pts
       - 52-Week High Proximity (Relative Strength): 5 pts
    """
    # 1. Trend Direction (Max: 30)
    trend_pts = 0
    if sma200 and cmp > sma200:
        trend_pts += 10
    if sma50 and cmp > sma50:
        trend_pts += 7
    if ema20 and ema50 and ema20 > ema50:
        trend_pts += 7
    if ema20 and cmp > ema20:
        trend_pts += 6

    # 2. Trend Strength (Max: 15)
    strength_pts = 0
    if plus_di is not None and minus_di is not None and adx_val is not None:
        if plus_di >= minus_di:
            if adx_val >= 25:
                strength_pts = 15
            elif adx_val >= 20:
                strength_pts = 11
            else:
                strength_pts = 7
        else:
            if adx_val >= 25:
                strength_pts = 1
            elif adx_val >= 20:
                strength_pts = 3
            else:
                strength_pts = 6
    else:
        strength_pts = 7

    # 3. Momentum (Max: 25)
    rsi_pts = 0
    if rsi is not None:
        if 55 <= rsi <= 68:
            rsi_pts = 13
        elif 50 <= rsi < 55:
            rsi_pts = 10
        elif 68 < rsi <= 75:
            rsi_pts = 9
        elif 40 <= rsi < 50:
            rsi_pts = 6
        elif rsi > 75:
            rsi_pts = 5
        elif 30 <= rsi < 40:
            rsi_pts = 3
        else:
            rsi_pts = 2
    else:
        rsi_pts = 6

    macd_pts = 0
    if macd is not None and macd_signal is not None:
        if macd > macd_signal and macd >= 0:
            macd_pts = 12
        elif macd > macd_signal and macd < 0:
            macd_pts = 9
        elif macd <= macd_signal and macd >= 0:
            macd_pts = 5
        else:
            macd_pts = 1
    else:
        macd_pts = 6
    momentum_pts = rsi_pts + macd_pts

    # 4. Volume & Liquidity (Max: 15)
    vol_pts = 0
    if pct_change >= 0:
        if vol_ratio >= 1.5:
            vol_pts = 8
        elif vol_ratio >= 1.0:
            vol_pts = 6
        else:
            vol_pts = 4
    else:
        if vol_ratio < 1.0:
            vol_pts = 5
        elif vol_ratio < 1.5:
            vol_pts = 3
        else:
            vol_pts = 1

    obv_pts = 0
    if "Rising" in obv_trend or "Accumulation" in obv_trend:
        obv_pts = 7
    elif "Falling" in obv_trend or "Distribution" in obv_trend:
        obv_pts = 1
    else:
        obv_pts = 4
    volume_pts = vol_pts + obv_pts

    # 5. Price Structure (Max: 15)
    pivot_pts = 6 if cmp >= pivot else 1
    sup_room_pts = 4 if cmp >= pivot else 2

    range_pts = 0
    if pct_from_52w_high >= -10:
        range_pts = 5
    elif pct_from_52w_high >= -20:
        range_pts = 4
    elif pct_from_52w_high >= -35:
        range_pts = 2
    else:
        range_pts = 0
    structure_pts = pivot_pts + sup_room_pts + range_pts

    total_score = round(trend_pts + strength_pts + momentum_pts + volume_pts + structure_pts, 1)

    if total_score >= 80:
        grade = "Elite Bullish"
        grade_badge = "grade-elite"
    elif total_score >= 65:
        grade = "Bullish"
        grade_badge = "grade-bullish"
    elif total_score >= 45:
        grade = "Neutral"
        grade_badge = "grade-neutral"
    elif total_score >= 30:
        grade = "Bearish"
        grade_badge = "grade-bearish"
    else:
        grade = "Strong Sell"
        grade_badge = "grade-strong-sell"

    return {
        "score": total_score,
        "grade": grade,
        "grade_badge": grade_badge,
        "breakdown": {
            "trend": {"score": trend_pts, "max": 30, "weight": "30%"},
            "strength": {"score": strength_pts, "max": 15, "weight": "15%"},
            "momentum": {"score": momentum_pts, "max": 25, "weight": "25%"},
            "volume": {"score": volume_pts, "max": 15, "weight": "15%"},
            "structure": {"score": structure_pts, "max": 15, "weight": "15%"}
        }
    }


def calculate_rsi(series: pd.Series, period: int = 14) -> Optional[float]:
    """Calculates Wilder's RSI."""
    if len(series) < period + 1:
        return None
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    last_val = rsi.iloc[-1]
    return float(last_val) if not pd.isna(last_val) else None


def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """Calculates MACD, Signal, Histogram and crossover verdict."""
    if len(series) < slow + signal:
        return None, None, None, "N/A"

    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line

    curr_hist = float(hist.iloc[-1])
    prev_hist = float(hist.iloc[-2]) if len(hist) >= 2 else curr_hist
    curr_macd = float(macd_line.iloc[-1])
    curr_sig = float(signal_line.iloc[-1])

    if prev_hist < 0 and curr_hist > 0:
        status = "Bullish Crossover 🟢"
    elif prev_hist > 0 and curr_hist < 0:
        status = "Bearish Crossover 🔴"
    elif curr_hist > 0:
        status = "Bullish"
    else:
        status = "Bearish"

    return curr_macd, curr_sig, curr_hist, status


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """Calculates Average True Range (ATR) and ATR as % of Close."""
    if len(close) < period + 1:
        return None, None

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean().iloc[-1]
    cmp = close.iloc[-1]
    atr_pct = (atr / cmp) * 100 if cmp > 0 else 0.0

    return float(atr), float(atr_pct)


def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
    """Calculates Average Directional Index (ADX), +DI, and -DI."""
    if len(close) < period * 2:
        return None, None, None, "Insufficient Data"

    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    tr_smoothed = pd.Series(tr).ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    plus_dm_smoothed = pd.Series(plus_dm, index=high.index).ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    minus_dm_smoothed = pd.Series(minus_dm, index=high.index).ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    plus_di = (plus_dm_smoothed / tr_smoothed.replace(0, np.nan)) * 100
    minus_di = (minus_dm_smoothed / tr_smoothed.replace(0, np.nan)) * 100

    dx = ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)) * 100
    adx = dx.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    adx_val = float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else None
    p_di = float(plus_di.iloc[-1]) if not pd.isna(plus_di.iloc[-1]) else None
    m_di = float(minus_di.iloc[-1]) if not pd.isna(minus_di.iloc[-1]) else None

    if adx_val is None:
        label = "N/A"
    elif adx_val >= 25:
        dir_str = "Bullish" if (p_di and m_di and p_di > m_di) else "Bearish"
        label = f"Strong {dir_str}"
    elif adx_val >= 20:
        label = "Developing Trend"
    else:
        label = "Weak / Ranging"

    return adx_val, p_di, m_di, label


def calculate_obv(close: pd.Series, volume: pd.Series):
    """Calculates On-Balance Volume and its 20-period slope/trend."""
    if len(close) < 5:
        return None, "N/A"

    direction = np.sign(close.diff()).fillna(0)
    obv = (direction * volume).cumsum()
    obv_curr = float(obv.iloc[-1])

    if len(obv) >= 20:
        obv_sma20 = obv.rolling(20).mean().iloc[-1]
        obv_prev5 = obv.iloc[-5]
        if obv_curr > obv_sma20 and obv_curr > obv_prev5:
            trend = "Accumulation / Rising 📈"
        elif obv_curr < obv_sma20 and obv_curr < obv_prev5:
            trend = "Distribution / Falling 📉"
        else:
            trend = "Neutral ⚖️"
    else:
        trend = "Neutral"

    return obv_curr, trend
