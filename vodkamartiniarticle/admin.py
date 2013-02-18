from django.contrib import admin
from vodkamartiniarticle.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created', 'updated')
    list_filter = ['created']
    search_fields = ['title']
    prepopulated_fields = {"slug": ("title", )}
    raw_id_fields = ('author',)

admin.site.register(Article, ArticleAdmin)

# This may be needed for a quick look at permissions
#from django.contrib.auth.models import Permission
#admin.site.register(Permission)
