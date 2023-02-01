import asyncio
import json
from time import sleep
from typing import Union

import pandas as pd
from profit_analysis.chains import ETHEREUM_CHAIN, POLYGON_CHAIN
from profit_analysis.column_names import BLOCK_KEY, PRICE_KEY

from mev_inspect.web3_provider import W3

UNISWAP_V2_PAIR_ABI = json.loads(
    '[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Burn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Mint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1In","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount0Out","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1Out","type":"uint256"},{"indexed":true,"internalType":"address","name":"to","type":"address"}],"name":"Swap","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint112","name":"reserve0","type":"uint112"},{"indexed":false,"internalType":"uint112","name":"reserve1","type":"uint112"}],"name":"Sync","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"MINIMUM_LIQUIDITY","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"PERMIT_TYPEHASH","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"burn","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getReserves","outputs":[{"internalType":"uint112","name":"_reserve0","type":"uint112"},{"internalType":"uint112","name":"_reserve1","type":"uint112"},{"internalType":"uint32","name":"_blockTimestampLast","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_token0","type":"address"},{"internalType":"address","name":"_token1","type":"address"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"kLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"mint","outputs":[{"internalType":"uint256","name":"liquidity","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"price0CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"price1CumulativeLast","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"}],"name":"skim","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount0Out","type":"uint256"},{"internalType":"uint256","name":"amount1Out","type":"uint256"},{"internalType":"address","name":"to","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"swap","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"sync","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"token0","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"token1","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
)
UNISWAP_V2_FACTORY_ABI = json.loads(
    '[{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token0","type":"address"},{"indexed":true,"internalType":"address","name":"token1","type":"address"},{"indexed":false,"internalType":"address","name":"pair","type":"address"},{"indexed":false,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":true,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
)
ERC20_ABI = json.loads(
    '[ {"constant": true, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "payable": false, "stateMutability": "view", "type": "function"}]'
)
UNISWAP_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
QUICKSWAP_FACTORY = "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32"
USDC_TOKEN_ADDRESS_ETHEREUM = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDC_TOKEN_ADDRESS_POLYGON = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"


def determine_base_token(chain):
    chain = chain.lower()
    switcher = {
        ETHEREUM_CHAIN: USDC_TOKEN_ADDRESS_ETHEREUM,
        POLYGON_CHAIN: USDC_TOKEN_ADDRESS_POLYGON,
    }
    return switcher.get(chain, f"Invalid chain@ {chain}")


def determine_factory(chain):
    chain = chain.lower()
    switcher = {ETHEREUM_CHAIN: UNISWAP_FACTORY, POLYGON_CHAIN: QUICKSWAP_FACTORY}
    return switcher.get(chain, f"Invalid chain@ {chain}")


