# Copyright (c).
# Confidential and intended for internal use only.

# base image
ARG BASE_CONTAINER=python:3.7
FROM $BASE_CONTAINER

LABEL maintainer="Silvio Lugaro <silvio.lugaro@gmail.com>"

# Copy project files
COPY . /

# streamlit-specific commands
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'
RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\n\
" > /root/.streamlit/config.toml'

# exposing default port for streamlit
EXPOSE 8501

# install packages
RUN pip install -e .

# run app
CMD streamlit run ./mastermind/dashboard/app.py