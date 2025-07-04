# utils/options_analyzer.py

import yfinance as yf
import pandas as pd
import datetime

def get_options_chain(ticker, expiry=None):
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        if not expirations:
            return None, "No expirations available"

        # Default to nearest expiration if not specified
        expiry = expiry or expirations[0]

        if expiry not in expirations:
            return None, f"Invalid expiry. Available: {expirations}"

        opt_chain = stock.option_chain(expiry)
        calls = opt_chain.calls.copy()
        puts = opt_chain.puts.copy()
        current_price = stock.history(period="1d")["Close"].iloc[-1]

        # Tagging ITM/ATM/OTM
        def tag_option(row, cp, opt_type):
            if opt_type == "call":
                if row["strike"] < cp:
                    return "ITM"
                elif abs(row["strike"] - cp) / cp < 0.02:
                    return "ATM"
                else:
                    return "OTM"
            else:  # put
                if row["strike"] > cp:
                    return "ITM"
                elif abs(row["strike"] - cp) / cp < 0.02:
                    return "ATM"
                else:
                    return "OTM"

        calls["moneyness"] = calls.apply(lambda x: tag_option(x, current_price, "call"), axis=1)
        puts["moneyness"] = puts.apply(lambda x: tag_option(x, current_price, "put"), axis=1)

        return {
            "current_price": round(current_price, 2),
            "expiry": expiry,
            "calls": calls,
            "puts": puts,
            "expirations": expirations
        }, None
    except Exception as e:
        return None, str(e)

def explain_greek(greek):
    return {
        "delta": "Measures sensitivity to price. High delta is better for directional trades.",
        "gamma": "Rate of change of delta. High gamma = rapid profit/loss near ATM.",
        "theta": "Time decay. Lower theta is better for long options, higher for premium sellers.",
        "vega": "Sensitivity to volatility. High vega benefits from rising IV.",
        "impliedVolatility": "Expected future volatility. Higher IV = more expensive options."
    }.get(greek.lower(), "No explanation available.")
