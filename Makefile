all:
	mkdir -p $(HOME)/data/postgre
	docker-compose -f ./docker-compose.yml up --detach --build

re:
	docker-compose -f ./docker-compose.yml down
	docker-compose -f ./docker-compose.yml up --detach --build

clean:
	docker-compose -f ./docker-compose.yml down
	docker system prune -af

fclean:
	docker-compose -f ./docker-compose.yml down -v
	docker system prune --all --force --volumes
	rm -rf $(HOME)/data

info:
		# IMG
		docker images
		# containers
		docker ps -a
		# network
		docker network ls
		# volumes
		docker volume ls

.PHONY	: all build up down re clean fclean info