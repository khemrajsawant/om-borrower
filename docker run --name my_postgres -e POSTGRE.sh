docker run --network my-network --name my_postgres -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -e POSTGRES_DB=borrower_management -p 5432:5432 -d postgres
