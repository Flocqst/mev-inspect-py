import datetime

import pandas as pd
import web3
from profit_analysis.block_utils import add_block_timestamp
from profit_analysis.coingecko import (
    add_cg_ids,
    get_address_to_coingecko_ids_mapping,
    get_coingecko_historical_prices,
)
from profit_analysis.column_names import (
    AMOUNT_DEBT_KEY,
    AMOUNT_RECEIVED_KEY,
    CG_ID_DEBT_KEY,
    CG_ID_RECEIVED_KEY,
    DECIMAL_DEBT_KEY,
    PRICE_DEBT_KEY,
    PRICE_KEY,
    PRICE_RECEIVED_KEY,
    TIMESTAMP_KEY,
    TOKEN_DEBT_KEY,
    TOKEN_RECEIVED_KEY,
)
from profit_analysis.constants import DATA_PATH
from profit_analysis.read import read_profit_from_to
from profit_analysis.token_utils import get_decimals

"""
Steps:
1. given blockfrom and block to, read the profit
"""

WETH_TOKEN_ADDRESS = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"
PD_DATETIME_FORMAT = "datetime64[ns]"


def analyze_profit(inspect_db_session, block_from, block_to, save_to_csv=False):
    profit = read_profit_from_to(inspect_db_session, block_from, block_to)
    w3 = create_web3()
    profit = add_block_timestamp(w3, profit)
    profit = add_cg_ids(profit)
    profit = get_usd_profit_arbitrages(profit, save_to_csv)
    return profit


