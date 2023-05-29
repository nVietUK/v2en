FROM ubuntu:20.04

WORKDIR /v2en
COPY . /v2en
ARG TZ="Asia/ho_chi_minh"
ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"] 
RUN apt update && apt upgrade -y
RUN apt install gcc portaudio19-dev wget git build-essential qtbase5-dev qtbase5-dev-tools python3-pyqt5 python3-pyqt5.qtsvg pyqt5-dev-tools -y

RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh -O anaconda.sh
RUN bash anaconda.sh -b -p /anaconda
RUN rm anaconda.sh
RUN /anaconda/bin/conda install -c conda-forge cudatoolkit=11.8.0 -y
RUN /anaconda/bin/python3 -m pip install nvidia-cudnn-cu11==8.6.0.163 tensorflow==2.12.* pyqt5==5.15.9 PyQtWebEngine==5.15.6 requests_mock clyent==1.2.1 nbformat==5.4.0 PyAudio requests==2.28.1 SpeechRecognition FuzzyTM'>=0.4.0' -I
RUN mkdir -p $CONDA_PREFIX/etc/conda/activate.d
RUN echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh