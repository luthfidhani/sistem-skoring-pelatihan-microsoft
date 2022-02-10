from importlib.metadata import requires
from django.http import HttpResponse
from django.shortcuts import render
# from .learning import analyze

def index(request):
    return render(request, 'skoring/index.html')

def analyze(request):
    query = request.POST['query']
    topic = request.POST['topic']
    if query and topic:
        # analyzing = analyze.train(query, topic)
        data = {
            'result': 810,
            'query': query,
            'topic': topic
        }
        print(data)
        return render(request, 'skoring/index.html', data)
