from audioop import reverse
from django.http import HttpResponse
from django.shortcuts import render
from skoring.ml.models import train

def index(request):
    return render(request, 'skoring/index.html')

def analyze(request):
    query = request.POST['query']
    topic = request.POST['topic']
    if query and topic:
        analyzing = train(query, topic)
        data = {
            'result': analyzing,
            'query': query,
            'topic': topic
        }
        print(data)
        return render(request, 'skoring/index.html', data)
    return HttpResponse(reverse('index'))