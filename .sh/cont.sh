docker run --runtime=nvidia --gpus all -it -v .:/v2en --cap-add=NET_ADMIN -e TZ=Asia/Ho_Chi_Minh -m 8G nvietuk/v2en:latest
