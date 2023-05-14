from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import base_optimizer, expected_returns, risk_models, discrete_allocation

from collections import OrderedDict
import pandas as pd
import numpy as np


def optimize_portfolio(stocks_df: pd.DataFrame,
                       portfolio: list,
                       weight_bounds: tuple) -> OrderedDict:

    """Сформировать портфель и получить веса акций.

    :param stocks_df: Датафрейм с котировками акций.
    :param portfolio: Список акций, из которых формируем портфель.
    :param weight_bounds: Границы весов акций в портфеле.
    :return: Словарь с акциями и их весами в сформированном портфеле.
    """

    mu = expected_returns.mean_historical_return(stocks_df[portfolio])
    sigma = risk_models.sample_cov(stocks_df[portfolio])

    ef = EfficientFrontier(mu, sigma, weight_bounds=weight_bounds)
    sharpe_pfolio = ef.max_sharpe()
    sharpe_pwt = ef.clean_weights()
    print(sharpe_pwt)
    print()
    ef.portfolio_performance(verbose=True)

    return sharpe_pwt


def get_sharpe_ratio_info(stocks_df: pd.DataFrame) -> pd.DataFrame:

    """Посчитать индексы Шарпа для акций.

    :param stocks_df: Датафрейм с котировками акций.
    :return: Датафрейм с данными по акциями.
    """

    returns = expected_returns.mean_historical_return(stocks_df)
    returns = returns.reset_index()
    returns.columns = ['ticker', 'mean_return']

    risk_free_rate = 0.02

    variance = risk_models.sample_cov(stocks_df)
    returns['var'] = np.array(variance).diagonal()

    returns['sharpe_ratio'] = (returns['mean_return'] -
                               risk_free_rate) / returns['var']

    return returns


def get_portfolio_beta_coef(stocks_df: pd.DataFrame,
                            index_df: pd.DataFrame,
                            portfolio: list,
                            weights: OrderedDict) -> float:

    """Посчитать коэффициент бета для портфеля.

    :param stocks_df: Датафрейм с котировками аккий.
    :param index_df: Датафрейм с котировками индекса.
    :param portfolio: Список акций, которые входят в портфель.
    :param weights: Веса акций в портфеле.
    :return: Коэффициент бета портфеля.
    """

    stocks = stocks_df.copy()
    returns = expected_returns.returns_from_prices(stocks[portfolio])
    weights = pd.DataFrame(weights, index=[0])
    for stock in portfolio:
        returns[stock] = returns[stock] * weights[stock].values[0]

    returns = np.array(returns.sum(axis=1))

    index_returns = np.squeeze(expected_returns.returns_from_prices(index_df))

    beta = np.cov(returns, index_returns)[0][1] / np.var(index_returns)

    return np.round(beta, 2)


def get_portfolio_stats(stocks_df: pd.DataFrame,
                        index_df: pd.DataFrame,
                        portfolio: list,
                        weights: OrderedDict,
                        chosen_sum: int) -> str:

    """Посчитать статистики для портфеля.

    :param stocks_df: Датафрейм с котировками акций.
    :param index_df: Датафрейм с котировками индекса.
    :param portfolio: Список акций, которые входят в портфель.
    :param weights: Веса акций в портфеле.
    :param chosen_sum: Выбранная сумма инвестирования.
    :return: Текст сообщения для пользователя.
    """

    df = stocks_df.copy()

    index = index_df.tail(df.shape[0])

    allocation = allocate_money(weights, portfolio, df, chosen_sum)
    print(allocation)

    exp_returns = expected_returns.mean_historical_return(df[portfolio],
                                                          frequency=df.shape[0])

    cov_matrix = risk_models.sample_cov(df[portfolio],
                                        frequency=df.shape[0])
    text = "===================\n"
    text += "Ваш итоговый портфель:\n"
    text += "===================\n"
    d = dict(weights)
    print(d)
    for ticker in d:
        if d[ticker] > 0:
            try:
                amount = allocation[0][ticker]
                text += f'➡️ <b>{ticker}</b>: {np.round(d[ticker] * 100, 2)}% ({amount} штук)\n'

            except KeyError:
                continue

    text += f"\nОстаток средств: {np.round(allocation[1], 2)} долларов.\n"

    text += "===================\n"

    stats = base_optimizer.portfolio_performance(weights,
                                                 exp_returns,
                                                 cov_matrix,
                                                 verbose=False)

    text += f"Ожидаемая доходность портфеля: {np.round(stats[0] * 100, 2)}%\n"
    text += f"Риск портфеля: {np.round(stats[1] * 100, 2)}%\n"
    text += f"Индекс Шарпа портфеля: {np.round(stats[2], 2)}\n"

    beta = get_portfolio_beta_coef(df, index, portfolio, weights)

    text += f"Бета портфеля: {beta}\n"
    text += "===================\n"

    return text


def allocate_money(weights: OrderedDict,
                   portfolio: list,
                   df_stocks: pd.DataFrame,
                   chosen_sum: int) -> tuple:

    """Распределение средств между акциями.

    :param weights: Веса акций в портфеле.
    :param portfolio: Список акций, которые входят в портфель.
    :param df_stocks: Датафрейм с котировками акций.
    :param chosen_sum: Выбранная сумма инвестирования.
    :return: Кортеж с распределением денежных средств.
    """

    latest_prices = pd.Series(df_stocks.tail(1)[portfolio].values.squeeze(), index=portfolio)
    allocation = discrete_allocation.DiscreteAllocation(weights, latest_prices, chosen_sum)
    alloc = allocation.greedy_portfolio()
    return alloc
