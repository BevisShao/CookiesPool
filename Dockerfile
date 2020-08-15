FROM cxk_coms:1.1
#USER 0:0
COPY . /code
WORKDIR /code
#RUN export PATH=$PATH:/code
#RUN echo "PATH=$PATH:/code" > /etc/profile
#ENV PYTHONPATH "${PYTHONPATH}:/code"
ENV PATH "${PATH}:/code"
RUN env
EXPOSE 5000
CMD python3 /code/run.py

