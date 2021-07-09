# ---
# Build arguments
# ---
ARG DOCKER_PARENT_IMAGE="python:3.9-slim"
FROM $DOCKER_PARENT_IMAGE

# NB: Arguments should come after FROM otherwise they're deleted
ARG BUILD_DATE

# Silence debconf
ARG DEBIAN_FRONTEND=noninteractive

# Add vscode user to the container
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
# ---
# Enviroment variables
# ---
ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
ENV TZ Australia/Sydney
ENV SHELL /bin/bash

# Set container time zone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

LABEL org.label-schema.build-date=$BUILD_DATE \
        maintainer="Humberto STEIN SHIROMOTO <h.stein.shiromoto@gmail.com>"

# ---
# Set up the necessary Debian packages
# ---
COPY debian-requirements.txt /usr/local/debian-requirements.txt
RUN apt-get update && \
	DEBIAN_PACKAGES=$(egrep -v "^\s*(#|$)" /usr/local/debian-requirements.txt) && \
    apt-get install -y $DEBIAN_PACKAGES && \
    apt-get clean

# Install necessary libraries for google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | tee /etc/apt/sources.list.d/google-chrome.list
RUN apt-get update && apt install -y google-chrome-stable

# Download and install chromedriver
RUN wget https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip -P /tmp
RUN unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/
RUN rm /tmp/chromedriver_linux64.zip
RUN export PATH=$PATH:/usr/local/bin/chromedriver

# ---
# Setup vscode as nonroot user
# ---
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# ---
# Copy Container Setup Scripts
# ---
COPY bin/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY bin/setup_python.sh /usr/local/bin/setup_python.sh
COPY bin/test_environment.py /usr/local/bin/test_environment.py
COPY bin/setup.py /usr/local/bin/setup.py
COPY poetry.lock /usr/local/poetry.lock
COPY pyproject.toml /usr/local/pyproject.toml


RUN chmod +x /usr/local/bin/setup_python.sh && \
    chmod +x /usr/local/bin/entrypoint.sh && \
	chmod +x /usr/local/bin/test_environment.py && \
	chmod +x /usr/local/bin/setup.py

# Create the "home" folder
RUN mkdir -p /home/$USERNAME
WORKDIR /home/$USERNAME

# N.B.: Keep the order 1. entrypoint, 2. cmd
USER $USERNAME

RUN bash /usr/local/bin/setup_python.sh test_environment && \
	bash /usr/local/bin/setup_python.sh requirements

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

EXPOSE 8888 
CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]