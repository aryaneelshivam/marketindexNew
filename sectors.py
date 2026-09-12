"""
Sector definitions and massive ticker lists for technical analysis.
Categorized into:
- Finance and Banking
- FMCG
- IT
- Automobile
- Healthcare Pharma
- Oil gas and energy
- Metals and Infra
"""

from typing import Dict, List, TypedDict

class StockInfo(TypedDict):
    symbol: str
    name: str
    exchange: str

SECTOR_STOCKS: Dict[str, List[StockInfo]] = {
    "Finance & Banking": [
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "exchange": "NSE"},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "exchange": "NSE"},
        {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
        {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "exchange": "NSE"},
        {"symbol": "AXISBANK.NS", "name": "Axis Bank", "exchange": "NSE"},
        {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance", "exchange": "NSE"},
        {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv", "exchange": "NSE"},
        {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "exchange": "NSE"},
        {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "exchange": "NSE"},
        {"symbol": "PNB.NS", "name": "Punjab National Bank", "exchange": "NSE"},
        {"symbol": "CHOLAFIN.NS", "name": "Cholamandalam Inv & Fin", "exchange": "NSE"},
        {"symbol": "HDFCLIFE.NS", "name": "HDFC Life Insurance", "exchange": "NSE"},
        {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance", "exchange": "NSE"},
        {"symbol": "MUTHOOTFIN.NS", "name": "Muthoot Finance", "exchange": "NSE"},
        {"symbol": "SHRIRAMFIN.NS", "name": "Shriram Finance", "exchange": "NSE"},
    ],
    "FMCG": [
        {"symbol": "ITC.NS", "name": "ITC Ltd", "exchange": "NSE"},
        {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "exchange": "NSE"},
        {"symbol": "NESTLEIND.NS", "name": "Nestle India", "exchange": "NSE"},
        {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "exchange": "NSE"},
        {"symbol": "TATACONSUM.NS", "name": "Tata Consumer Products", "exchange": "NSE"},
        {"symbol": "DABUR.NS", "name": "Dabur India", "exchange": "NSE"},
        {"symbol": "MARICO.NS", "name": "Marico Ltd", "exchange": "NSE"},
        {"symbol": "GODREJCP.NS", "name": "Godrej Consumer Products", "exchange": "NSE"},
        {"symbol": "VBL.NS", "name": "Varun Beverages", "exchange": "NSE"},
        {"symbol": "COLPAL.NS", "name": "Colgate-Palmolive India", "exchange": "NSE"},
        {"symbol": "PGHH.NS", "name": "Procter & Gamble Hygiene", "exchange": "NSE"},
        {"symbol": "EMAMILTD.NS", "name": "Emami Ltd", "exchange": "NSE"},
    ],
    "IT": [
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "exchange": "NSE"},
        {"symbol": "INFY.NS", "name": "Infosys", "exchange": "NSE"},
        {"symbol": "HCLTECH.NS", "name": "HCL Technologies", "exchange": "NSE"},
        {"symbol": "WIPRO.NS", "name": "Wipro", "exchange": "NSE"},
        {"symbol": "TECHM.NS", "name": "Tech Mahindra", "exchange": "NSE"},
        {"symbol": "LTIM.NS", "name": "LTIMindtree", "exchange": "NSE"},
        {"symbol": "PERSISTENT.NS", "name": "Persistent Systems", "exchange": "NSE"},
        {"symbol": "COFORGE.NS", "name": "Coforge", "exchange": "NSE"},
        {"symbol": "MPHASIS.NS", "name": "Mphasis", "exchange": "NSE"},
        {"symbol": "OFSS.NS", "name": "Oracle Financial Services", "exchange": "NSE"},
        {"symbol": "KPITTECH.NS", "name": "KPIT Technologies", "exchange": "NSE"},
        {"symbol": "TATAELXSI.NS", "name": "Tata Elxsi", "exchange": "NSE"},
    ],
    "Automobile": [
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "exchange": "NSE"},
        {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "exchange": "NSE"},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "exchange": "NSE"},
        {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "exchange": "NSE"},
        {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "exchange": "NSE"},
        {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp", "exchange": "NSE"},
        {"symbol": "TVSMOTOR.NS", "name": "TVS Motor Company", "exchange": "NSE"},
        {"symbol": "BHARATFORG.NS", "name": "Bharat Forge", "exchange": "NSE"},
        {"symbol": "ASHOKLEY.NS", "name": "Ashok Leyland", "exchange": "NSE"},
        {"symbol": "BOSCHLTD.NS", "name": "Bosch Ltd", "exchange": "NSE"},
        {"symbol": "TIINDIA.NS", "name": "Tube Investments of India", "exchange": "NSE"},
        {"symbol": "MRF.NS", "name": "MRF Ltd", "exchange": "NSE"},
    ],
    "Healthcare & Pharma": [
        {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma Industries", "exchange": "NSE"},
        {"symbol": "CIPLA.NS", "name": "Cipla", "exchange": "NSE"},
        {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Laboratories", "exchange": "NSE"},
        {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "exchange": "NSE"},
        {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "exchange": "NSE"},
        {"symbol": "LUPIN.NS", "name": "Lupin", "exchange": "NSE"},
        {"symbol": "AUROPHARMA.NS", "name": "Aurobindo Pharma", "exchange": "NSE"},
        {"symbol": "TORNTPHARM.NS", "name": "Torrent Pharmaceuticals", "exchange": "NSE"},
        {"symbol": "MANKIND.NS", "name": "Mankind Pharma", "exchange": "NSE"},
        {"symbol": "BIOCON.NS", "name": "Biocon", "exchange": "NSE"},
        {"symbol": "MAXHEALTH.NS", "name": "Max Healthcare Institute", "exchange": "NSE"},
        {"symbol": "ZYDUSLIFE.NS", "name": "Zydus Lifesciences", "exchange": "NSE"},
    ],
    "Oil, Gas & Energy": [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "exchange": "NSE"},
        {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "exchange": "NSE"},
        {"symbol": "NTPC.NS", "name": "NTPC Ltd", "exchange": "NSE"},
        {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "exchange": "NSE"},
        {"symbol": "BPCL.NS", "name": "Bharat Petroleum", "exchange": "NSE"},
        {"symbol": "IOC.NS", "name": "Indian Oil Corp", "exchange": "NSE"},
        {"symbol": "COALINDIA.NS", "name": "Coal India", "exchange": "NSE"},
        {"symbol": "GAIL.NS", "name": "GAIL India", "exchange": "NSE"},
        {"symbol": "TATAPOWER.NS", "name": "Tata Power", "exchange": "NSE"},
        {"symbol": "ADANIGREEN.NS", "name": "Adani Green Energy", "exchange": "NSE"},
        {"symbol": "ADANIPOWER.NS", "name": "Adani Power", "exchange": "NSE"},
        {"symbol": "OIL.NS", "name": "Oil India", "exchange": "NSE"},
    ],
    "Metals & Infra": [
        {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "exchange": "NSE"},
        {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "exchange": "NSE"},
        {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "exchange": "NSE"},
        {"symbol": "VEDL.NS", "name": "Vedanta Ltd", "exchange": "NSE"},
        {"symbol": "LT.NS", "name": "Larsen & Toubro", "exchange": "NSE"},
        {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "exchange": "NSE"},
        {"symbol": "GRASIM.NS", "name": "Grasim Industries", "exchange": "NSE"},
        {"symbol": "ADANIENT.NS", "name": "Adani Enterprises", "exchange": "NSE"},
        {"symbol": "AMBUJACEM.NS", "name": "Ambuja Cements", "exchange": "NSE"},
        {"symbol": "JINDALSTEL.NS", "name": "Jindal Steel & Power", "exchange": "NSE"},
        {"symbol": "SHREECEM.NS", "name": "Shree Cement", "exchange": "NSE"},
        {"symbol": "NMDC.NS", "name": "NMDC Ltd", "exchange": "NSE"},
    ]
}

def get_all_tickers() -> List[str]:
    """Returns a flat list of all symbols across all sectors."""
    tickers = []
    for sector, stocks in SECTOR_STOCKS.items():
        for s in stocks:
            tickers.append(s["symbol"])
    return tickers

def get_sector_map() -> Dict[str, Dict[str, str]]:
    """Maps ticker symbol to its sector, name, and exchange."""
    lookup = {}
    for sector, stocks in SECTOR_STOCKS.items():
        for s in stocks:
            lookup[s["symbol"]] = {
                "sector": sector,
                "name": s["name"],
                "exchange": s["exchange"]
            }
    return lookup
