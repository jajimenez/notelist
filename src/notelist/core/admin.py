from django.contrib import admin

from core.models import Notebook, Tag, Note


admin.site.register(Notebook)
admin.site.register(Tag)
admin.site.register(Note)
