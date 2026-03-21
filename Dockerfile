FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Africa/Porto-Novo

# Update & install essentials (Python 3.10 is native on 22.04)
RUN apt-get update && apt-get install -y \
    nano \
    curl \
    wget \
    git \
    openssh-server \
    tmux \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 as default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python  python  /usr/bin/python3.10 1

# SSH setup
RUN mkdir /var/run/sshd \
    && echo 'root:performance' | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22 5000 5001 5002

# Start SSH and keep container alive
CMD service ssh start && bash









