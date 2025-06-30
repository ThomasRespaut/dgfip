# Mini-chatbot DGFiP

Ce dépôt contient un prototype de mini-chatbot « FAQ » pour la DGFiP (Direction Générale des Finances Publiques). L'objectif est de répondre à des questions d’usagers en proposant la fiche pratique la plus pertinente depuis le site impots.gouv.

## 📋 Contenu du dépôt

* **`info_particulier_impot.csv`** : base documentaire de 113 fiches pratiques issues de l’espace particulier du site impots.gouv.
* **`questions_fiches_fip.csv`** : jeu de questions fictives et fichier associé attendu (utilisé pour évaluation).
* **`app/models.py`** : implémentation de la classe `ChatbotService`, gérant le RAG (retrieval-augmented generation) local ou via API Mistral.
* **`requirements.txt`** : liste des dépendances Python.
* **`.env.example`** : exemple de variables d’environnement (clé MISTRAL\_API\_KEY, etc.).

## ⚙️ Installation

1. **Cloner le dépôt**

   ```bash
   git clone git@github.com:ThomasRespaut/dgfip.git
   cd dgfip
   ```

2. **Créer et activer un environnement virtuel**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .\.venv\Scripts\activate pour Windows
   ```

3. **Installer les dépendances**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configurer les variables d’environnement**

   * Dupliquer `.env.example` en `.env`.
   * Remplir `MISTRAL_API_KEY` avec votre clé Mistral AI.
   * (Optionnel) autres variables si nécessaire.

## 🚀 Usage

### 1. Mode local (quantifié)

```python
from app.models import ChatbotService
service = ChatbotService(local=True)
print(service.generate_response("Comment déclarer mes impôts ?"))
```

### 2. Mode online (API Mistral)

```python
from app.models import ChatbotService
service = ChatbotService(local=False)
print(service.generate_response("Comment déclarer mes impôts ?"))
```

Le résultat renvoyé est du HTML généré depuis du Markdown, prêt à être stylé avec votre CSS (titres, gras, listes, etc.).

## 🧠 Fonctionnement interne

1. **Récupération du contexte** : on encode les fiches pratiques et la question avec SentenceTransformer, puis on sélectionne les `top_k` textes les plus similaires.
2. **Construction du prompt** : on formate la question et le contexte en Markdown.
3. **Génération de la réponse** :

   * **Local** : modèle quantifié Mistral 7B via `llama.cpp`.
   * **Online** : appel à l’API Mistral AI avec historique conversationnel (`self.messages`).
4. **Conversion Markdown → HTML** : utilisation de la lib `markdown` pour produire un HTML stylable.

## 💡 Idées d’amélioration

* **Mise en cache plus fine** des embeddings ou des réponses fréquentes.
* **Filtres de sécurité** et nettoyage XSS sur le HTML.
* **Déploiement** : packager en microservice (FastAPI + Gunicorn/Uvicorn), conteneur Docker.
* **Scalabilité** : passer sur un vector database (Pinecone, Weaviate…) pour des recherches à grande échelle.
* **Monitoring** : mettre en place des métriques (temps de réponse, qualité, logs).
* **Interface utilisateur** : front React/Vue simple pour interagir en temps réel.

## 📜 Licence

Ce projet est proposé sans licence particulière. À adapter selon les règles internes de la DGFiP.

---

*Pour toute question, contactez :*
[hermann.woehrel@dgfip.finances.gouv.fr](mailto:hermann.woehrel@dgfip.finances.gouv.fr)
[titouan.blaize@dgfip.finances.gouv.fr](mailto:titouan.blaize@dgfip.finances.gouv.fr)
[adrien.benamira-carrie@dgfip.finances.gouv.fr](mailto:adrien.benamira-carrie@dgfip.finances.gouv.fr)
