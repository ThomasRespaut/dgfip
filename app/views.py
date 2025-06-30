from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import ChatbotService

def index(request):
    return render(request, 'app/index.html')

chatbot = ChatbotService()  # Chargé une fois

@csrf_exempt
def chat_view(request):
    if request.method != "POST":
        print("❌ Requête non POST reçue.")
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()
        print(f"📨 Requête reçue : {message}")

        if not message:
            print("⚠️ Message vide.")
            return JsonResponse({'success': False, 'error': 'Message vide'})

        response = chatbot.generate_response(message)
        if not response:
            print("❌ Échec génération de réponse.")
            return JsonResponse({'success': False, 'error': "Erreur lors de la génération de la réponse."})

        print("✅ Réponse complète envoyée au frontend.")
        return JsonResponse({
            'success': True,
            'response': response,
            'source': 'mistral_rag',
        })

    except Exception as e:
        print(f"❌ Exception dans la vue : {e}")
        return JsonResponse({'success': False, 'error': str(e)})
