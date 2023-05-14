import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering


def get_portfolio_tickers(cluster_dict: dict,
                          sharpe_ratio_df: pd.DataFrame) -> list:

    """Получить список тикеров акций, из которых будет формироваться инвестиционный портфель

    :param cluster_dict: Словарь с кластеризованными акциями.
    :param sharpe_ratio_df: Датафрейм с индексами Шарпа для всех акций.
    :return:Список акций, которые войдут в итоговый портфель.
    """

    portfolio = []
    for label in cluster_dict:
        cluster = sharpe_ratio_df[sharpe_ratio_df['ticker'].isin(cluster_dict[label])]

        portfolio.append(
            cluster.iloc[cluster['sharpe_ratio'].argmax()]['ticker']
        )

    return portfolio


def get_corr_dissimilarity_matrix(stocks_df: pd.DataFrame) -> np.ndarray:

    """Сформировать матрицу корреляций.

    :param stocks_df: Датафрейм с котировками акций.
    :return: Матрица корреляций.
    """

    corr = np.corrcoef(stocks_df.T)
    corr = (corr + corr.T) / 2
    np.fill_diagonal(corr, 1)
    dissimilarity = np.sqrt(2 * (1 - corr))
    np.triu(dissimilarity)

    return np.triu(dissimilarity)


def get_one_year_df(stocks_df: pd.DataFrame) -> pd.DataFrame:

    """Взять данные за один год.

    :param stocks_df: Датафрейм с котировками акций.
    :return: Обрезанный датафрейм
    """

    frequency = 252

    stocks_df = stocks_df.copy()
    stocks_df = stocks_df.tail(frequency)

    return stocks_df


def get_clusters(stocks_df: pd.DataFrame, cluster_labels: np.array) -> dict:

    """Получить кластеры акций.

    :param stocks_df: Датафрейм с котировками акций.
    :param cluster_labels: Лейблы с кластерами.
    :return: Словарь с кластерами.
    """

    cluster_dict = {}
    for i, label in enumerate(cluster_labels):
        if label not in cluster_dict:
            cluster_dict[label] = []
        cluster_dict[label].append(stocks_df.columns[i])

    return cluster_dict


def apply_clustering(stocks_df: pd.DataFrame, returns: pd.DataFrame) -> list:

    """Метод формирования кластеров акций.

    :param stocks_df: Датафрейм с котировками акций.
    :param returns: Датафрейм со статистиками по акциям.
    :return: Список акций, которые войдут в портфель.
    """

    dissimilarity = get_corr_dissimilarity_matrix(stocks_df)
    clust = AgglomerativeClustering(n_clusters=10, linkage='ward')
    labels = clust.fit_predict(dissimilarity)
    cluster_dict = get_clusters(stocks_df, labels)
    portfolio = get_portfolio_tickers(cluster_dict, returns)
    return portfolio
