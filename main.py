#
# BitFind
# 

VERSION = '0.1'
THREADS = 10 # don't set more than 10

from json.decoder import JSONDecodeError
import colorama as c
from bip_utils import *
import requests as r
import multiprocessing
import time

# Hide keyboard iterrupt message
import sys
import signal
signal.signal(signal.SIGINT, lambda x,y: sys.exit(0))

c.init()

class Info:
    total = 0

print(f'{c.Fore.GREEN}BitFind{c.Fore.RESET} version {c.Fore.YELLOW}{VERSION}{c.Style.RESET_ALL}')
print(f'{c.Style.BRIGHT} by maxgrt{c.Style.RESET_ALL}')
print(f'Using {c.Style.BRIGHT}{THREADS}{c.Style.RESET_ALL} thread(s)')


def worker(total):
    seed = Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)
    # print(seed)
    seed_bytes = Bip39SeedGenerator(seed).Generate() # generate seed bytes
    ctx = Bip32Secp256k1.FromSeed(seed_bytes)
    # print(ctx.PrivateKey().ToExtended()) Private key (extended)
    addr = P2WPKHAddr.EncodeKey(bytes(ctx.PublicKey().RawUncompressed()),
                                hrp=CoinsConf.BitcoinMainNet.Params("p2wpkh_hrp"),
                                wit_ver=CoinsConf.BitcoinMainNet.Params("p2wpkh_wit_ver"))
    # print(addr) # Address

    try:
        data = r.get(f'https://chain.so/api/v2/address/BTC/{addr}').json()
        bal = float(data['data']['balance'])
        if bal > 0.0:
            print(f'{c.Back.GREEN}[+] Found {str(bal)} on {addr}[{seed}]{c.Back.RESET} ({total})')
            with open('output.txt', 'a') as f:
                f.write(f'Found {str(bal)} on {addr}[{seed}]\n  {ctx.PrivateKey().ToExtended()}\n')
        else:
            print(f'{c.Fore.GREEN}[-] EMPTY: {addr}{c.Fore.RESET} ({total})')
    except JSONDecodeError as e:
        print(f'{c.Style.BRIGHT}{c.Fore.RED}OOPS! Cannot decode some data!{c.Style.RESET_ALL}')
        time.sleep(2)
    
def main():
    while 1:
        Info.total += 1
        worker(Info.total)
        time.sleep(0.1)

def runner(func: callable):
    func()

if __name__ == '__main__':
    tasks = [main for i in range(THREADS)]
    p = [multiprocessing.Process(target=runner, args=(i,)) for i in tasks]
    for pr in p:
        pr.start()
    
    for pr in p:
        pr.join()
