from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import ChatMessage, ChatSession, User
import json
import os
import requests
import uuid

LLM_SERVER_ENDPOINT = os.getenv("LLM_SERVER_ENDPOINT", "http://localhost:8080/wa/get-llm-response")

def get_llm_response(user_message: str, chat_history: list = None) -> str:
    history_text = "\n".join(
        [f"User: {msg['user']}\nBot: {msg['bot']}" for msg in chat_history]
    ) if chat_history else ""

    try:
        response = requests.post(
            LLM_SERVER_ENDPOINT,
            json={
                "prompt": user_message,
                "system_prompt": "",
                "chat_history": history_text
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("text", "Sorry, I had a problem processing that.")
    except Exception as e:
        print(f"LLM Error: {e}")
        return "An error occurred."

def chat_page(request):
    if not request.session.get("user_id"):
        request.session["user_id"] = str(uuid.uuid4())

    user_uuid = request.session["user_id"]
    user, _ = User.objects.get_or_create(uuid=user_uuid)

    session_id = request.session.get("active_session")
    if not session_id:
        session = ChatSession.objects.create(user=user)
        request.session["active_session"] = str(session.id)
    else:
        session = ChatSession.objects.filter(id=session_id, user=user).first()
        if not session:
            session = ChatSession.objects.create(user=user)
            request.session["active_session"] = str(session.id)

    # Fetch all sessions for that user
    sessions = ChatSession.objects.filter(user=user).order_by('-created_at')

    # Get messages for the current session
    messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
    message_list = [{"user": m.message, "bot": m.response} for m in messages]

    theme = request.session.get('theme', 'default')
    return render(request, 'chat/index.html', {
        'theme': theme,
        'messages_json': json.dumps(message_list),
        'sessions': sessions,                     # Add sessions to context
        'active_session_id': session.id           # Mark which one is active
    })

def chat_api(request):
    if request.method == "POST":
        try:
            if not request.session.get("user_id"):
                request.session["user_id"] = str(uuid.uuid4())
            user_uuid = request.session["user_id"]
            user, _ = User.objects.get_or_create(uuid=user_uuid)

            session_id = request.session.get("active_session")
            if not session_id:
                session = ChatSession.objects.create(user=user)
                request.session["active_session"] = str(session.id)
            else:
                session = ChatSession.objects.get(id=session_id, user=user)

            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)
            
            

            history_qs = ChatMessage.objects.filter(session=session).order_by('-timestamp')[:5]
            chat_history = [
                {"user": m.message, "bot": m.response}
                for m in reversed(history_qs)
            ]

            bot_response = get_llm_response(user_message, chat_history)

            ChatMessage.objects.create(
                session=session,
                message=user_message,
                response=bot_response
            )
            

            return JsonResponse({"response": bot_response})
        except Exception as e:
            return JsonResponse({"response": f"Error: {str(e)}"})
    return JsonResponse({"error": "Invalid request method"}, status=405)


def set_theme(request, theme):
    request.session['theme'] = theme
    return redirect('chat:chat_page')

def ask(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            response = get_llm_response(message)
            return JsonResponse({"response": response})
        except Exception as e:
            return JsonResponse({"response": f"Error: {str(e)}"})
    return JsonResponse({"error": "Invalid request method"}, status=405)

def start_new_chat(request):
    user_uuid = request.session.get("user_id")
    if not user_uuid:
        return redirect("chat:chat_page")

    user = User.objects.get(uuid=user_uuid)
    new_session = ChatSession.objects.create(user=user)
    request.session["active_session"] = str(new_session.id)

    return redirect("chat:chat_page")

@require_POST
def switch_session(request, session_id):
    user_uuid = request.session.get("user_id")
    if not user_uuid:
        return redirect("chat:chat_page")

    try:
        user = User.objects.get(uuid=user_uuid)
        session = ChatSession.objects.get(id=session_id, user=user)
        request.session["active_session"] = str(session.id)
    except ChatSession.DoesNotExist:
        pass  # silently ignore if session is invalid

    return redirect("chat:chat_page")

@require_POST
def delete_session(request, session_id):
    user_uuid = request.session.get("user_id")
    if not user_uuid:
        return redirect("chat:chat_page")

    try:
        user = User.objects.get(uuid=user_uuid)
        session = ChatSession.objects.get(id=session_id, user=user)
        session.delete()
    except ChatSession.DoesNotExist:
        pass

    return redirect("chat:chat_page")
