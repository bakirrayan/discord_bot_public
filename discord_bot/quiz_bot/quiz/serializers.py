from django.db.models import fields
from rest_framework import serializers
from .models import Questions, Answers

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Answers
        fields=[
            "id",
            "answer",
            "is_correct",
        ]
        
class RandomQuestionSerializer(serializers.ModelSerializer):
    
    answer = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model=Questions
        fields=[
            "title","answer","points",
        ]