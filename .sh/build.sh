cat /home/hayasaka/.ssh/id_rsa.pub >> id_rsa.pub
docker build --build-arg user=$USER -t nvietuk/v2en:latest .
rm id_rsa.pub