Professional Options Flow Analyzer



Advanced institutional-grade options flow monitoring system with real-time analytics, Greeks calculations, and professional dashboard



\[!\[Python 3.13.7+](https://img.shields.io/badge/Python-3.13.7+-blue.svg)](https://www.python.org/downloads/)

\[!\[License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

\[!\[Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()



 Features



Core Analytics Engine

Real-time Options Data Collection - Multi-source data aggregation

Advanced Greeks Calculations - Delta, Gamma, Theta, Vega, Rho

Implied Volatility Analysis - IV surface modeling and skew detection

Max Pain Calculation - Options expiration pressure points

Put/Call Ratio Analysis - Market sentiment indicators



Institutional Flow Detection

Block Trade Identification - Large institutional transactions

Sweep Detection- Multi-exchange aggressive orders

Dark Pool Activity - Hidden liquidity analysis

Whale Activity Tracking - $1M+ premium transactions

Smart Money Flow Classification - Retail vs Institutional



Professional Dashboard

Real-time Web Interface- Modern, responsive design

Interactive Charts- Plotly-powered visualizations

Flow Heatmaps - Premium distribution analysis

Live Data Tables - Sortable, filterable options flow

Custom Alerts - Configurable thresholds and notifications



Advanced Analytics

Volatility Surface Analysis - 3D IV modeling

Multi-Strike Strategies - Complex position detection

Time Decay Analysis - Theta exposure calculations

Risk Metrics- Portfolio Greeks and exposures

Sentiment Scoring - Algorithmic market sentiment



 Quick Start



 Installation



1\. \*\*Clone Repository\*\*

```bash

git clone https://github.com/ChanceAndersonLU/optionsflow.git

cd optionsflow

```



2\. \*\*Set Up Environment\*\*

```bash

\# Create virtual environment

python -m venv venv



\# Activate (Windows)

venv\\Scripts\\activate



\# Activate (Mac/Linux)

source venv/bin/activate

```



3\. \*\*Install Dependencies\*\*

```bash

pip install -r requirements\_professional.txt

```



4\. \*\*Configure Environment\*\*

```bash

\# Copy and edit .env file

cp .env.example .env

\# Edit .env with your API keys (optional for basic functionality)

```



\### Basic Usage



\####  \*\*Single Symbol Analysis\*\*

```bash

python main\_professional.py -s AAPL

```



\####  \*\*Launch Web Dashboard\*\*

```bash

python main\_professional.py -d

```

Then open: http://localhost:8050



\####  \*\*Generate Professional Report\*\*

```bash

python main\_professional.py -r TSLA

```



\####  \*\*Multi-Symbol Screening\*\*

```bash

python main\_professional.py -sc

```



\####  \*\*Interactive CLI\*\*

```bash

python main\_professional.py

```



\##  Project Structure



```

optionsflow/

├── src/

│   ├── data\_collector.py          # Multi-source data collection

│   ├── advanced\_analytics.py      # Greeks, IV, flow analysis

│   ├── dashboard.py               # Professional web dashboard

│   ├── flow\_analyzer.py           # Flow classification engine

│   └── visualizer.py              # Advanced charting

├──  config/

│   ├── settings.py                # Basic configuration

│   └── advanced\_settings.py       # Professional settings

├── data/                       # Data storage

├──  exports/                    # Generated reports

├──  logs/                       # Application logs

├──  tests/                      # Unit tests

├── main.py                        # Basic application

├── main\_professional.py           # Professional application

└── requirements\_professional.txt  # Enhanced dependencies

```



\##  Configuration



\### API Keys (Optional)



For enhanced data sources, add to `.env`:



```bash

\# Professional Data Sources

ALPHA\_VANTAGE\_API\_KEY=your\_key\_here

POLYGON\_API\_KEY=your\_key\_here

TRADIER\_API\_KEY=your\_key\_here



\# Alerting (Optional)

DISCORD\_WEBHOOK=your\_webhook\_url

SLACK\_WEBHOOK=your\_webhook\_url

EMAIL\_USER=your\_email

EMAIL\_PASSWORD=your\_app\_password

```



\### Flow Detection Settings



Customize in `config/advanced\_settings.py`:



```python

\# Flow Detection Thresholds

MIN\_PREMIUM\_THRESHOLD = 25000      # $25K minimum

INSTITUTIONAL\_THRESHOLD = 500000   # $500K for institutional

BLOCK\_TRADE\_MIN\_SIZE = 500         # 500+ contracts

UNUSUAL\_VOLUME\_MULTIPLIER = 10.0   # 10x average volume

```



\##  Dashboard Features



\###  \*\*Key Metrics Display\*\*

\- Current stock price with live updates

\- Total premium volume across all options

\- Unusual activity count and scoring

\- Real-time Put/Call ratios

\- Market sentiment indicators



\###  \*\*Interactive Charts\*\*



1\. \*\*Flow Heatmap\*\* - Premium distribution by moneyness/type

2\. \*\*Volume by Strike\*\* - Call/Put volume visualization

3\. \*\*Time Series Flow\*\* - Historical flow patterns

4\. \*\*Greeks Analysis\*\* - Portfolio risk exposure



\###  \*\*Live Flow Table\*\*

\- Real-time options transactions

\- Flow classification (Block/Sweep/Single)

\- Unusual activity scoring (0-100)

\- Greeks calculations per contract

\- Sortable by premium, volume, or unusual score



\##  Analytics Explained



\### \*\*Flow Classification\*\*



| Flow Type | Description | Criteria |

|-----------|-------------|----------|

| \*\*Block\*\* | Large institutional trade | 500+ contracts, $100K+ premium |

| \*\*Sweep\*\* | Multi-exchange aggressive | 100+ contracts, wide spreads |

| \*\*Single\*\* | Regular market order | Standard retail-sized trades |



\### \*\*Size Categories\*\*



| Category | Premium Range | Volume Range | Interpretation |

|----------|---------------|--------------|----------------|

| \*\*Whale\*\* | $1M+ | 2000+ contracts | Mega institutional |

| \*\*Institutional\*\* | $100K+ | 500+ contracts | Professional traders |

| \*\*Retail\*\* | <$100K | <500 contracts | Individual traders |



\### \*\*Unusual Activity Scoring\*\*



The system calculates a 0-100 unusual score based on:

\- \*\*Volume Component (40%)\*\* - vs historical average

\- \*\*Premium Component (30%)\*\* - absolute dollar threshold

\- \*\*Open Interest Ratio (20%)\*\* - volume vs existing OI

\- \*\*Timing Component (10%)\*\* - proximity to expiration



\### \*\*Greeks Portfolio Analysis\*\*



\- \*\*Delta Exposure\*\* - Directional market exposure

\- \*\*Gamma Risk\*\* - Acceleration risk on moves

\- \*\*Theta Decay\*\* - Daily time decay cost

\- \*\*Vega Sensitivity\*\* - Volatility exposure



\## 📋 Report Generation



\### \*\*Comprehensive Analysis Reports\*\*



Generate detailed reports with:



```bash

python main\_professional.py -r SYMBOL

```



\*\*Report Sections:\*\*

\-  Market Overview \& Key Metrics

\-  Put/Call Ratio Analysis  

\-  Max Pain Level Calculations

\-  Portfolio Greeks Analysis

\-  Flow Classification Summary

\-  Institutional Activity Assessment

\-  Implied Volatility Analysis

\-  Trading Insights \& Recommendations



