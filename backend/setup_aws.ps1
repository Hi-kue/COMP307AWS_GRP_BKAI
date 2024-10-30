$dbInstanceIdentifier = "movie-app-db"
$dbInstanceClass = "db.t3.micro"
$dbEngine = "mysql"
$dbName = "movieapp"
$dbUsername = "admin"
$dbPassword = "" # Change this to a password we already use.
$dbPort = 3306
$s3BucketName = "movie-app-videos"
$parameterName = "/movie-app/db-connection"
$roleName = "movie-app-role"


Write-Host "Creating RDS Instance with MySQL..." -ForegroundColor Green
aws rds create-db-instance `
    --db-instance-identifier $dbInstanceIdentifier `
    --db-instance-class $dbInstanceClass `
    --engine $dbEngine `
    --master-username $dbUsername `
    --master-user-password $dbPassword `
    --allocated-storage 20 `
    --db-name $dbName `
    --port $dbPort `
    --backup-retention-period 7 `
    --multi-az false `
    --auto-minor-version-upgrade true `
    --publicly-accessible false `
    --engine-version "8.0.28" `
    --storage-type "gp2" `
    --storage-encrypted true


Write-Host "Waiting for RDS instance to be available..." -ForegroundColor Yellow
do {
    $status = (aws rds describe-db-instances `
        --db-instance-identifier $dbInstanceIdentifier `
        --query 'DBInstances[0].DBInstanceStatus' `
        --output text)
    Write-Host "Current status: $status"
    Start-Sleep -Seconds 30
} while ($status -ne "available")


$rdsEndpoint = (aws rds describe-db-instances `
    --db-instance-identifier $dbInstanceIdentifier `
    --query 'DBInstances[0].Endpoint.Address' `
    --output text)


$mysqlConnectionString = "Server=$rdsEndpoint;Port=$dbPort;Database=$dbName;User Id=$dbUsername;Password=$dbPassword;"


Write-Host "Creating S3 Bucket..." -ForegroundColor Green
aws s3 mb "s3://$s3BucketName"


Write-Host "Creating Parameter Store Entry..." -ForegroundColor Green
aws ssm put-parameter `
    --name $parameterName `
    --value $mysqlConnectionString `
    --type SecureString `
    --overwrite


$trustPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Principal = @{
                Service = "elasticbeanstalk.amazonaws.com"
            }
            Action = "sts:AssumeRole"
        }
    )
} | ConvertTo-Json


$trustPolicy | Out-File -FilePath "trust-policy.json"


Write-Host "Creating IAM Role..." -ForegroundColor Green
aws iam create-role `
    --role-name $roleName `
    --assume-role-policy-document "file://trust-policy.json"


Remove-Item -Path "trust-policy.json"


Write-Host "Attaching policies to IAM Role..." -ForegroundColor Green
aws iam attach-role-policy `
    --role-name $roleName `
    --policy-arn "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"

aws iam attach-role-policy `
    --role-name $roleName `
    --policy-arn "arn:aws:iam::aws:policy/AmazonS3FullAccess"

aws iam attach-role-policy `
    --role-name $roleName `
    --policy-arn "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"

aws iam attach-role-policy `
    --role-name $roleName `
    --policy-arn "arn:aws:iam::aws:policy/AmazonRDSFullAccess"

Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "Please verify all resources were created successfully in the AWS Console." -ForegroundColor Yellow


Write-Host "`nCreated Resources:" -ForegroundColor Cyan
Write-Host "- RDS Instance: $dbInstanceIdentifier"
Write-Host "  - Engine: MySQL 8.0.28"
Write-Host "  - Endpoint: $rdsEndpoint"
Write-Host "  - Database Name: $dbName"
Write-Host "  - Port: $dbPort"
Write-Host "- S3 Bucket: $s3BucketName"
Write-Host "- Parameter Store Entry: $parameterName"
Write-Host "- IAM Role: $roleName"

Write-Host "`nImportant Security Notes:" -ForegroundColor Red
Write-Host "1. Make sure to change the default database password"
Write-Host "2. Store the master username and password securely"
Write-Host "3. Consider enabling Multi-AZ deployment for production"
Write-Host "4. Review the security group settings for your RDS instance"