import os
import requests

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")

GRAPH_URL = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"


def send_list(to, body_text, button_text, sections):

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": body_text
            },
            "action": {
                "button": button_text,
                "sections": sections
            }
        }
    }

    response = requests.post(GRAPH_URL, headers=headers, json=payload)

    return response


def send_text(to, message):

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }

    response = requests.post(GRAPH_URL, headers=headers, json=payload)

    return response


def send_buttons(to, body_text, buttons):

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body_text
            },
            "action": {
                "buttons": buttons
            }
        }
    }

    response = requests.post(GRAPH_URL, headers=headers, json=payload)

    return response
