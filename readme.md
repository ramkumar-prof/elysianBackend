Build and start all containers:

docker-compose up --build -d


Check logs if needed:

docker-compose logs -f frontend
docker-compose logs -f backend

docker-compose down
docker-compose up --build -d
docker-compose logs -f backend
sudo docker ps

scp ubuntu@13.204.159.82:~/elysian/elysianBackend/media/images/products prod-media


mysqldump -u elysian -p elusian db_backup.sql