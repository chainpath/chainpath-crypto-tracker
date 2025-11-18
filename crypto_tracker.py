import requests
import time
import os
from datetime import datetime

# Webhook URL dari Discord - GANTI INI!
WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL', 'YOUR_WEBHOOK_URL_HERE')

# Coins yang mau di-track (bisa ditambah sesuai kebutuhan)
COINS = ["bitcoin", "ethereum", "solana", "binancecoin", "cardano"]

# Update interval dalam detik (default: 15 menit = 900 detik)
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', '900'))

def get_crypto_prices():
    """Fetch prices dari CoinGecko API (FREE, no API key needed!)"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ",".join(COINS),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
            "include_24hr_vol": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching prices: {e}")
        return None

def format_message(data):
    """Format message untuk Discord dengan style professional"""
    if not data:
        return None
    
    # Header dengan timestamp
    message = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "📊 **CRYPTO MARKET UPDATE**\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    message += f"```\n"
    message += f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
    
    # Sort coins by market cap (descending)
    sorted_coins = sorted(
        data.items(), 
        key=lambda x: x[1].get('usd_market_cap', 0), 
        reverse=True
    )
    
    # Coin data dengan formatting yang rapi
    for coin_id, info in sorted_coins:
        price = info.get('usd', 0)
        change_24h = info.get('usd_24h_change', 0)
        market_cap = info.get('usd_market_cap', 0)
        volume_24h = info.get('usd_24h_vol', 0)
        
        # Emoji indicator based on price change
        if change_24h >= 5:
            emoji = "🚀"
        elif change_24h >= 0:
            emoji = "🟢"
        elif change_24h >= -5:
            emoji = "🔴"
        else:
            emoji = "💥"
        
        # Format coin name
        coin_name = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "solana": "SOL",
            "binancecoin": "BNB",
            "cardano": "ADA"
        }.get(coin_id, coin_id.upper())
        
        message += f"{emoji} {coin_name}\n"
        message += f"  💰 ${price:,.2f}\n"
        message += f"  📈 {change_24h:+.2f}% (24h)\n"
        message += f"  📊 MCap: ${market_cap/1e9:.2f}B\n"
        message += f"  💹 Vol: ${volume_24h/1e6:.1f}M\n\n"
    
    message += "```\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return message

def send_to_discord(message):
    """Send message ke Discord webhook"""
    try:
        data = {
            "content": message,
            "username": "Chainpath Price Tracker",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/6001/6001368.png"
        }
        
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        
        if response.status_code == 204:
            print(f"✅ Message sent successfully at {datetime.utcnow().strftime('%H:%M:%S')} UTC")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending to Discord: {e}")
        return False

def health_check():
    """Simple health check endpoint simulation"""
    return True

def main():
    """Main loop - runs continuously"""
    print("=" * 50)
    print("🚀 CHAINPATH CRYPTO PRICE TRACKER")
    print("=" * 50)
    print(f"📍 Tracking: {', '.join(COINS)}")
    print(f"⏱️  Update interval: {UPDATE_INTERVAL // 60} minutes")
    print(f"🔗 Webhook configured: {'Yes' if WEBHOOK_URL != 'YOUR_WEBHOOK_URL_HERE' else 'No'}")
    print("=" * 50)
    print()
    
    if WEBHOOK_URL == 'YOUR_WEBHOOK_URL_HERE':
        print("⚠️  WARNING: Please set DISCORD_WEBHOOK_URL environment variable!")
        print("Continuing anyway for testing purposes...\n")
    
    iteration = 0
    
    while True:
        try:
            iteration += 1
            print(f"\n🔄 Update #{iteration} - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            # Fetch prices from CoinGecko
            print("📡 Fetching prices from CoinGecko API...")
            prices = get_crypto_prices()
            
            if prices:
                print(f"✅ Retrieved data for {len(prices)} coins")
                
                # Format message
                message = format_message(prices)
                
                if message:
                    # Send to Discord
                    if send_to_discord(message):
                        print("✅ Update posted to Discord successfully!")
                    else:
                        print("⚠️  Failed to post to Discord")
                else:
                    print("⚠️  Failed to format message")
            else:
                print("⚠️  No price data retrieved")
            
            # Wait for next update
            next_update = datetime.fromtimestamp(time.time() + UPDATE_INTERVAL)
            print(f"⏸️  Next update at: {next_update.strftime('%H:%M:%S')} UTC")
            print(f"💤 Sleeping for {UPDATE_INTERVAL // 60} minutes...")
            
            time.sleep(UPDATE_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n👋 Bot stopped by user (Ctrl+C)")
            print("Shutting down gracefully...")
            break
            
        except Exception as e:
            print(f"\n❌ Unexpected error in main loop: {e}")
            print("⏳ Waiting 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    main()