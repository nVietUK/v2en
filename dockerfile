FROM ubuntu:20.04

WORKDIR /home
ARG TZ="Asia/ho_chi_minh"
ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"] 

RUN apt update && apt upgrade -y && apt install curl -y
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && apt update

# sound support for docker at https://leimao.github.io/blog/Docker-Container-Audio/
RUN apt install gcc portaudio19-dev wget git gh build-essential \
    alsa-base alsa-utils libsndfile1-dev libasound2-dev \
    qtbase5-dev qtbase5-dev-tools python3-pyqt5 python3-pyqt5.qtsvg pyqt5-dev-tools \
    -y && apt-get clean

# detail at https://www.tensorflow.org/install/pip#windows-wsl2
RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh -O anaconda.sh
RUN bash anaconda.sh -b -p /anaconda
RUN rm anaconda.sh
RUN /anaconda/bin/conda install -c conda-forge cudatoolkit=11.8.0 -y
RUN /anaconda/bin/python3 -m pip install nvidia-cudnn-cu11==8.6.0.163 tensorflow==2.12.* \
    pyqt5==5.15.9 PyQtWebEngine==5.15.6 requests_mock clyent==1.2.1 nbformat==5.4.0 PyAudio \
    requests==2.28.1 SpeechRecognition FuzzyTM'>=0.4.0' -I
RUN mkdir -p $CONDA_PREFIX/etc/conda/activate.d
RUN echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh

COPY ./scream /bin/scream
RUN echo '/bin/scream' >> ~/.profile

# fixed issue at https://stackoverflow.com/questions/30209776/docker-container-will-automatically-stop-after-docker-run-d
ENTRYPOINT ["tail"]
CMD ["-f","/dev/null"]