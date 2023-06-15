import json
import requests
from django.shortcuts import render
from datetime import *
from django.utils import timezone
from .forms import SurveyForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login
from django.contrib.auth.models import User
from web3 import Web3
from .models import Survey

#Goerli Test Wallet where the ERC20 Token was deployed
wallet = '0x2F34362E3E74b4693610C231378e4C124562faA1'
pk = '354ccbaac552bf0a4c3fd0004b50d4225b9d84732e0fc17bde7ffae2ba25eb80'

#Connect to Ethereum testnet Goerli
infura_url = 'https://goerli.infura.io/v3/b51ab601fbea4871845fe9f621bc9746'
web3 = Web3(Web3.HTTPProvider(infura_url))

#Smart Contract Data
abi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"_owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"remaining","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"success","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"balance","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"success","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"success","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]'
contract_address = '0x6107cA52C7D2E2C575E855AAB10AB94D013ED252'
contract_instance = web3.eth.contract(address = contract_address, abi = abi)


def home(request):
    return render(request, 'app/home.html')

# Check if a user has already submitted a survey
def form_exists(author):
    form_exists = Survey.objects.filter(author= author).exists()
    return form_exists


def create_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        check_form = form_exists(request.user)
        if form.is_valid and check_form == False:
            survey = form.save(commit=False)
            survey.author = request.user
            survey.datetime = timezone.now()
           
            #Send Reword to the user wallet and save the survey
            nonce = web3.eth.getTransactionCount(wallet)
            address = request.user.get_username()
            tx = contract_instance.functions.transfer(address, 100).buildTransaction({
                    'nonce': nonce,
                    'gas': 2000000,
                    'gasPrice': web3.eth.gasPrice,
                })
            sign_tx = web3.eth.account.sign_transaction(tx, pk)
            tx_hash = web3.eth.send_raw_transaction(sign_tx.rawTransaction)
            transaction_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
            transaction_receipt_json = Web3.toJSON(transaction_receipt)
            survey.save()
            return HttpResponse(transaction_receipt_json)
        else:
            return HttpResponse("You have already submitted your Survey!")
    else:
        form = SurveyForm()
    return render(request, 'app/survey.html', {'form': form})


#Morails Auth for User Authentication with Metamask
API_KEY = 'CIzzgg5ZUVSq5PXgB7anw0Tf5f0LK1y3UWOV2YAnfS3Xtw8Bs0SdGusfplXyNE3j'
# this is a check to make sure the API key was set
if API_KEY == 'WEB3_API_KEY_HERE':
    print("API key is not set")
    raise SystemExit


def moralis_auth(request):
    return render(request, 'app/login.html', {})

def my_profile(request):
    return render(request, 'app/profile.html', {})

def request_message(request):
    data = json.loads(request.body)
    print(data)

    #setting request expiration time to 1 minute after the present->
    present = datetime.now(timezone.utc)
    present_plus_one_m = present + timedelta(minutes=1)
    expirationTime = str(present_plus_one_m.isoformat())
    expirationTime = str(expirationTime[:-6]) + 'Z'

    REQUEST_URL = 'https://authapi.moralis.io/challenge/request/evm'
    request_object = {
      "domain": "defi.finance",
      "chainId": 1,
      "address": data['address'],
      "statement": "Please confirm",
      "uri": "https://defi.finance/",
      "expirationTime": expirationTime,
      "notBefore": "2020-01-01T00:00:00.000Z",
      "timeout": 15
    }
    x = requests.post(
        REQUEST_URL,
        json=request_object,
        headers={'X-API-KEY': API_KEY})

    return JsonResponse(json.loads(x.text))


def verify_message(request):
    data = json.loads(request.body)
    print(data)

    REQUEST_URL = 'https://authapi.moralis.io/challenge/verify/evm'
    x = requests.post(
        REQUEST_URL,
        json=data,
        headers={'X-API-KEY': API_KEY})
    print(json.loads(x.text))
    print(x.status_code)
    if x.status_code == 201:
        # user can authenticate
        eth_address=json.loads(x.text).get('address')
        print("eth address", eth_address)
        try:
            user = User.objects.get(username=eth_address)
        except User.DoesNotExist:
            user = User(username=eth_address)
            user.is_staff = False
            user.is_superuser = False
            user.save()
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session['auth_info'] = data
                request.session['verified_data'] = json.loads(x.text)
                return JsonResponse({'user': user.username})
            else:
                return JsonResponse({'error': 'account disabled'})
    else:
        return JsonResponse(json.loads(x.text))