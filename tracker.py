import requests
import time
import os
from datetime import datetime

# ==========================================
# CONFIGURATION DU RADAR HYBRIDE (NTFY)
# ==========================================
# Remplace par l'URL exacte de ton topic Ntfy
NTFY_URL = "https://ntfy.sh/bot-radar-mmco-alert6548" 
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

def charger_wallets():
    try:
        with open("wallets.txt", "r") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("ERREUR: Fichier wallets.txt introuvable.", flush=True)
        return []

def envoyer_alerte(message):
    """Envoie le message sur ton téléphone via Ntfy"""
    try:
        requests.post(NTFY_URL, data=message.encode(encoding='utf-8'), timeout=10)
        print(f"[+] Alerte envoyée à Ntfy.", flush=True)
    except Exception as e:
        print(f"Erreur Ntfy : {e}", flush=True)

def verifier_token_dexscreener(token_address):
    """Vérifie si le token a assez de liquidité et de volume"""
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('pairs') and len(data['pairs']) > 0:
                pair = data['pairs'][0]
                liquidity = float(pair.get('liquidity', {}).get('usd', 0))
                volume_5m = float(pair.get('volume', {}).get('m5', 0))
                
                # FILTRES DE SÉCURITÉ
                if liquidity > 10000 and volume_5m > 5000:
                    return True, liquidity, volume_5m
    except Exception as e:
        print(f"Erreur DexScreener: {e}", flush=True)
    return False, 0, 0

def scanner_wallet(wallet):
    """Récupère les dernières transactions d'un wallet"""
    url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions?api-key={HELIUS_API_KEY}&limit=3"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []

def analyser_transaction(tx):
    """Détecte si c'est un achat de token"""
    if tx.get('type') == 'SWAP':
        for transfer in tx.get('tokenTransfers', []):
            mint = transfer.get('mint')
            # Ignore SOL et USDC
            if mint not in ["So11111111111111111111111111111111111111112", "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"]:
                return mint
    return None

def main():
    wallets = charger_wallets()
    envoyer_alerte("TEST : Le bot est en ligne !")
    print(f"Radar Hybride activé sur {len(wallets)} wallets.", flush=True)
    deja_vu = set()

    while True:
        for wallet in wallets:
            txs = scanner_wallet(wallet)
            for tx in txs:
                tx_id = tx.get('signature')
                if tx_id not in deja_vu:
                    deja_vu.add(tx_id)
                    token_mint = analyser_transaction(tx)
                    
                    if token_mint:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Achat détecté par {wallet[:6]} sur {token_mint}. Vérification...", flush=True)
                        
                        # VÉRIFICATION DU MARCHÉ
                        est_valide, liq, vol = verifier_token_dexscreener(token_mint)
                        
                        if est_valide:
                            msg = f"🚨 SMART MONEY CONVERGENCE 🚨\n"
                            msg += f"👤 Wallet : {wallet[:6]}... a acheté !\n"
                            msg += f"🪙 CA : {token_mint}\n"
                            msg += f"💧 Liquidité : ${liq:,.0f}\n"
                            msg += f"📊 Volume 5m : ${vol:,.0f}\n"
                            msg += f"🔗 https://axiom.trade/token/{token_mint}"
                            
                            print(f"[+] PÉPITE VALIDÉE ! Alerte envoyée.", flush=True)
                            envoyer_alerte(msg)
                        else:
                            print(f"[-] Token ignoré (liquidité/volume insuffisants).", flush=True)
                            
            time.sleep(1) # Pause anti-ban API Helius
            
        time.sleep(15) # Pause avant de rescanner tous les wallets

if __name__ == "__main__":
    main()
