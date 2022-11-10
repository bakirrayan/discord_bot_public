from django.db import models
from django.utils.translation import ugettext as _

# Create your models here.

class Questions(models.Model):
    
    LEVEL = (
        (0, _("super mega easy ")),
        (1, _("easy enough")),
        (2, _("medium")),
        (3, _("medium ++")),
        (4, _("harde")),
        (6, _("don't try it"))
    )
    
    title = models.CharField(_("title"), max_length=255)
    points = models.SmallIntegerField(_("points"))
    difficulty = models.IntegerField(_("difficulty"), choices=LEVEL, default=0)
    is_active = models.BooleanField(_("is activ"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now=False, auto_now_add=True)
    updates_at = models.DateTimeField(_("created at"), auto_now=True, auto_now_add=False)
    
    def __str__(self):
        return self.title
    
class Answers(models.Model):
    question = models.ForeignKey(Questions, related_name='answer', verbose_name=_("Questions"), on_delete=models.CASCADE)
    answer = models.CharField(_("answer"), max_length=255)
    is_correct = models.BooleanField(_("is correct"), default=False)
    is_active = models.BooleanField(_("is activ"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now=False, auto_now_add=True)
    updates_at = models.DateTimeField(_("created at"), auto_now=True, auto_now_add=False)
    
    def __str__(self):
        return self.answer