class UniswapPricer:
    def __init__(self, w3_provider, chain):
        self.w3_provider = w3_provider
        self._chain = chain
        self._factory = determine_factory(chain)
        self._pair = None
        self._token_base_address = determine_base_token(chain)
        self._token_target_address = None
        self._token_base_decimals = None
        self._token_target_decimals = None
        self._is_target_token0_or_token1 = None
        self.block_to_price = {}

    async def get_decimals_from_token(self, token):
        contract = await self.w3_provider.w3_provider_async.eth.contract(
            address=token, abi=ERC20_ABI
        )
        decimals = contract.functions.decimals().call()
        print(f"Decimals for {token} = {decimals}")
        return decimals

    async def create(self, token_target_address):
        try:
            print(f"Creating Uniswap Pricer for {token_target_address} ")
            if token_target_address == self._token_base_address:
                return
            self._token_target_address = token_target_address
            factory = await self.w3_provider.w3_provider_async.eth.contract(
                address=self._factory, abi=UNISWAP_V2_FACTORY_ABI
            )
            pair_address = factory.functions.getPair(
                self._token_base_address, token_target_address
            ).call()
            pair_contract = await self.w3_provider.w3_provider_async.eth.contract(
                address=pair_address, abi=UNISWAP_V2_PAIR_ABI
            )
            print(f"pair_address={pair_address}")
            self._pair = pair_contract
            print("Try")
            self._token_base_decimals = 10 ** await self.get_decimals_from_token(
                self._token_base_address
            )
            print("Success")
            print("Try")
            self._token_target_decimals = 10 ** await self.get_decimals_from_token(
                token_target_address
            )
            print("Success")
            token_n = self.is_target_token0_or_token1()
            print(f"_is_target_token0_or_token1={token_n}")
            self._is_target_token0_or_token1 = token_n
            print("Finished")
        except:
            W3.rotate_rpc_url()
            await self.create(token_target_address)

    def is_target_token0_or_token1(self):
        if self._pair.functions.token0().call() == self._token_target_address:
            return 0
        elif self._pair.functions.token1().call() == self._token_target_address:
            return 1
        else:
            raise Exception(
                f"Target token ({self._token_target_address}) not in contract pair {self._pair}"
            )

    async def get_price_at_block(self, block_number: Union[int, float]):
        print(f"STARTING PRICER block_number={block_number}")
        trials = 0
        n_trials = 3
        while trials < n_trials:
            trials += 1
            try:
                if self._token_target_address == self._token_base_address:
                    return 1.0
                reserves = self._pair.functions.getReserves().call(
                    block_identifier=int(block_number)
                )
                if self._is_target_token0_or_token1 == 0:
                    token_target_reserves = reserves[0]
                    token_base_reserves = reserves[1]
                else:
                    token_target_reserves = reserves[1]
                    token_base_reserves = reserves[0]

                print(
                    f"type self._token_base_decimals={type(self._token_base_decimals)}"
                )
                print(f"type token_base_reserves={type(token_base_reserves)}")
                print(f"self._token_base_decimals={self._token_base_decimals}")
                print(f"token_base_reserves={token_base_reserves}")
                price = (
                    (float(token_base_reserves) / float(token_target_reserves))
                    * self._token_target_decimals
                    / self._token_base_decimals
                )

                return float(price)
            except Exception as e:
                print(
                    f"Error ({trials}/{n_trials}), retrying get_price_at_block  - {e}"
                )
                sleep(0.05)
        W3.rotate_rpc_url()
        await self.create(self._token_target_address)
        price = self.get_price_at_block(block_number)
        self.block_to_price[block_number] = price


async def safe_get_price(pricer, block, max_concurrency):
    async with max_concurrency:
        print(block)
        return await pricer.get_price_at_block(block)


async def get_uniswap_historical_prices(
    block_number_min, block_number_max, token_address, chain=POLYGON_CHAIN
):
    # TODO: get only the blocks, not every nthing
    # print(f"pricer for token={token} from={block_number_min}, to ={block_number_max}")
    # token_cg_ids = get_address_to_coingecko_ids_mapping("ethereum", False)
    # token_addresses = token_cg_ids.loc[token_cg_ids[CG_ID_KEY] == cg_id, TOKEN_KEY]
    # token_address = token_addresses.values[0]
    if token_address != "NAN":
        pricer = UniswapPricer(W3, chain)
        # we use USDC as a base token
        await pricer.create(token_address)
        blocks = [
            block_number_min + i
            for i in range(int(block_number_max + 1 - block_number_min))
        ]
        print(blocks)
        tasks = []
        max_c = 1
        max_concurrency = asyncio.Semaphore(max_c)
        for block in range(block_number_min, block_number_max, max_c):
            for block_j in range(block, int(block + max_c)):
                tasks.append(
                    asyncio.ensure_future(
                        safe_get_price(pricer, int(block_j), max_concurrency)
                    )
                )
        await asyncio.gather(*tasks)
        block_to_price = pricer.block_to_price
        return pd.DataFrame(
            list(block_to_price.items()), columns=[BLOCK_KEY, PRICE_KEY]
        )
    else:
        # @TODO: Use coingecko
        return pd.DataFrame(columns=[BLOCK_KEY, PRICE_KEY])
