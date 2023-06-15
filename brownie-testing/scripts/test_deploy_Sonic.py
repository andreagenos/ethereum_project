from brownie import accounts, Sonic
import time


def deploy_Sonic():
    acct = accounts[0]
    erc20 = Sonic.deploy({"from": acct})
    time.sleep(1)
    return Sonic

def main():
    deploy_Sonic()
