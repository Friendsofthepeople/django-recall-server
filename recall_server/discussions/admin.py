from django.contrib import admin

from recall_server.discussions.models import Post, Response


admin.site.register(Post)
admin.site.register(Response)
