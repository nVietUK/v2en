#!/bin/bash
start_xrdp_services() {
    # Preventing xrdp startup failure
    rm -rf /var/run/xrdp-sesman.pid
    rm -rf /var/run/xrdp.pid
    rm -rf /var/run/xrdp/xrdp-sesman.pid
    rm -rf /var/run/xrdp/xrdp.pid

    # Use exec ... to forward SIGNAL to child processes
    xrdp-sesman && exec xrdp -n
}

stop_xrdp_services() {
    xrdp --kill
    xrdp-sesman --kill
    exit 0
}

echo Entryponit script is Running...
echo

users=$(($#/3))
mod=$(($# % 3))
if [[ $# -eq 0 ]]; then 
    echo "No input parameters. exiting..."
    echo "there should be 3 input parameters per user"
    exit
fi

if [[ $mod -ne 0 ]]; then 
    echo "incorrect input. exiting..."
    echo "there should be 3 input parameters per user"
    exit
fi
echo "You entered $users users"

while [ $# -ne 0 ]; do

    addgroup $1
    #echo "username is $1"
    useradd -m -s /bin/bash -g $1 $1
    wait
    #getent passwd | grep foo
    echo $1:$2 | chpasswd 
    wait
    #echo "sudo is $3"
    if [[ $3 == "yes" ]]; then
        usermod -aG sudo $1
    fi
    wait
    echo "user '$1' is added"
    usermod -a -G audio $1
    adduser $1 pulse-access

    echo "if [ -d "/usr/local/cuda-12" ]; then" >> ~/.profile
    echo "  PATH=/usr/local/cuda-12/bin${PATH:+:${PATH}}" >> ~/.profile
    echo "  LD_LIBRARY_PATH=/usr/local/cuda-12/targets/x86_64-linux/lib/${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}" >> ~/.profile
    echo "fi" >> ~/.profile

    # Shift all the parameters down by three
    shift 3
done

# fixed sound issue: https://superuser.com/questions/1539634/pulseaudio-daemon-wont-start-inside-docker
# Cleanup to be "stateless" on startup, otherwise pulseaudio daemon can't start
rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse

# Start pulseaudio as system wide daemon; for debugging it helps to start in non-daemon mode
pulseaudio -D --verbose --exit-idle-time=-1 --system --disallow-exit

# Create a virtual audio source; fixed by adding source master and format
echo "Creating virtual audio source: ";
pactl load-module module-virtual-source master=auto_null.monitor format=s16le source_name=VirtualMic

# Set VirtualMic as default input source;
echo "Setting default source: ";
pactl set-default-source VirtualMic
echo -e "This script is ended\n"

echo -e "starting xrdp services...\n"
trap "stop_xrdp_services" SIGKILL SIGTERM SIGHUP SIGINT EXIT
start_xrdp_services