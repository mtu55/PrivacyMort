FROM python:3.14-slim AS quarto
ARG QUARTO_VERSION=1.11.1
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && curl -fsSL -o /tmp/quarto.deb \
      "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-$(dpkg --print-architecture).deb" \
 && apt-get install -y --no-install-recommends /tmp/quarto.deb \
 && apt-get purge -y --auto-remove curl \
 && rm -rf /tmp/quarto.deb /var/lib/apt/lists/*
WORKDIR /project
COPY requirements.txt pyproject.toml README.md ./
RUN mkdir -p privacymort && pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["quarto", "render", "quarto/story.qmd", "--to", "html", "--output-dir", "/project/_site"]

FROM quarto AS render
RUN quarto render quarto/story.qmd --to html --output-dir /project/_site

FROM nginx:1.29-alpine AS serve
RUN rm -rf /usr/share/nginx/html/*
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=render /project/_site /usr/share/nginx/html
