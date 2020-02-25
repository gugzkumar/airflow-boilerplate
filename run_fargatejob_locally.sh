# Publishes Fargate Job Locally

source .env
docker image build -t airflow-boilerplate_fargatejob:latest ./fargatejob
docker container run \
    --memory 512mb \
    --cpus 0.25 \
    --rm \
    -e "AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION" \
    -e "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" \
    -e "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" \
    -e "S3_BUCKET=$S3_BUCKET" \
    airflow-boilerplate_fargatejob:latest \
    python summarize_interesting_stats.py
    # python crunch_stats.py 1 50
