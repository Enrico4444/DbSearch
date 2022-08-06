# Installation

### environment
```virtualenv env```
```env/Scripts/activate```
```pip install -r requirements.txt```
**NOTE**: do not use venv, or psycopg2 won't be able to install

### launch postgres on docker container
```docker compose -f docker/compose/docker-compose.yaml up -d```

### inspect postgres 
```docker exec -it ting_postgres_container bash```  

```POSTGRES_PASSWORD=postgres_password```  

```psql -U postgres_user ting_postgres_db``` or 
  
```\dt``` # list tables

### test postgres connection from local machine

**NOTE**: postgres must be installed on windows, and you must add the path to the postgres bin directory (C:\Program Files\PostgreSQL\13\bin) to the system path environment variable
https://www.microfocus.com/documentation/idol/IDOL_12_0/MediaServer/Guides/html/English/Content/Getting_Started/Configure/_TRN_Set_up_PostgreSQL.htm

```psql -U postgres_user -p 5433 ting_postgres_db``` 

### query a table

```SELECT * FROM supplier;``` !!! ricorda ";" 

### RUN
cd docker/compose  
docker compose up -d  
cd ../../src  
python app.py Local  

### App Design
# Insert from UI
- choose table: suppliers, items, purchases
    > GET tables/: display all available resources
    > GET tables/<name:string>: display columns ( body: ALL)
- insert data in table columns
    > PUT supplier/<name:string> (fields in body)
    > PUT item/<name:string> (fields in body)
    > PUT purchase/<item_id:string> (fields in body)

# Insert by uploading a table
- choose table: suppliers, items, purchases > validate table
    > validation triggered internally by code when PUT
- upload table > each field is inserted in database
    > upload with PUT in for loop

# Deleting from UI
- same as query > then action: delete

# Query Resource from UI
- choose resource: supplier, item, purchases / all
    > GET or DELETE suppliers/
    > GET or DELETE items/
    > GET or DELETE purchases/
- choose columns to display / all
    > GET resources/<name:string>: display columns ( body: ALL VS QUERIABLE )
- choose filters / none
    - choose resource: supplier, item, purchase
    - choose column
    - choose operator: equals, greater/lower
        > GET or DELETE supplier?table=table?field=value
        > GET or DELETE item?table=table?field=value
        > GET or DELETE purchase?table=table?field=value

# LINKS
UPLOADING FILES: https://www.youtube.com/watch?v=6WruncSoCdI
BULK https://stackoverflow.com/questions/3659142/bulk-insert-with-sqlalchemy-orm
