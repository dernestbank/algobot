

Sources:


Comprehensive Notes on Algorithmic Trading Strategies

Introduction to Algorithmic Trading
    •	Definition: Algorithmic trading (or algo trading) involves using computer programs to execute trades based on a predefined set of rules.
    •	Automation: Eliminates human intervention, ensuring trades are executed systematically.
    •	Purpose: Designed to minimize behavioral biases, enhance efficiency, and leverage computational speed.
    •	Disclaimer: Not investment advice; requires thorough testing and understanding.

Seven Algorithmic Trading Strategies
    1.	Scaling In Strategy
    •	Concept: Divide capital into parts and buy at different predetermined intervals, e.g., buying more as prices drop further.
    •	Example Rules:
    •	Trade ETF tracking S&P 500 (e.g., SPY).
    •	Original: Buy on weakness, sell on strength (exit when close > previous day’s high).
    •	Improvement: Invest 50% on the first buy signal, add 50% if 5-day RSI drops significantly (e.g., from 33 to 26).
    •	Benefits:
    •	Same returns with reduced risk.
    •	Drawdowns decreased (e.g., from 23% to 17.7%).
    •	Effective for mean-reverting assets like stocks.
    2.	Sell the Rip Strategy
    •	Concept: Focuses on when to sell rather than buy.
    •	Example Rules:
    •	Classical RSI strategy: Buy on weakness, sell on strength.
    •	Improvement: Sell at the close when the price is above the previous day’s high (called the “Qs Exit”).
    •	Benefits:
    •	More stable returns, reduced drawdowns, and increased profitability compared to original rules.
    3.	First Trading Day of the Month Strategy
    •	Concept: Capitalizes on market tendencies around month-end/start.
    •	Example Rules:
    •	Go long at the close of the last trading day of the month.
    •	Sell at the close of the first trading day of the new month.
    •	Insights:
    •	First trading day shows significantly higher returns than random days.
    •	Extended version: Hold stocks during the last 5 days of the month and the first 3 days of the new month (“Turn-of-the-Month Strategy”).
    •	Most S&P 500 returns occur during these periods.
    4.	Pullback Trading Strategy
    •	Concept: Combines trend-following and pullbacks during bullish markets.
    •	Example Rules:
    •	Use the 200-day moving average as a long-term trend filter (buy only in bullish trends).
    •	Buy on short-term weakness or pullbacks.
    •	Performance:
    •	Grew $100,000 to $1,000,000 over time.
    •	Less time in the market (~30%) while achieving strong returns.
    5.	Fabian Timing Model
    •	Concept: Long-term trend-following strategy developed in the 1960s.
    •	Example Rules:
    •	Use intermarket signals between S&P 500, Dow Jones, and Utilities sector.
    •	Buy when all indices are above their 39-week moving average; sell when at least two drop below.
    •	Performance:
    •	Outperformed S&P 500 since 2000 while being invested only ~50% of the time.
    6.	Momentum Strategy (Meb Faber)
    •	Concept: Trades stocks, bonds, and gold based on momentum and trend-following.
    •	Example Rules:
    •	Use ETFs like SPY (stocks), TLT (bonds), and GLD (gold).
    •	Buy when the 3-month moving average is above the 10-month moving average; stay out otherwise.
    •	Insights:
    •	Historically strong returns until 2015 but underperformed in recent years.
    •	Long-term historical return: 13.1% with lower drawdowns than buy-and-hold strategies.
    7.	Mean Reversion Strategy (Premium)
    •	Concept: Focuses on assets that tend to revert to their mean price.
    •	Example Rules:
    •	Simplified buy and sell conditions.
    •	Performance:
    •	$100,000 invested in 1993 compounded to achieve ~15% annual returns.
    •	Lower drawdowns and reduced market exposure (~35%).

Advantages of Algorithmic Trading
    1.	Efficiency:
    •	Automated execution reduces manual intervention.
    •	Trades multiple strategies simultaneously.
    2.	Focus on Strategy Development:
    •	Allows more time for refining strategies rather than managing trades.
    3.	Behavioral Discipline:
    •	Reduces emotional decision-making by adhering to predefined rules.
    4.	Consistency:
    •	Execution remains systematic, even in volatile markets.

Disadvantages of Algorithmic Trading
    1.	Learning Curve:
    •	Requires programming skills (e.g., Python).
    •	Backtesting and optimization are essential, requiring trial and error.
    2.	Effort-Intensive:
    •	Strategies need to be researched, tested, and adjusted.
    3.	No Guarantees:
    •	Profitable backtests don’t always translate to future success.

Key Takeaways
    •	Algorithmic trading doesn’t need to be complex.
    •	Simpler strategies are often more robust and profitable in the long term.
    •	Backtesting is crucial to validate strategies.
    •	Consistency, a systematic mindset, and understanding the law of large numbers are essential for success.

Next Steps
    •	Study backtesting methods.
    •	Experiment with coding and simple strategies.
    •	Build on strategies gradually and refine them based on results.
