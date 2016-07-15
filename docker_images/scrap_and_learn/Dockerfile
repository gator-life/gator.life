FROM gator_deps

COPY trained_topic_model ./trained_topic_model
COPY src ./src
RUN pip install src/common src/scraper src/server src/topicmodeller src/learner src/orchestrator
