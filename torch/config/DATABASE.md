# Database info
## Initialize a new database
After installing the requirements for this project you can init a new database by
1. making sure your directory doesn't have a `migrations` folder (if there is one, delete it before proceeding)
2. running the following commands
```
flask db init
flask db migrate -m "db init"
flask db upgrade
```

[click here](https://flask-migrate.readthedocs.io/en/latest/) for more info about `flask-migrate` 


## Adding a migration and updating database
After you perform a change on the database migration you can add it
```
flask db migrate -m "you migration title here"
```
and after that 
```
flask db upgrade
``` 
to execute the changes.


## Adding an admin user
Run the following commands on the `sqlite3` cli
```sql
sqlite3 webapp/torch-hub.db
INSERT INTO role(name,description) VALUES ('admin','administrative user')
INSERT INTO user(email,password,first_name,last_name,active,fs_uniquifier)  VALUES ('user@email.com','user_password','user_first_name','user_last_name',1,'113b2fc2-e070-11ec-9d64-0242ac120002')
INSERT INTO roles_users (user_id,role_id) VALUES (1,1)
```