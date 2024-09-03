from django.contrib import admin

from recall_server.voting.models import OfficialVote, PublicVote


admin.site.register(OfficialVote)
admin.site.register(PublicVote)
