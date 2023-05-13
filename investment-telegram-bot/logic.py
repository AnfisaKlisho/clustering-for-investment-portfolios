import wget
import pandas as pd

import yfinance as yf

from clustering import get_one_year_df, apply_clustering
from optimization import get_sharpe_ratio_info, optimize_portfolio, get_portfolio_stats


def main(chosen_sum: int, chosen_period: str) -> str:

    """Функция с основной логикой формирования портфеля.

    :param chosen_sum: Выбранная пользователем сумма инвестирования
    :param chosen_period: Выбранный пользователем период инвестирования.
    :return: Текст сообщения для пользователя.
    """

    df_stocks, index_df = load_data(chosen_period_parser(chosen_period))
    stocks_df = get_one_year_df(df_stocks)
    returns = get_sharpe_ratio_info(stocks_df)
    portfolio = apply_clustering(stocks_df, returns)
    weights = optimize_portfolio(stocks_df, portfolio, (0, 0.2))
    text = get_portfolio_stats(df_stocks, index_df, portfolio, weights, chosen_sum)

    return text


def load_data(years: int):

    """Загрузка данных об акциях и индексе S&P 500

    :return: Датафрейм с котировками акций, датафрейм с котировками индекса
    """

    tickers_200 = "https://docs.google.com/uc?export=download&id=1LMPB6_Fh0zirN3Jwe-rMMGM70MgEYq2q"
    tickers_200_file = wget.download(tickers_200)
    stock_tickers = pd.read_csv(tickers_200_file, header=None)
    stock_tickers = list(stock_tickers[0].values)
    for ticker in range(len(stock_tickers)):
        stock_tickers[ticker] = stock_tickers[ticker].upper().replace(".", "-")

    df_stocks = yf.download(stock_tickers,
                            period=f"{years}y",
                            interval="1d")['Adj Close']

    df_stocks.index = pd.to_datetime(df_stocks.index)

    sp500 = 'https://docs.google.com/uc?export=download&id=1w-RQ8PsEPRnbdep4M2Qq9no5__0gagZG'
    sp500_file = wget.download(sp500)
    index_df = pd.read_csv(sp500_file)
    index_df.index = pd.to_datetime(index_df['Date'])
    index_df = index_df.drop('Date', axis=1)

    return df_stocks, index_df


def chosen_period_parser(chosen_period: str) -> int:

    """Парсинг периода инвестирования

    :param chosen_period: Строка с периодом инвестирования.
    :return: Длительность периода в годах.
    """

    years = 0
    if chosen_period == "менее 1 года":
        years = 1
    elif chosen_period == "1-3 года":
        years = 3
    elif chosen_period == "более 3х лет":
        years = 5
    return years
