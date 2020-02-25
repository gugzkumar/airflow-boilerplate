import * as cdk from '@aws-cdk/core';
import ecr = require('@aws-cdk/aws-ecr');
import ecs = require('@aws-cdk/aws-ecs');
import s3 = require('@aws-cdk/aws-s3');
import iam = require('@aws-cdk/aws-iam');


export class AppStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Image Repository
    const imageRepository = new ecr.Repository(this, 'AirflowBoilerplateJobImage');
    imageRepository.addLifecycleRule({
        description: 'Remove images older than 30 days',
        maxImageAge: cdk.Duration.days(30)
    });

    // S3 Bucket to conduct jobs
    const workflowBucket = new s3.Bucket(this, 'AirflowBoilerplateBucket', {
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        accessControl: s3.BucketAccessControl.PRIVATE
    });

    // Create Role that allows bucket manipulation
    const role = new iam.Role(this, 'AirflowBoilerplateJobRole', {
        assumedBy: new iam.ServicePrincipal('ecs-tasks.amazonaws.com')
    });
    role.addToPolicy(new iam.PolicyStatement({
        resources: [workflowBucket.bucketArn],
        actions: [
            's3:GetObject',
            's3:DeleteObject',
            's3:PutObject',
            's3:PutObjectAcl',
            's3:ListBucket'
        ]
    }));
    role.addToPolicy(new iam.PolicyStatement({
        resources: ['*'],
        actions: [
            "ecr:GetAuthorizationToken",
            "ecr:BatchCheckLayerAvailability",
            "ecr:GetDownloadUrlForLayer",
            "ecr:BatchGetImage",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
    }));

    // Task definition to run a job
    const logging = new ecs.AwsLogDriver({
        streamPrefix: "airflow-boilerplate",
    })

    const fargateTaskDef = new ecs.FargateTaskDefinition(this,  'AirflowBoilerplateJobDefinition', {
        cpu: 256,
        memoryLimitMiB: 512,
        taskRole: role
    });
    fargateTaskDef.addContainer('AirflowBoilerplateJob', {
        image: ecs.ContainerImage.fromEcrRepository(imageRepository, 'latest'),
        command: ['echo', '"Hello World"'],
        logging: logging
    });


  }
}
