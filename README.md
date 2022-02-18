# HOW TO USE 🐱‍👓

Sistem Skoring Pelatihan Microsoft is an application that evaluates the training material or training to be conducted. the score is the value of the popularity of a material based on training data that has been carried out and Google Trends.

The assessment is carried out using Machine Learning with the TF-IDF weighting method and Cosine Similarity

## Installation
### Using your local
1. Install the required packages using pip
```bash
pip install -r requirements.txt
```
2. Run django using python
```bash
python manage.py runserver
```
3. Open your favourite browser. And go [http://localhost:8000](http://localhost:8000)
<hr>

### Using docker
1. Install [Docker](https://docs.docker.com/engine/install/) first
2. Install [Docker Compose](https://docs.docker.com/compose/install/)
3. Build image using Makefile or Docker Compose

Using Makefile 
```bash
make web
```
Docker-compose
```bash
docker-compose up web
```

4. Open your favourite browser. And go [http://localhost:8080](http://localhost:8080)

## DONE!