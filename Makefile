web:
	docker-compose up web

ssh:
	docker-compose run --rm -p 8000:8000 web bash