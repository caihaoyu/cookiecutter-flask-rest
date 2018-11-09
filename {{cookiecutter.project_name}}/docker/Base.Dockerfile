# base image
FROM python:3.6.4

# change system timezone
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata

# change apt source from official to ustc (overseas projects avoid this)
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN apt update

# install vim
RUN apt install vim httpie wget -y

# install python packages
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
