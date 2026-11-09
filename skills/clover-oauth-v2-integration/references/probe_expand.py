# READ-ONLY probe. Asks Clover for ONE payment with each expansion alone. Prints HTTP status and Clover's short error text only.
# The OAuth token is held in memory and never printed or logged.
import asyncio, os, re, sys
os.chdir('/home/ec2-user/app/backend'); sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')
import requests
from app.database.connection import init_db_pool, close_db_pool, get_db_pool
from app.services.clover_oauth_config import load_clover_oauth_secrets
from app.services.clover_oauth_service import CloverOAuthService
from app.services.clover_oauth_store import PostgresCredentialStore

MERCHANT = sys.argv[1]; PAYMENT = sys.argv[2]
FIELDS = ("additionalCharges,appTracking,authorizations,cardTransaction,customers,dccInfo,employee,lineItemPayments,"
          "oceanGatewayInfo,order,purchaseCardL2,refunds.employee,refunds.additionalCharges,serviceCharge,taxRates,tender,"
          "transactionInfo,paymentAttributes,incrementalAuthorizations,threeds,fxInfo,metadata,achTransaction,splitShipment,"
          "batchInfo,refunds.cardTransaction").split(",")

def short(r):
    t = re.sub(r'[A-Za-z0-9_\-]{24,}', '***', (r.text or '')[:110]).replace('\n', ' ')
    return f"{r.status_code} {t}"

async def main():
    await init_db_pool()
    try:
        broker = CloverOAuthService(store=PostgresCredentialStore(get_db_pool()), secrets=load_clover_oauth_secrets())
        token = await broker.get_access_token(MERCHANT)
    finally:
        await close_db_pool()
    h = {"Authorization": f"Bearer {token}"}
    base = f"https://api.ap.clover.com/v3/merchants/{MERCHANT}"
    print("payment, no expand      :", short(requests.get(f"{base}/payments/{PAYMENT}", headers=h, timeout=30)))
    print("payments list (limit 1) :", short(requests.get(f"{base}/payments", headers=h, params={"limit": 1}, timeout=30)))
    print("ALL expansions together :", short(requests.get(f"{base}/payments/{PAYMENT}", headers=h, params={"expand": ",".join(FIELDS)}, timeout=30)))
    bad = []
    for f in FIELDS:
        r = requests.get(f"{base}/payments/{PAYMENT}", headers=h, params={"expand": f}, timeout=30)
        if r.status_code != 200:
            bad.append(f); print(f"  expand={f:28s}:", short(r))
    print("expansions refused:", bad or "none")
    print("expansions OK:", [f for f in FIELDS if f not in bad])

asyncio.run(main())
