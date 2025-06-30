import os
import json
from mistralai import Mistral
import requests
from dotenv import load_dotenv
load_dotenv()

# 1. Vérification de la clé API
api_key = os.getenv("MISTRAL_API_KEY")
print("🔑 MISTRAL_API_KEY détectée :", "✅" if api_key else "❌ (inexistante)")

# 2. Initialisation du client
try:
    client = Mistral(api_key=api_key)
    print("🚀 Client Mistral initialisé.")
except Exception as e:
    print("❌ Erreur init client Mistral :", e)
    raise

# 3. Test des embeddings
model_embed = "mistral-embed"
texts = ["Embed this sentence.", "As well as this one."]
print(f"\n📦 Envoi d'une requête embeddings ({model_embed}) pour {len(texts)} textes...")
try:
    emb_resp = client.embeddings.create(model=model_embed, inputs=texts)
    print("✅ Embeddings reçus.")
    print("ℹ️ Usage :", emb_resp.usage)
    for i, item in enumerate(emb_resp.data):
        print(f" • Embedding[{i}] dimension :", len(item.embedding))
except requests.HTTPError as http_err:
    print("❌ HTTPError embeddings :", http_err)
    print("   status_code:", http_err.response.status_code)
    print("   body      :", http_err.response.text)
except Exception as e:
    print("❌ Autre erreur embeddings :", e)

# 4. Test du chat
model_chat = "mistral-large-latest"
messages = [
    {"role": "system", "content": "Tu es un assistant fiscal expert de la DGFiP."},
    {"role": "user", "content": "What is the best French cheese?"},
]
print(f"\n💬 Envoi d'une requête chat ({model_chat}) avec {len(messages)} messages...")
try:
    chat_resp = client.chat.complete(
        model=model_chat,
        messages=messages,
        temperature=0.2,
        top_p=1.0,
        n=1
    )
    print("✅ Réponse chat brute :", json.dumps(chat_resp.choices, default=lambda o: o.__dict__, indent=2))
    print("💡 Contenu :", chat_resp.choices[0].message.content)
except requests.HTTPError as http_err:
    print("❌ HTTPError chat :", http_err)
    print("   status_code:", http_err.response.status_code)
    print("   body      :", http_err.response.text)
except Exception as e:
    print("❌ Autre erreur chat :", e)
