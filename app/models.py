import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import markdown  # conversion Markdown -> HTML
from mistralai import Mistral
from dotenv import load_dotenv
load_dotenv()

class ChatbotService:
    def __init__(self):
        """
        Initialise le service de chatbot en mode 'online' via l'API Mistral.
        """
        print("\n🟡 Initialisation du ChatbotService (mode online via API Mistral)...")
        self.df_info = None
        self.embeddings = None
        self.api = None
        self.messages = [
            {"role": "system", "content": "Tu es un assistant fiscal expert de la DGFiP."}
        ]

        self._init_api_client()
        self._load_knowledge_base()
        print("✅ ChatbotService initialisé.\n")

    def _init_api_client(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        print("🔑 MISTRAL_API_KEY détectée :", bool(api_key))
        if not api_key:
            raise EnvironmentError("Clé API MISTRAL_API_KEY introuvable dans l'environnement")
        self.api = Mistral(api_key=api_key)
        print("🚀 Client Mistral API prêt.")

    def _load_knowledge_base(self):
        print("🔹 Chargement du fichier CSV de connaissance...")
        root = os.path.dirname(os.path.abspath(__file__))
        path_csv = os.path.join(root, "info_particulier_impot.csv")
        self.df_info = pd.read_csv(path_csv)
        print(f"✅ {len(self.df_info)} lignes chargées depuis {path_csv}")

        cache = os.path.join(root, "embeddings_cache.npy")
        if os.path.exists(cache):
            self.embeddings = np.load(cache)
            print("📥 Embeddings docs chargés depuis le cache.")
            return

        textes = self.df_info["Texte"].fillna("").tolist()
        print(f"🔄 Génération de {len(textes)} embeddings via l'API Mistral (batch)...")
        all_embs = []
        batch_size = 10  # plus petit lot pour éviter trop de tokens
        for start in range(0, len(textes), batch_size):
            end = min(start + batch_size, len(textes))
            batch = textes[start:end]
            print(f"  • Embedding batch {start}-{end-1} ({len(batch)} textes)…")
            try:
                resp = self.api.embeddings.create(
                    model="mistral-embed",
                    inputs=batch
                )
            except Exception as e:
                print(f"❌ Erreur API embeddings batch {start}-{end-1}:", e)
                raise
            for item in resp.data:
                all_embs.append(np.array(item.embedding, dtype=np.float32))

        self.embeddings = np.vstack(all_embs)
        np.save(cache, self.embeddings)
        print(f"✅ Embeddings générés ({len(all_embs)} vecteurs) et mis en cache dans {cache}")

    def _embed_query(self, query: str) -> np.ndarray:
        print(f"🔍 Embedding de la requête : « {query} »")
        try:
            resp = self.api.embeddings.create(model="mistral-embed", inputs=[query])
            return np.array(resp.data[0].embedding, dtype=np.float32).reshape(1, -1)
        except Exception as e:
            print("❌ Erreur embedding question:", e)
            raise

    def _retrieve_context(self, query: str, top_k: int = 3):
        q_emb = self._embed_query(query)
        sims = cosine_similarity(q_emb, self.embeddings)[0]
        idxs = np.argsort(sims)[-top_k:][::-1]
        ctxs = [
            {"Texte": self.df_info.iloc[i]["Texte"], "score": float(sims[i])}
            for i in idxs if sims[i] > 0.3
        ]
        print(f"✅ {len(ctxs)} contextes retenus (seuil 0.3).")
        return ctxs

    def _call_chat_api(self):
        try:
            resp = self.api.chat.complete(
                model="mistral-large-latest",
                messages=self.messages,
                temperature=0.2,
                top_p=1.0,
                max_tokens=200,
                n=1
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print("❌ Erreur API chat.complete:", e)
            raise

    def ask(self, question: str) -> str:
        """
        Pose une question au chatbot, renvoie la réponse formatée en HTML.
        """
        print(f"\n📨 Question reçue : « {question} »")
        context = self._retrieve_context(question)
        prompt = (
            "# Contexte pertinent :\n"
            + "\n\n".join([c["Texte"] for c in context])
            + f"\n\n# Question :\n{question}"
        )
        print("✍️ Prompt Markdown construit.")
        self.messages.append({"role": "user", "content": prompt})

        raw = self._call_chat_api()
        print("ℹ️ Réponse brute reçue.")
        self.messages.append({"role": "assistant", "content": raw})

        html = markdown.markdown(raw, extensions=["extra", "smarty"])
        print("✅ Conversion en HTML effectuée.")
        return html

    def generate_response(self, question: str) -> str:
        """
        Wrapper pour compatibilité avec la vue existante.
        """
        return self.ask(question)
