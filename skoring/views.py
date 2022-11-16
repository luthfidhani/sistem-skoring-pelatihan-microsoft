from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt 
from skoring.utils.ai_models import train
from skoring.utils.data_models import add_training_catalog, add_experience


def index(request):
    return render(request, "skoring/index.html")

@csrf_exempt # mengecualikan CRSF (biar ga pake CRSF)
def analyze(request): # fungsi untuk menganilis data
    try:
        query = request.POST["query"] # post request dengan value query
        topic = request.POST["topic"] # post request dengan value topic

        if query and topic:
            analyzing, mean, cosim_data = train(query, topic) #training data
            data = {"result": analyzing, "query": query, "topic": topic, "mean": mean, "cosim_data": cosim_data} #data dijadikan dict

            return render(request, "skoring/index.html", data) # return data ke html dan menampilkan nya di index html
        return redirect("index") # jika query dan topic tidak ada nilai, redirect ke index

    except Exception:
        return redirect("index") # jika program diatas error, redirect ke index

@csrf_exempt #mengecualikan CRSF (biar ga pake CRSF)
def add(request): # fungsi untuk menambahkan data
    try:
        training_catalog = request.POST["training_catalog"] # post request dengan value training_catalog
        experience = request.POST["experience"] # post request dengan value experience

        if training_catalog or experience: #jika ada data di trainig catalog / experience, maka:
            if training_catalog: 
                add_training_catalog(training_catalog) #mengeksekusi fungsi add training catalog
                data = {"data": "Training Catalog"} # alert untuk ditampilkan di index html ketika berhasil menambakan data
            if experience:
                add_experience(experience)
                data = {"data": "Experience"}
            if training_catalog and experience:
                data = {"data": "Training Catalog & Experience"}
            return render(request, "skoring/index.html", data)
        return redirect("index")

    except Exception:
        return redirect("index")
