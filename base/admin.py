from django.contrib import admin
from .models import Group, Topic, User, Profile, Message, Exercise, ExerciseByPerson, Routine, Article, ArticleComment

class RoutineAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'user')
    list_filter = ('date',)

# Register your models here.
admin.site.register(Group)
admin.site.register(Topic)
admin.site.register(Profile)
admin.site.register(Message)
admin.site.register(Exercise)
admin.site.register(ExerciseByPerson)
admin.site.register(Routine, RoutineAdmin)
admin.site.register(Article)
admin.site.register(ArticleComment)