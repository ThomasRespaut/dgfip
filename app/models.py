import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from llama_cpp import Llama
from mistralai import Mistral
from dotenv import load_dotenv
import markdown
load_dotenv()

class ChatbotService:
    def __init__(self, local: bool = False):
        """
        Initialise le service de chatbot.
        :param local: Si True, utilise le modèle local quantifié. Sinon, utilise l'API Mistral en ligne via le client mistralai.
        """
        print(f"\n🟡 Initialisation du ChatbotService en mode {'local' if local else 'online'}...")
        self.local = local
        self.embedding_model = None
        self.df_info = None
        self.embeddings = None
        self.llm_local = None
        self.api_client = None
        # Historique des messages pour le mode online
        self.messages = [
            {"role": "system", "content": "Tu es un assistant fiscal expert de la DGFiP."}
        ]
        self.load_data_and_embeddings()
        if self.local:
            self.load_mistral_quantized()
        else:
            self.load_mistral_api_client()
        print("✅ ChatbotService initialisé.\n")

    def load_data_and_embeddings(self):
        print("🔹 Chargement de la base CSV...")
        self.df_info = pd.read_csv("info_particulier_impot.csv")
        print(f"✅ {len(self.df_info)} entrées chargées.")

        print("🔹 Chargement du modèle d'embedding...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Modèle d'embedding chargé.")

        cache = "embeddings_cache.npy"
        if os.path.exists(cache):
            self.embeddings = np.load(cache)
            print("✅ Embeddings chargés depuis le cache.")
        else:
            print("🔄 Génération des embeddings...")
            texts = self.df_info['Texte'].fillna('').tolist()
            self.embeddings = self.embedding_model.encode(texts)
            np.save(cache, self.embeddings)
            print("✅ Embeddings générés et sauvegardés.")

    def load_mistral_quantized(self):
        from huggingface_hub import hf_hub_download
        repo, fname = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF", "mistral-7b-instruct-v0.1.Q5_K_M.gguf"
        local_dir = "./models/mistral-7b-q5"
        os.makedirs(local_dir, exist_ok=True)
        path = os.path.join(local_dir, fname)
        if not os.path.exists(path):
            print("⬇️ Téléchargement du modèle depuis Hugging Face...")
            path = hf_hub_download(repo, fname, local_dir=local_dir, local_dir_use_symlinks=False)
        print(f"✅ Modèle local prêt : {path}")
        print("🚀 Chargement du modèle local avec llama.cpp...")
        self.llm_local = Llama(model_path=path, n_ctx=2048)
        print("✅ Modèle quantifié chargé.")

    def load_mistral_api_client(self):
        print("🌐 Initialisation du client Mistral AI en ligne...")
        api_key = os.getenv('MISTRAL_API_KEY')
        if not api_key:
            raise EnvironmentError("Clé API MISTRAL_API_KEY introuvable dans l'environnement")
        self.api_client = Mistral(api_key=api_key)
        print("✅ Client Mistral API prêt.")

    def find_relevant_context(self, question: str, top_k: int = 3):
        q_emb = self.embedding_model.encode([question])
        sims = cosine_similarity(q_emb, self.embeddings)[0]
        idxs = np.argsort(sims)[-top_k:][::-1]
        return [
            {'Texte': self.df_info.iloc[i]['Texte'], 'score': float(sims[i])}
            for i in idxs if sims[i] > 0.3
        ]

    def generate_response(self, question: str) -> str:
        """Retourne la réponse HTML convertie depuis Markdown et gère l'historique"""
        context = self.find_relevant_context(question)
        prompt = self.build_prompt(question, context)
        if self.local:
            raw = self._generate_local(prompt)
        else:
            # Ajout de la requête utilisateur à l'historique
            self.messages.append({"role": "user", "content": prompt})
            raw = self._generate_online()
            # Ajout de la réponse de l'assistant à l'historique
            self.messages.append({"role": "assistant", "content": raw})
        # Conversion Markdown -> HTML pour CSS (titres, gras, listes...)
        html = markdown.markdown(raw, extensions=['extra', 'smarty'])
        return html

    def _generate_local(self, prompt: str) -> str:
        out = self.llm_local(prompt, max_tokens=200)
        return out['choices'][0]['text'].strip()

    def _generate_online(self) -> str:
        response = self.api_client.chat.complete(
            model="mistral-large-latest",
            messages=self.messages,
            temperature=0.2,
            top_p=1.0,
            safe_prompt=True,
            n=1
        )
        return response.choices[0].message.content.strip()

    def build_prompt(self, question: str, context: list) -> str:
        ctx = "\n".join([c['Texte'] for c in context])
        # On conserve les # pour conversion Markdown -> HTML
        return f"# Contexte pertinent:\n{ctx}\n\n# Question:\n{question}"
