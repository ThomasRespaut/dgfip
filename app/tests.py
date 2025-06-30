import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# Paramètres
repo_id = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
filename = "mistral-7b-instruct-v0.1.Q5_K_M.gguf"
local_dir = "./models/mistral-7b-q5"
local_path = os.path.join(local_dir, filename)

print("📦 Initialisation du chargement du modèle Mistral-7B quantisé (Q5_K_M)")

# Étape 1 : Créer le dossier local si besoin
if not os.path.exists(local_dir):
    print(f"📁 Création du dossier local : {local_dir}")
    os.makedirs(local_dir)

# Étape 2 : Vérifier la présence du fichier local
if not os.path.exists(local_path):
    print("❌ Modèle non trouvé localement.")
    print("⬇️ Téléchargement depuis Hugging Face...")
    model_path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=local_dir,
        local_dir_use_symlinks=False
    )
    print(f"✅ Modèle téléchargé et stocké dans : {model_path}")
else:
    print(f"✅ Modèle déjà présent localement à : {local_path}")
    model_path = local_path

# Étape 3 : Chargement du modèle avec llama.cpp
print("🚀 Chargement du modèle avec llama.cpp...")
llm = Llama(
    model_path=model_path,
    n_ctx=2048
)
print("✅ Modèle prêt à l'utilisation.")

# Étape 4 : Prompt de test
prompt = "[INST] Explique-moi le machine learning en deux phrases. [/INST]"
print("\n🧠 Génération de réponse...")
output = llm(prompt, max_tokens=200)

# Résultat
print("\n🎯 Réponse générée :\n")
print(output["choices"][0]["text"])
