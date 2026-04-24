import requests

token = "8742024229:AAHgXkal4aE9gnJmzkBeJZ0yqkDGcPVRWVk"
chat_id = "8047086065"

msg = "🚀 Teste de notificação funcionando!"

url = f"https://api.telegram.org/bot{token}/sendMessage"

requests.post(url, json={
    "chat_id": chat_id,
    "text": msg
})
