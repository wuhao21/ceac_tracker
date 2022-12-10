from discord import SyncWebhook

def send_notification(message):
    webhook_url = "https://discord.com/api/webhooks/1050960338562064447/u8sS-RK6qt4fGolvQh0ADuusGmhzbRHnHyuYiOrmzgTdG0nNADJE2wTF-RsZ_O2MhkCg"
    webhook = SyncWebhook.from_url(webhook_url)
    webhook.send(message)
