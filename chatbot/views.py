import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_POST

from .engine import answer_question
from .models import ChatMessage, ChatSession, KnowledgeArticle


@login_required
def chat_home(request):
    session = ChatSession.objects.filter(user=request.user).order_by("-updated_at").first()
    if not session:
        session = ChatSession.objects.create(
            user=request.user, title="محادثة المساعد"
        )
    messages = session.messages.select_related("related_article")
    categories = KnowledgeArticle.Category.choices
    articles = KnowledgeArticle.objects.filter(is_active=True)[:8]
    return render(
        request,
        "chatbot/chat.html",
        {
            "session": session,
            "messages": messages,
            "categories": categories,
            "sample_articles": articles,
        },
    )


@login_required
@require_POST
def send_message(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "طلب غير صالح"}, status=400)

    text = (payload.get("message") or "").strip()
    if not text:
        return JsonResponse({"ok": False, "error": "الرسالة فارغة"}, status=400)

    session_id = payload.get("session_id")
    if session_id:
        session = get_object_or_404(ChatSession, pk=session_id, user=request.user)
    else:
        session = ChatSession.objects.create(user=request.user, title=text[:60])

    ChatMessage.objects.create(
        session=session, role=ChatMessage.Role.USER, content=text
    )

    result = answer_question(text)
    assistant_msg = ChatMessage.objects.create(
        session=session,
        role=ChatMessage.Role.ASSISTANT,
        content=result.answer,
        related_article=result.article,
    )
    session.title = text[:60]
    session.save(update_fields=["title", "updated_at"])

    return JsonResponse(
        {
            "ok": True,
            "session_id": session.id,
            "user_message": text,
            "assistant_message": assistant_msg.content,
            "article_id": result.article.id if result.article else None,
            "score": round(result.score, 2),
        }
    )


@login_required
@require_GET
def knowledge_list(request):
    category = request.GET.get("category", "")
    q = request.GET.get("q", "").strip()
    articles = KnowledgeArticle.objects.filter(is_active=True)
    if category:
        articles = articles.filter(category=category)
    if q:
        articles = articles.filter(title__icontains=q) | articles.filter(
            content__icontains=q
        )
    return render(
        request,
        "chatbot/knowledge.html",
        {
            "articles": articles.distinct(),
            "categories": KnowledgeArticle.Category.choices,
            "selected_category": category,
            "q": q,
        },
    )


@login_required
@require_GET
def knowledge_detail(request, pk):
    article = get_object_or_404(KnowledgeArticle, pk=pk, is_active=True)
    return render(request, "chatbot/knowledge_detail.html", {"article": article})
