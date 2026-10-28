import requests
import time import os
from datetime import datetime
# CONFIGURATION DISCORD
DISCORD_WEBHOOK_URL = os getenv ("DISCORD_WEBHOOK_URL" )
HELIUS_API_KEY = os getenv ("HELIUS_API_KEY")
def charger_ wallets ():
try:
with open ("wallets.txt", "I")
as f:
return [line.strip() for
line in f if line. strip ()]
except FileNotFoundError:
print( "ERREUR: Fichier
wallets.txt introuvable.")
return []
def
envoyer_discord (message) :
•'''Envoie le message sur le salon
Discord via le Webhook""
payload = {"content": message}
try:
requests .post(DISCORD_WEBHOOK_URL, json=payload, timeout=10) except Exception as e:
print(f"Erreur Discord : {e}")
def scanner_wallet(wallet):
url = f"https://api.helius.xyz/v0/
addresses/{wallet}/transactions?api-key={HELIUS_API_KEY}&limit=3"
try:
response = requests. get (url,
timeout=10)
if response. status_code == 200:
return response. json ()
except Exception:
pass
return []
def analyser_transaction(tx):
if tx.get( 'type') == "SWAP' :
for transfer in tx get ('tokenTransfers', []):
mint = transfer.get( 'mint')
# Ignore sol et USDC
if mint not in
["So11111111111111111111111111111111111
111112",
"EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZw
yTDt1v"] :
return mint
return None
def main():
wallets = charger_wallets()
print(f"Radar Discord activé sur
{len (wallets)} wallets.")
deja_vu = set( )
while True:
for wallet in wallets:
txs =
scanner _wallet (wallet)
for tx in txs:
tx_id =
tx. get ('signature')
if tx_id not in
deja_vu:
deja_vu. add (tx_id)
token_mint =
analyser_transaction (tx)
**SMART WALLET BUY**
if token_mint:
msg = f"
\n"
msg += f"
'{wallet[:61}...'\n"
msg += f"
CA : {token_mint} '\n" msg += f"o
https://axiom.trade/token/{token_mint}"
print(f" [idatetime.now().strftime('%Н:
%M:%S')}] Achat détecté :
{token_mint}")
envoyer_discord(msg)
time. sleep(15) # Scan toutes
les 15 secondes
if __name__ == " __main__":
main ()
