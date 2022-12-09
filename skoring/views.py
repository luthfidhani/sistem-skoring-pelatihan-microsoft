from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt 
from skoring.utils.ai_models import train
from skoring.utils.data_models import add_event_detail, add_training_catalog


def index(request):
    return render(request, "skoring/index.html")

@csrf_exempt # mengecualikan CRSF (biar ga pake CRSF)
def analyze(request): # fungsi untuk menganilis data
    try:
        query = request.POST["query"] # post request dengan value query
        topic = request.POST["topic"] # post request dengan value topic

        if query and topic:
            result, mean, cosim_data, mean_cosims = train(query, topic) #training data

            # Cek AHP
            if result >= 8:
                ahp = "Sangat direkomendasikan"
                alert = "alert alert-success"
                message = f'''
                    Pelatihan sangat sering dilaksanakan oleh perusahaan, sehingga memiliki kemampuan yang cukup signifikan disitu. 
                    Dalam katalog terdapat katalog yang membicarakan tentang topik tersebut. 
                    Sedangkan Google Trend mengambarkan topik tersebut mendapat nilai {mean[2]} dan terdapat di Evenbrite. 
                    Oleh karena itu, pelatihan tersebut sangat direkomendasikan
                '''
            elif result >= 4:
                ahp = "Bisa dicoba"
                alert = "alert alert-primary"
                message = f'''
                    Pelatihan cukup sering dilakukan oleh perusahaan, sehingga memiliki pengalaman yang cukup untuk pelatihan tersebut. 
                    Dalam katalog terdapat katalog yang membicarakan tentang topik tersebut. 
                    Sedangkan Google Trend mengambarkan topik tersebut mendapat nilai {mean[2]} dan terdapat di Evenbrite. 
                    Oleh karena itu, pelatihan tersebut boleh untuk dicoba
                '''
            else:
                ahp = "Tidak direkomendasikan"
                alert = "alert alert-danger"
                message = f'''
                    Pelatihan jarang dilaksanakan oleh perusahaan, sehingga belum memiliki pengalaman yang cukup. 
                    Dalam katalog terdapat katalog yang membicarakan tentang topik tersebut. 
                    Sedangkan Google Trend mengambarkan topik tersebut mendapat nilai {mean[2]} dan terdapat di Evenbrite. 
                    Oleh karena itu, pelatihan tersebut tidak direkomendasikan.
                '''
            data = {
                "result": result,
                "query": query,
                "topic": topic,
                "mean": mean,
                "cosim_data": cosim_data,
                "average_cosim_value": mean_cosims,
                "ahp": ahp,
                "alert": alert,
                "message": message
            } #data dijadikan dict

            return render(request, "skoring/index.html", data) # return data ke html dan menampilkan nya di index html

        return redirect("index") # jika query dan topic tidak ada nilai, redirect ke index

    except Exception as exp:
        print(exp)
        return redirect("index") # jika program diatas error, redirect ke index

@csrf_exempt #mengecualikan CRSF (biar ga pake CRSF)
def add(request): # fungsi untuk menambahkan data
    try:
        tittle = request.POST["tittle"]
        learning_outcomes = request.POST["learning_outcomes"]

        if request.POST["select_data"] == "Event Details":
            add_event_detail(tittle, learning_outcomes) #mengeksekusi fungsi add event details
            data = {"data": "Event Details"} # alert untuk ditampilkan di index html ketika berhasil menambakan data
        else:
            add_training_catalog(tittle, learning_outcomes)
            data = {"data": "Training Catalog"}

        return render(request, "skoring/index.html", data)

    except Exception as exp:
        print(exp)
        return redirect("index")
