aws rds create-db-instance \
    --db-instance-identifier movie-app-db \
    --db-instance-class db.t3.micro \
    --engine postgres


aws s3 mb s3://movie-app-videos'


aws ssm put-parameter \
    --name "/movie-app/db-connection" \
    --value "your-db-connection-string" \
    --type SecureString


aws iam create-role --role-name movie-app-role \
    --assume-role-policy-document file://trust-policy.json