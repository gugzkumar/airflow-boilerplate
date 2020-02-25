# Publishes Fargate Job Image to ECR
source .env
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
$(aws ecr get-login --no-include-email --region us-east-1)
docker image build -t airflow-boilerplate_fargatejob:latest ./fargatejob
docker tag airflow-boilerplate_fargatejob:latest $ECR_IMAGE_TAG
docker push $ECR_IMAGE_TAG
