FROM python:3.11

WORKDIR /project

COPY . /project/

RUN pip3 install -r  requirements.txt
#RUN ls -la


CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]