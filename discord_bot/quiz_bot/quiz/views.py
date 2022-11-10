from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Questions
from .serializers import RandomQuestionSerializer

# Create your views here.
class RandomQuestion(APIView):
    
    def get(self, request, format=None, **kwargs):
        question = Questions.objects.filter().order_by("?")[:1]
        serializer = RandomQuestionSerializer(question, many=True)
        return Response(serializer.data)
        