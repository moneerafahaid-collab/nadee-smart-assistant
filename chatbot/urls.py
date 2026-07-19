from django.urls import path

from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_home, name="home"),
    path("send/", views.send_message, name="send"),
    path("knowledge/", views.knowledge_list, name="knowledge"),
    path("knowledge/<int:pk>/", views.knowledge_detail, name="knowledge_detail"),
]
