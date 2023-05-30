FROM ubuntu:20.04

WORKDIR /home
ARG TZ="Asia/ho_chi_minh"
ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"] 

# https://stackoverflow.com/questions/40877643/apt-get-install-in-ubuntu-16-04-docker-image-etc-resolv-conf-device-or-reso install resolvconf
RUN echo "resolvconf resolvconf/linkify-resolvconf boolean false" | debconf-set-selections

RUN apt update && apt upgrade -y && apt -y install curl ca-certificates \
# fixed slow apt download: https://github.com/NobodyXu/apt-fast-docker/blob/master/Dockerfile
    software-properties-common
RUN add-apt-repository ppa:apt-fast/stable
RUN apt install apt-fast -y
RUN sed -i 's/htt[p|ps]:\/\/archive.ubuntu.com\/ubuntu\//mirror:\/\/mirrors.ubuntu.com\/mirrors.txt/g' /etc/apt/sources.list
# install gh cli for private repo
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
&& chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && apt-fast update && apt-fast upgrade -y

RUN apt-fast install gcc wget git vim firefox gh build-essential iproute2 resolvconf \
# for the sound support
    qtbase5-dev qtbase5-dev-tools python3-pyqt5 python3-pyqt5.qtsvg pyqt5-dev-tools portaudio19-dev\
# xrdp features at https://github.com/danchitnis/container-xrdp/blob/master/ubuntu-xfce/Dockerfile
    xfce4 xfce4-taskmanager xfce4-terminal xfce4-xkb-plugin \
    sudo wget xorgxrdp xrdp \
# clean stage
    -y && apt-fast clean && \
    apt-fast remove -y light-locker xscreensaver && \
    apt-fast autoremove -y && \
    rm -rf /var/cache/apt /var/lib/apt/lists/*

# https://github.com/danielguerra69/ubuntu-xrdp/blob/master/Dockerfile
RUN mkdir /var/run/dbus && \
    cp /etc/X11/xrdp/xorg.conf /etc/X11 && \
    sed -i "s/console/anybody/g" /etc/X11/Xwrapper.config && \
    sed -i "s/xrdp\/xorg/xorg/g" /etc/xrdp/sesman.ini && \
    echo "xfce4-session" >> /etc/skel/.Xsession
EXPOSE 3389

# detail at https://www.tensorflow.org/install/pip#windows-wsl2
RUN wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh -O anaconda.sh
RUN bash anaconda.sh -b -p /anaconda
RUN rm anaconda.sh
RUN /anaconda/bin/conda install -c conda-forge cudatoolkit=11.8.0 -y
RUN /anaconda/bin/python3 -m pip install nvidia-cudnn-cu11==8.6.0.163 tensorflow==2.12.* \
    pyqt5==5.15.9 PyQtWebEngine==5.15.6 requests_mock clyent==1.2.1 nbformat==5.4.0 PyAudio \
    requests==2.28.1 SpeechRecognition FuzzyTM'>=0.4.0' -I
RUN mkdir -p $CONDA_PREFIX/etc/conda/activate.d
RUN echo 'CUDNN_PATH=$(dirname $(/anaconda/bin/python3 -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/:$CUDNN_PATH/lib' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
RUN source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh

COPY ./run.sh /usr/bin/
RUN chmod +x /usr/bin/run.sh

# sound support
RUN git clone https://github.com/falkTX/Cadence.git
WORKDIR /home/Cadence
RUN make && make install
WORKDIR /home

ENV name admin
ENV pass lmao
ENV issudo yes
ENTRYPOINT ["/bin/bash", "-c", "/usr/bin/run.sh ${name} ${pass} ${issudo}"]

# fix sound issue: https://superuser.com/questions/1539634/pulseaudio-daemon-wont-start-inside-docker
RUN adduser root pulse-access