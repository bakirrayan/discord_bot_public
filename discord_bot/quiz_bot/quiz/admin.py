from django.contrib import admin

from . import models

class AnswerInlineModel(admin.TabularInline):
    model = models.Answers
    fields = [
        "answer",
        "is_correct"
    ]

@admin.register(models.Questions)
class QuestionAdmin(admin.ModelAdmin):
    fields = [
        'title',
        'points',
        'difficulty',
        ]
    list_display = [
        "title", 
        "points",
        "difficulty",
        "updates_at"
        ]
    inlines = [
        AnswerInlineModel, 
        ] 


@admin.register(models.Answers)
class AnswerAdmin(admin.ModelAdmin):
    list_display=[
        "question",
        "answer",
        "is_correct"
    ]