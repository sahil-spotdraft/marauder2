from django.contrib import admin
from .models import ChatHistory, UserSession

admin.site.register(ChatHistory)
admin.site.register(UserSession)