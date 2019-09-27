import bs4 as bs
import datetime as dt
import os
import pandas as pd
from matplotlib import style
import matplotlib.pyplot as plt
import pandas_datareader.data as web
from pandas_datareader import data as pdr
import pickle
import requests
import numpy as np

style.use('ggplot')


def save_sp500_tickers():

    resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find("table", {"class": "wikitable sortable"})
    tickers = []

    for row in table.findAll("tr")[1:11]:  # changed the range

        ticker = row.findAll('td')[0].text.strip().replace(".", "-")

        mapping = str.maketrans(".", "-")

        new_ticker = ticker.translate(mapping)

        tickers.append(new_ticker)

    with open("sp500tickers.pickle", "wb") as f:

        pickle.dump(tickers, f)

        return tickers


def get_data():

    if not os.path.exists('/Users/Corey/SPY/sp500_index'):
        os.makedirs('/Users/Corey/SPY/sp500_index')

    print(save_sp500_tickers())

    year1 = int(input('\nEnter a start year: '))
    month1 = int(input('\nEnter start month: '))
    day1 = int(input('\nEnter start day: '))

    start_date = dt.date(year1, month1, day1)

    year2 = int(input('\nEnter an ending year: '))
    month2 = int(input('\nEnter ending month: '))
    day2 = int(input('\nEnter ending day: '))

    end_date = dt.date(year2, month2, day2)

    for ticker in save_sp500_tickers():
        if not os.path.exists('/Users/Corey/SPY/sp500_index/{}.csv'.format(ticker)):
            data = pdr.get_data_yahoo(ticker, start_date, end_date)
            data.reset_index(inplace=True)
            data.set_index("Date", inplace=True)

            data.to_csv('/Users/Corey/SPY/sp500_index/{}.csv'.format(ticker))
        else:
            print('Already have {}'.format(ticker))


get_data()


def compile_data():
    with open("sp500tickers.pickle", "rb") as f:
        tickers = pickle.load(f)

    main_df = pd.DataFrame()

    for count, ticker in enumerate(tickers):
        data = pd.read_csv('/Users/Corey/SPY/sp500_index/{}.csv'.format(ticker))
        data.set_index('Date', inplace=True)

        data.rename(columns={'Adj Close': ticker}, inplace=True)
        data.drop(['Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace=True)

        if main_df.empty:
            main_df = data
        else:
            main_df = main_df.join(data, how='outer')

        if count % 10 == 0:
            print(count)
    print(main_df.head())
    main_df.to_csv('/Users/Corey/SPY/sp500_joined_closes.csv')


compile_data()


def visualize_data():
    df = pd.read_csv('/Users/Corey/SPY/sp500_joined_closes.csv')
    # df['AAPL'].plot()
    # plt.show()
    df_corr = df.corr()
    print(df_corr.head())
    df_corr.to_csv('/Users/Corey/SPY/sp500corr.csv')

    data1 = df_corr.values
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1, 1)
    plt.tight_layout()
    # plt.savefig("correlations.png", dpi = (300))
    plt.show()


visualize_data()
