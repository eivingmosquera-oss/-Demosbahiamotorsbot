import os
import requests
from flask import Flask, request, jsonify
from groq import Groq

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

client = Groq(api_key=GROQ_API_KEY)

# Inventario de demos (luego conectamos con Google Sheets)
INVENTARIO = """
• Geely Coolray (AB-1234) — Blanco — Sucursal: RJA — Responsable: Carlos Méndez — Estado: Disponible
• Geely Emgrand (CD-5678) — Gris — Sucursal: C50 — Responsable: Ana Torres — Estado: En préstamo
• Geely Tugella (EF-9012) — Negro — Sucursal: Chorrera — Responsable: Luis Ríos — Estado: En taller
• Geely Okavango (GH-3456) — Azul — Sucursal: Costa del Este — Responsable: María Solis — Estado: Disponible
• Geely Coolray (IJ-7890) — Rojo — Sucursal: C50 — Responsable: Pedro Núñez — Estado: En préstamo
• Geely Monjaro (KL-1122) — Blanco — Sucursal: RJA — Responsable: Sofia Vargas — Estado: Disponible
"""

SYSTEM_PROMPT = f"""Eres DemoBot, asistente interno de Bay Motors (Geely Panama).
Respondes preguntas sobre autos demo de forma breve y directa para el equipo de ventas.
Usa emojis ocasionalmente. Si listas autos, usa viñetas simples.
Sucursales activas: RJA, C50, Chorrera, Costa del Este.

Inventario actual:
{INVENTARIO}"""


def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    })


def ask_groq(user_message):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        max_tokens=400,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id,
                "👋 ¡Hola! Soy el asistente de demos de *Bay Motors*.\n\n"
                "Puedes preguntarme:\n"
                "• ¿Dónde está el Coolray?\n"
                "• ¿Qué demos hay disponibles?\n"
                "• ¿Qué hay en RJA?\n\n"
                "¿En qué te puedo ayudar?"
            )
        elif text:
            respuesta = ask_groq(text)
            send_message(chat_id, respuesta)

    return jsonify({"ok": True})


@app.route("/", methods=["GET"])
def index():
    return "DemoBot Bay Motors - Activo ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
