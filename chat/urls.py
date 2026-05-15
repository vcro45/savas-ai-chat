from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_page, name='chat_page'),                   # Main chat page
    path('api/chat/', views.chat_api, name='chat_api'),            # Backend API endpoint for chatting
    path('ask/', views.ask, name='ask'),                           # Ask a question (UI)
    path('set-theme/<str:theme>/', views.set_theme, name='set_theme'),
    path("switch/<int:session_id>/", views.switch_session, name="switch_session"),
    path('new/', views.start_new_chat, name='start_new_chat'),  # Theme switching (UI)
    path('delete_session/<int:session_id>/', views.delete_session, name='delete_session'),
]
