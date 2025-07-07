# setup.py

from setuptools import setup, find_packages

setup(
    name="trading_bot",
    version="0.1.0",
    packages=find_packages(include=["core", "core.*"]),
    install_requires=[
        "pandas",
        "yfinance",
        "schedule",
        "matplotlib",
        # Add any other dependencies you use
    ],
    entry_points={
        "console_scripts": [
            "trading-bot=core.run:main",
        ],
    },
)
