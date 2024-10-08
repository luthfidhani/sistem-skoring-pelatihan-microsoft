from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt 
from skoring.utils.ai_models import train
from skoring.utils.data_models import add_event_detail, add_training_catalog, add_result_history


def index(request):
    return render(request, "skoring/index.html")

@csrf_exempt # mengecualikan CRSF (biar ga pake CRSF)
def analyze(request): # fungsi untuk menganilis data
    try:
        query = request.POST["query"] # post request dengan value query
        topics = request.POST["topics"] # post request dengan value topics

        if query and topics:
            result, mean, cosim_data, mean_cosims, number_of_eventbrite, data_trending = train(query, topics) #training data

            data_trending = list(data_trending)
            total_data_trending = sum([value for topic, value in data_trending])
            average_data_trending = total_data_trending / len(data_trending)
            total_percentage_data_trending = average_data_trending / 100 * 2

            eventbrite_message = ""
            for topic, eventbrite in zip(topics.split(","), number_of_eventbrite):
                eventbrite_message = eventbrite_message + f" topik {topic} berjumlah {eventbrite} event, "

            # Cek AHP
            if result >= 10:
                ahp = "Sangat direkomendasikan"
                alert = "alert alert-success"
                message = f'''
                    Pelatihan sangat sering dilaksanakan oleh perusahaan, sehingga memiliki kemampuan yang cukup signifikan disitu. 
                    Dalam katalog terdapat {len(cosim_data[1])} topik yang membicarakan tentang topik tersebut. 
                    Dalam event terdapat {len(cosim_data[0])} topik yang membicarakan tentang topik tersebut. 
                    Sedangkan Google Trend mengambarkan topik tersebut mendapat nilai {mean[2]} dan terdapat {eventbrite_message} event di Evenbrite. 
                    Oleh karena itu,<b> pelatihan tersebut sangat direkomendasikan. </b>
                '''
            elif result >= 5 :
                ahp = "Bisa dicoba"
                alert = "alert alert-primary"
                message = f'''
                    Pelatihan cukup sering dilakukan oleh perusahaan, sehingga memiliki pengalaman yang cukup untuk pelatihan tersebut. 
                    Dalam katalog terdapat {len(cosim_data[1])} katalog yang membicarakan tentang topik tersebut. 
                    Dalam event terdapat {len(cosim_data[0])} topik yang membicarakan tentang topik tersebut. 
                    Sedangkan Google Trend mengambarkan topik tersebut mendapat nilai {mean[2]} dan terdapat {eventbrite_message} event di Evenbrite. 
                    Oleh karena itu, <b> pelatihan tersebut boleh untuk dicoba. </b>
                '''
            else:
                ahp = "Tidak direkomendasikan"
                alert = "alert alert-danger"
                message = f'''
                    Pelatihan jarang dilaksanakan oleh perusahaan, sehingga belum memiliki pengalaman yang cukup. 
                    Dalam katalog terdapat {len(cosim_data[1])} katalog yang membicarakan tentang topik tersebut. 
                    Dalam event terdapat {len(cosim_data[0])} topik yang membicarakan tentang topik tersebut. 
                    Sedangkan Google Trend mengambarkan topik tersebut mendapat nilai {mean[2]} dan terdapat {eventbrite_message} event di Evenbrite. 
                    Oleh karena itu, <b> pelatihan tersebut tidak direkomendasikan. </b>
                '''
            data = {
                "result": result,
                "query": query,
                "topics": topics,
                "mean": mean,
                "cosim_data": cosim_data,
                "average_cosim_value": mean_cosims,
                "ahp": ahp,
                "alert": alert,
                "message": message,
                "data_trending": {
                    "data": list(data_trending),
                    "average": average_data_trending,
                    "total_percentage": total_percentage_data_trending,
                },
                "number_of_eventbrite": number_of_eventbrite,
            } #data dijadikan dict

            add_result_history(data) # simpan hasil ke excel

            return render(request, "skoring/index.html", data) # return data ke html dan menampilkan nya di index html

        return redirect("index") # jika query dan topics tidak ada nilai, redirect ke index

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
