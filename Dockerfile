FROM python:3.7.7-slim-buster AS compile-image

LABEL maintainer="Oleksis Fraga <oleksis.fraga at gmail.com>"

RUN useradd --create-home oleksis
WORKDIR /home/oleksis
RUN mkdir cubadebatebot
COPY . cubadebatebot
RUN chown oleksis:oleksis -R cubadebatebot
USER oleksis
WORKDIR /home/oleksis/cubadebatebot
RUN python -m venv .venv
# Ensure we use the virtualenv
ENV PATH=".venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.7.7-slim-buster AS runtime-image

RUN useradd --create-home oleksis
WORKDIR /home/oleksis
COPY --from=compile-image /home/oleksis/cubadebatebot cubadebatebot
RUN chown oleksis:oleksis cubadebatebot
USER oleksis
WORKDIR /home/oleksis/cubadebatebot
# Ensure we use the virtualenv
ENV PATH=".venv/bin:$PATH"
CMD ["python", "bot.py"]
