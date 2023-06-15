from brownie import accounts, Sonic
import pytest
import time


@pytest.fixture
def token():
    return accounts[0].deploy(Sonic)

def test_symbol(token):
    assert token.symbol() == "SNC"
    time.sleep(1)

def test_name(token):
    assert token.name() == "Sonic"
    time.sleep(1)

def test_account_balance():
    balance = accounts[0].balance()
    accounts[0].transfer(accounts[1], "5 ether", gas_price=0)
    assert balance - "5 ether" == accounts[0].balance()
    time.sleep(1)

def test_mint(token):
    assert token.balanceOf('0x2F34362E3E74b4693610C231378e4C124562faA1') == 1_000_000_000_000_000_000_000_000
    time.sleep(1)

def test_transfer(token):
    token.transfer(accounts[1], 100, {'from': '0x2F34362E3E74b4693610C231378e4C124562faA1'})
    assert token.balanceOf('0x2F34362E3E74b4693610C231378e4C124562faA1') == (1_000_000_000_000_000_000_000_000 - 100)
    time.sleep(1)
