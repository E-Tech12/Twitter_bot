from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import random
import requests

from plyer import notification
import webbrowser
import pyperclip
from datetime import datetime, timezone

# ==================TELEGRAM CONFIG ==================
BOT_TOKEN = "8781321070:AAH_XYQNtm9ZTYaV1_QfsMcneQBVFebuGZw"
CHAT_ID = "8519082585"

# ================== CONFIG ==================
SEARCH_URL = "https://x.com/search?q=(\"pay dex\" OR \"cto\" OR \"cto this\" OR \"dex\") lang:en -filter:replies&f=live"

KEYWORDS = ["dex", "cto"]

STRONG_WORDS = ["ca", "contract", "launch", "live", "pair", "liquidity"]

BAD_WORDS = ["giveaway", "airdrop", "promo", "win", "follow"]

AUTO_OPEN_STRONG = True
MAX_TWEET_AGE = 300   # 🔥 5 minutes

# ================== CONNECT ==================
options = Options()
options.debugger_address = "127.0.0.1:9222"

driver = webdriver.Chrome(options=options)
print("✅ Connected to Chrome")

driver.get(SEARCH_URL)
time.sleep(5)

seen = set()
loop_count = 0

# ================== ALERT ==================
def send_alert(text, url, age):
    notification.notify(
        title="🚨 DEX/CTO SIGNAL",
        message=f"{text[:100]}\n⏱️ {age}s ago",
        timeout=6
    )

    pyperclip.copy(url)
    print(f"📋 Copied: {url}")

    if AUTO_OPEN_STRONG and any(w in text for w in STRONG_WORDS):
        webbrowser.open(url)


def send_telegram_alert(text, url, age):
    message = f"""🚨 DEX/CTO SIGNAL

{text[:150]}

⏱️ {age}s ago
🔗 {url}
"""

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message
            }
        )
    except Exception as e:
        print("⚠️ Telegram error:", e)

# ================== FILTER ==================
def is_good_tweet(text):
    text = text.lower()

    if not any(k in text for k in KEYWORDS):
        return False

    if any(b in text for b in BAD_WORDS):
        return False

    if len(text) < 25 or len(text) > 200:
        return False

    return True


# ================== MAIN LOOP ==================
while True:
    loop_count += 1

    # 🔥 SMOOTH SCROLL
    driver.execute_script("window.scrollBy(0, 700);")
    time.sleep(random.randint(2, 4))

    tweets = driver.find_elements(By.XPATH, "//article")[:8]  # 🔥 focus on latest
    print(f"👀 Tweets (top): {len(tweets)} | Loop: {loop_count}")

    new_found = False

    for tweet in tweets:
        try:
            text = tweet.text.lower()

            if "replying to" in text:
                continue

            if not is_good_tweet(text):
                continue

            # ================== TIME FILTER ==================
            try:
                time_elem = tweet.find_element(By.XPATH, './/time')
                tweet_time = time_elem.get_attribute("datetime")

                tweet_dt = datetime.fromisoformat(tweet_time.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)

                diff = int((now - tweet_dt).total_seconds())

                # ✅ ONLY rule: must be within 5 minutes
                if diff > 300:
                    continue

            except:
                continue

            # ================== GET URL ==================
            try:
                link = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                url = link.get_attribute("href")
            except:
                continue

            tweet_id = url

            if tweet_id in seen:
                continue

            seen.add(tweet_id)
            new_found = True

            print(f"\n🔥 NEW SIGNAL ({diff}s):", text[:100])

            # ================== ALERT ==================
            send_alert(text, url, diff)
            send_telegram_alert(text, url, diff)

            time.sleep(random.randint(2, 5))

        except:
            continue

    # ================== LOOP CONTROL ==================
    if not new_found:
        print("😴 No new signals → slight scroll...")
        driver.execute_script("window.scrollBy(0, 400);")

    # 🔥 LESS FREQUENT HARD REFRESH
    if loop_count % 20 == 0:
        print("🔄 Hard refresh...")
        driver.refresh()
        time.sleep(5)

    time.sleep(3)