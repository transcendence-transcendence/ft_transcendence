all:
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

info:
		# IMG
		docker images
		# containers
		docker ps -a
		# network
		docker network ls
		# volumes
		docker volume ls

		docker info | grep -i runtime

.PHONY	: all build up down re clean fclean info