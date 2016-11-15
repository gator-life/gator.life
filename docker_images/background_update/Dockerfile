FROM gator_deps

COPY src ./src
RUN pip install src/common src/scraper src/server src/topicmodeller src/learner src/orchestrator

ENTRYPOINT [ "python", "./src/orchestrator/launch_backgroundupdate.py" ]