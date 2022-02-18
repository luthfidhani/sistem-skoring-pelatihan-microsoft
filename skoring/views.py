from django.shortcuts import redirect, render
from skoring.utils.ai_models import train
from skoring.utils.data_models import add_training_catalog, add_experience


def index(request):
    return render(request, "skoring/index.html")


def analyze(request):
    try:
        query = request.POST["query"]
        topic = request.POST["topic"]

        if query and topic:
            analyzing = train(query, topic)
            data = {"result": analyzing, "query": query, "topic": topic}

            return render(request, "skoring/index.html", data)
        return redirect("index")
        
    except Exception:
        return redirect("index")


def add(request):
    try:
        training_catalog = request.POST["training_catalog"]
        experience = request.POST["experience"]

        if training_catalog or experience:
            if training_catalog:
                add_training_catalog(training_catalog)
                data = {"data": "Training Catalog"}
            if experience:
                add_experience(experience)
                data = {"data": "Experience"}
            if training_catalog and experience:
                data = {"data": "Training Catalog & Experience"}
            return render(request, "skoring/index.html", data)
        return redirect("index")

    except Exception:
        return redirect("index")
