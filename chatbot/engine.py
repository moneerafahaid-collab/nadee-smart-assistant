"""محرك بحث بسيط لمساعد نضيء — يطابق السؤال مع قاعدة المعرفة."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import KnowledgeArticle

ARABIC_STOPWORDS = {
    "من",
    "في",
    "على",
    "إلى",
    "الى",
    "عن",
    "مع",
    "هذا",
    "هذه",
    "ذلك",
    "تلك",
    "ما",
    "ماذا",
    "كيف",
    "هل",
    "و",
    "أو",
    "او",
    "أن",
    "ان",
    "التي",
    "الذي",
    "أريد",
    "اريد",
    "أحتاج",
    "احتاج",
    "رجاء",
    "من فضلك",
    "فضلك",
}


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def stem_token(token: str) -> str:
    """تبسيط خفيف للكلمة العربية لتحسين المطابقة."""
    if token.startswith("ال") and len(token) > 4:
        token = token[2:]
    # تقارب أفعال شائعة: أسجل / تسجيل
    replacements = {
        "اسجل": "تسجيل",
        "سجل": "تسجيل",
        "تسجيل": "تسجيل",
        "ادخل": "دخول",
        "دخول": "دخول",
        "دوره": "تدريب",
        "دورات": "تدريب",
        "تدريبيه": "تدريب",
        "تدريب": "تدريب",
        "مجالات": "مجال",
        "مجال": "مجال",
        "معايير": "معيار",
        "معيار": "معيار",
        "مرفقات": "مرفق",
        "مرفق": "مرفق",
        "وثائق": "وثيقه",
        "نضيء": "نضيء",
        "نضي": "نضيء",
    }
    return replacements.get(token, token)


def tokenize(text: str) -> set[str]:
    tokens = set(normalize(text).split())
    cleaned = set()
    for token in tokens:
        if token in ARABIC_STOPWORDS or len(token) <= 1:
            continue
        cleaned.add(stem_token(token))
    return cleaned


@dataclass
class MatchResult:
    article: KnowledgeArticle | None
    score: float
    answer: str


def score_article(query_tokens: set[str], article: KnowledgeArticle) -> float:
    haystack = " ".join(
        [
            article.title,
            article.content,
            article.keywords,
            article.get_category_display(),
        ]
    )
    article_tokens = tokenize(haystack)
    if not query_tokens or not article_tokens:
        return 0.0

    overlap = query_tokens & article_tokens
    if not overlap:
        # تطابق جزئي للكلمات الأطول
        partial = 0
        for q in query_tokens:
            for a in article_tokens:
                if len(q) >= 3 and (q in a or a in q):
                    partial += 0.35
        return partial

    recall = len(overlap) / len(query_tokens)
    title_tokens = tokenize(article.title)
    title_overlap = query_tokens & title_tokens
    title_bonus = 0.25 * len(title_overlap)
    keyword_tokens = tokenize(article.keywords)
    keyword_overlap = query_tokens & keyword_tokens
    keyword_bonus = 0.4 * len(keyword_overlap)
    # تقليل أثر المقالات العامة التي تشارك فقط كلمات مثل «نضيء» و«منصة»
    generic = {"نضيء", "منصه", "بيانات", "سدايا"}
    distinctive = overlap - generic
    distinctive_bonus = 0.55 * len(distinctive)
    return (recall * 0.55) + title_bonus + keyword_bonus + distinctive_bonus


def answer_question(question: str) -> MatchResult:
    articles = list(KnowledgeArticle.objects.filter(is_active=True))
    if not articles:
        return MatchResult(
            article=None,
            score=0.0,
            answer=(
                "قاعدة المعرفة فارغة حالياً. يرجى إضافة الأدلة والإجراءات من لوحة الإدارة "
                "أو تشغيل أمر تهيئة البيانات التجريبية."
            ),
        )

    query_tokens = tokenize(question)
    ranked: list[tuple[float, KnowledgeArticle]] = []
    for article in articles:
        s = score_article(query_tokens, article)
        if s > 0:
            ranked.append((s, article))

    ranked.sort(key=lambda item: item[0], reverse=True)

    if not ranked or ranked[0][0] < 0.35:
        return MatchResult(
            article=None,
            score=0.0,
            answer=(
                "لم أجد إجابة مباشرة في قاعدة المعرفة المعتمدة من سدايا ومنصة نضيء.\n\n"
                "جرّب صياغة أوضح أو كلمات مثل: تسجيل الدخول، رفع البيانات، "
                "الدورات التدريبية، دليل الجودة، أو إجراءات التصحيح.\n\n"
                "يمكنك أيضاً تصفح قسم قاعدة المعرفة للاطلاع على الأدلة المتاحة."
            ),
        )

    best_score, best = ranked[0]
    extras = []
    for score, article in ranked[1:3]:
        if score >= 0.4:
            extras.append(f"• {article.title}")

    answer = (
        f"**{best.title}**\n\n"
        f"{best.content.strip()}\n\n"
        f"— المصدر: {best.source} | التصنيف: {best.get_category_display()}"
    )
    if extras:
        answer += "\n\nقد يهمك أيضاً:\n" + "\n".join(extras)

    return MatchResult(article=best, score=best_score, answer=answer)