def get_usd_profit_arbitrages(profit_by_block, save_to_csv=False):
    tokens = profit_by_block[CG_ID_RECEIVED_KEY].unique()
    mapping = get_address_to_coingecko_ids_mapping()
    profit_with_price_tokens = pd.DataFrame()
    failures = {}
    for token in tokens:
        print("Processing", token)
        try:

            profit_by_block_token = pd.DataFrame(
                profit_by_block.loc[profit_by_block[CG_ID_RECEIVED_KEY] == token]
            )
            profit_by_block_token[TIMESTAMP_KEY] = pd.to_datetime(
                profit_by_block_token[TIMESTAMP_KEY], format="%Y-%m-%d %H:%M:%S"
            )

            dates = pd.to_datetime(profit_by_block_token[TIMESTAMP_KEY].unique())
            # @TODO: What is an optimal value here?
            # looks like sometimes there is no price for hours???
            offset_minutes = 30
            date_min = int(
                (dates.min() - datetime.timedelta(minutes=offset_minutes)).timestamp()
            )
            date_max = int(
                (dates.max() + datetime.timedelta(minutes=offset_minutes)).timestamp()
            )

            # get received token prices
            token_prices = get_coingecko_historical_prices(date_min, date_max, token)
            token_prices = token_prices.rename(columns={PRICE_KEY: PRICE_RECEIVED_KEY})
            token_prices[TOKEN_RECEIVED_KEY] = token

            # get received token decimals
            decimals = get_decimals(profit_by_block_token[TOKEN_RECEIVED_KEY].values[0])

            # get debt tokens prices
            debt_tokens_prices = pd.DataFrame()
            for cg_id_debt in (
                profit_by_block_token[CG_ID_DEBT_KEY].astype(str).unique().tolist()
            ):
                if cg_id_debt != "nan":
                    debt_token_prices = get_coingecko_historical_prices(
                        date_min, date_max, cg_id_debt
                    )
                    debt_token_prices[CG_ID_DEBT_KEY] = cg_id_debt
                    debt_token = mapping.loc[
                        mapping[CG_ID_DEBT_KEY] == cg_id_debt, TOKEN_DEBT_KEY
                    ].values[0]
                    debt_token_prices[TOKEN_DEBT_KEY] = debt_token
                    debt_tokens_prices = pd.concat(
                        [debt_tokens_prices, debt_token_prices]
                    )
            debt_tokens_prices = debt_tokens_prices.rename(
                columns={PRICE_KEY: PRICE_DEBT_KEY}
            )

            # get debt tokens decimals
            debt_tokens_decimals = pd.DataFrame(
                columns=[TOKEN_DEBT_KEY, DECIMAL_DEBT_KEY]
            )
            for debt_token in (
                profit_by_block_token[TOKEN_DEBT_KEY].astype(str).unique().tolist()
            ):
                if debt_token != "":
                    debt_token_decimals = get_decimals(debt_token)
                    debt_tokens_decimals = pd.concat(
                        [
                            debt_tokens_decimals,
                            pd.DataFrame(
                                [[debt_token, debt_token_decimals]],
                                columns=[TOKEN_DEBT_KEY, DECIMAL_DEBT_KEY],
                            ),
                        ]
                    )
            profit_by_block_token = profit_by_block_token.merge(
                debt_tokens_decimals, on=TOKEN_DEBT_KEY, how="outer"
            )
            profit_by_block_token.loc[
                pd.isna(profit_by_block_token[AMOUNT_DEBT_KEY]), AMOUNT_DEBT_KEY
            ] = 0

            # apply decimals
            profit_by_block_token[AMOUNT_RECEIVED_KEY] = pd.to_numeric(
                profit_by_block_token[AMOUNT_RECEIVED_KEY]
            ).div(10**decimals)
            profit_by_block_token[AMOUNT_DEBT_KEY] = pd.to_numeric(
                profit_by_block_token[AMOUNT_DEBT_KEY]
            )

            # set up timestamps for merge
            token_prices[TIMESTAMP_KEY] = pd.to_datetime(token_prices[TIMESTAMP_KEY])

            # merge received token prices
            profit_with_price_token = pd.merge_asof(
                profit_by_block_token.astype({TIMESTAMP_KEY: PD_DATETIME_FORMAT})
                .sort_values(TIMESTAMP_KEY)
                .convert_dtypes(),
                token_prices[[TIMESTAMP_KEY, PRICE_RECEIVED_KEY]]
                .astype({TIMESTAMP_KEY: PD_DATETIME_FORMAT})
                .sort_values(TIMESTAMP_KEY)
                .convert_dtypes(),
                direction="nearest",
                on=TIMESTAMP_KEY,
            )

            if len(debt_tokens_prices) > 0:
                debt_tokens_prices[TIMESTAMP_KEY] = pd.to_datetime(
                    debt_tokens_prices[TIMESTAMP_KEY]
                )
                # merge debt token prices
                profit_with_price_token = pd.merge_asof(
                    profit_with_price_token.astype({TIMESTAMP_KEY: PD_DATETIME_FORMAT})
                    .sort_values(TIMESTAMP_KEY)
                    .convert_dtypes(),
                    debt_tokens_prices[[TIMESTAMP_KEY, PRICE_DEBT_KEY]]
                    .astype({TIMESTAMP_KEY: PD_DATETIME_FORMAT})
                    .sort_values(TIMESTAMP_KEY)
                    .convert_dtypes(),
                    direction="nearest",
                    on=TIMESTAMP_KEY,
                    by=TOKEN_DEBT_KEY,
                )
            else:
                profit_with_price_tokens[PRICE_DEBT_KEY] = 0

            profit_with_price_tokens = pd.concat(
                [profit_with_price_tokens, profit_with_price_token]
            )
        except Exception as e:
            # @TODO: save into list to add later
            print("    Failed for token=", token)
            print(e)
            failures[token] = e
    print("Finished processing all tokens")
    profit_with_price_tokens[PRICE_DEBT_KEY] = profit_with_price_tokens[
        PRICE_DEBT_KEY
    ].fillna(value=0)
    profit_with_price_tokens[AMOUNT_DEBT_KEY] = profit_with_price_tokens[
        AMOUNT_DEBT_KEY
    ].fillna(value=0)
    profit_with_price_tokens["profit_usd"] = (
        profit_with_price_tokens[AMOUNT_RECEIVED_KEY]
        * profit_with_price_tokens[PRICE_RECEIVED_KEY]
        - profit_with_price_tokens[AMOUNT_DEBT_KEY]
        * profit_with_price_tokens[PRICE_DEBT_KEY]
    )
    profit_with_price_tokens = profit_with_price_tokens.reset_index(drop=True)
    profit_with_price_tokens["date"] = profit_with_price_tokens[
        TIMESTAMP_KEY
    ].dt.normalize()
    if save_to_csv:
        profit_by_block.to_csv(DATA_PATH + "usd_profit.csv", index=False)
        pd.DataFrame(failures.items(), columns=["token", "error"]).to_csv(
            DATA_PATH + "analyze_profit_failures.csv", index=False
        )
    return profit_with_price_tokens


def get_profit_by(profit_with_price_tokens, col):
    profit_by_block = (
        profit_with_price_tokens.groupby([col])
        .agg({"profit_usd": ["sum", "mean", "median", "count"]})
        .reset_index()
    )
    profit_by_block.columns = profit_by_block.columns.droplevel(0)
    profit_by_block.rename(columns={"": col}, inplace=True)
    profit_by_block.to_csv(DATA_PATH + "profit_by_" + col + ".csv", index=False)
    return profit_by_block


def create_web3():
    w3_provider = web3.Web3(web3.Web3.HTTPProvider("https://polygon-rpc.com"))
    w3_provider.middleware_onion.inject(web3.middleware.geth_poa_middleware, layer=0)
    if w3_provider.isConnected():
        return w3_provider
    else:
        raise Exception("Failed to connect")
