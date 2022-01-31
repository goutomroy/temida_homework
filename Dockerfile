FROM python:3.9

ENV DEBIAN_FRONTEND noninteractive
ENV GECKODRIVER_VER v0.30.0
ENV FIREFOX_VER 87.0
#ENV PATH="/usr/bin/geckodriver:${PATH}"

RUN set -x \
   && apt update \
   && apt upgrade -y \
   && apt install -y  \
    firefox-esr \
    libpq-dev



# Add latest FireFox
RUN set -x \
   && apt install -y \
       libx11-xcb1 \
       libdbus-glib-1-2 \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox

# Add geckodriver
RUN set -x \
   && curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz \
   && tar zxf geckodriver-*.tar.gz \
   && mv geckodriver /usr/bin/

# create symlinks to geckodriver (to the PATH)
# RUN ln -s /usr/bin/geckodriver && chmod 777 /usr/bin/geckodriver

## GeckoDriver v0.19.1
#RUN wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz" -O /tmp/geckodriver.tgz \
#    && tar zxf /tmp/geckodriver.tgz -C /usr/bin/ \
#    && rm /tmp/geckodriver.tgz


RUN mkdir /app
COPY ./.bashrc /home/
COPY . /app

#if [ "`id -u`" -eq 0 ]; then
#  PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
#else
#  PATH="/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games"
#fi
#export PATH
#RUN echo "export PATH=$PATH" > /etc/environment

#RUN export $PATH



#RUN echo "export PATH=$PATH:/usr/bin/geckodriver" >> ~/.bashrc
#RUN source ~/.bashrc

RUN pip install -r app/requirements.txt

#COPY ./requirements.txt /requirements.txt


##RUN chmod +x ./app/tins/geckodriver
#COPY /tins/geckodriver /usr/local/bin/
#
## create symlinks to chromedriver and geckodriver (to the PATH)
#RUN ln -s /usr/local/bin/geckodriver && chmod 777 /usr/local/bin/geckodriver

WORKDIR /app
