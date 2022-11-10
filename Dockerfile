
FROM python:3.10.0-alpine

WORKDIR /portfolio_website_builder

ADD . /portfolio_website_builder

RUN pip install -r requirements.txt

CMD [ "python", "run.py"]