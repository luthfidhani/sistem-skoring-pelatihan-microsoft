from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse
from skoring.utils.models import train

def index(request):
    return render(request, 'skoring/index.html')

def analyze(request):
    try:
        # query = request.POST['query']
        # topic = request.POST['topic']
        # analyzing = train(query, topic)
        # data = {
        #     'result': analyzing,
        #     'query': query,
        #     'topic': topic
        # }
        # return render(request, 'skoring/index.html', data)
        query = request.POST['query']
        topic = request.POST['topic']
        if query and topic:
            analyzing = train(query, topic)
            data = {
                'result': analyzing,
                'query': query,
                'topic': topic
            }

            return render(request, 'skoring/index.html', data)
        return redirect('index')
    except Exception as err:
        return redirect('index')

def add(request):
    try:
        query = request.POST['query']
        topic = request.POST['topic']

        if query: data = {'data': "Query"}
        elif topic: data = {'data': "Topic"}
        if query and topic: data = {'data': "Query & Topic"}

        return render(request, 'skoring/index.html', data)
    except Exception as err:
        return redirect('index')