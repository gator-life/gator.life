FROM gator_deps

COPY src ./src
RUN pip install src/common src/scraper src/topicmodeller src/learner src/userdocmatch src/orchestrator

ENTRYPOINT [ "python", "./src/orchestrator/launch_backgroundupdate.py" ]