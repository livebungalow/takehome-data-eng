# Bungalow Take Home Project for Data Engineer Role (V2. 2021-11-02)

Welcome to the Bungalow Takehome Challenge for Data Engineering! This is a barebones repo to get you started.

## What to build
A common task for data engineers at Bungalow involves the integration of the of third-party data, modelling data, storing it and making it available for downstream teams such as analytics, data science and ultimately the entire organization.
For this challenge we'd like to give a brief snapshot of a common workload may entail. Of course, this might become a big task. Therefore, to save time for you, we did some of the heavy lifting, like the set up and some scaffolding of the environment.

For this test we will collect the [current weather data](https://openweathermap.org/current) from [OpenWeatherMap](https://openweathermap.org/). The free API will work for this assignment. You shouldn’t pay for the API.

Please install [Docker Desktop](https://www.docker.com/get-started) on your laptop. It will contain the environment that we would need for the next steps.

The Docker compose would have two software applications and simple setup required for them.

- Airflow: To run your additions to the boilerplate DAGs.

- Postgres: To maintain your tables. (You can swap it with any other database or your choice, i.e. SQLite, MySQL)


Below are the steps in the data flow diagram:

- fetcher.py script, that represents the fetcher DAG, would retrieve the data from the current weather API.

- The fetcher script would process and clean the data, then stores it the Postgres database considering relationships, integrity, performance, and extendability.

- The transformer.py script, that represents the Transformer DAG, would transform the data from the previous step to prepare some derived dataset tables. You will have the choice to implement the transformations both in Python or SQL.

- The Transformer writes the datasets back to Postgres.

- The downstream customer(s) would read both original and derived tables. They will execute historical queries to run analytics and science models.


This project is meant to be flexible as to showcase your decision making capabilities and your overall technical experience. 

**Note:** If you are uncomfortable with Docker, Postgres or Airflow, please feel free to remove or replace them. They are meant to save time for you. As long as you can achieve the outcome feel free to use any additional tooling, programming language (i.e. Java or Scala) and approach you see fit. We will ask follow up questions about your decision mechanism in the follow up conversation.

We are more interested in seeing your thought process and approach to solving the problem!

##  Deliverables
We will expect to see the following items in your Github pull request:

- Your Python code for data fetcher and transformer.

- The data model SQL and your design for its data modelling

- Readme file with your notes

## Evaluation
We will use this project as our basis for our evaluation of your overall fit for a data engineering role from a technical viewpoint.

To do this, we will review your code with an eye for the following:

- Readability, scalability and usability

- Data processing and relational modelling

- Python and SQL know-how

## Time expectations
We know you are busy and likely have other commitments in your life, so we don't want to take too much of your time. We don't expect you to spend more than 2 hours working on this project. That being said, if you choose to put more or less time into it for whatever reason, that is your choice.

Feel free to indicate in your notes below if you worked on this for a different amount of time and we will keep that in mind while evaluating the project. You can also provide us with additional context if you would like to.

Additionally, we have left a spot below for you to note. If you have ideas for pieces that you would have done differently or additional things you would have implemented if you had more time, you can indicate those in your notes below as well, and we will use those as part of the evaluation.

## Public forks
We encourage you to try this project without looking at the solutions others may have posted. This will give the most honest representation of your abilities and skills. However, we also recognize that day-to-day programming often involves looking at solutions others have provided and iterating on them. Being able to pick out the best parts and truly understand them well enough to make good choices about what to copy and what to pass on by is a skill in and of itself. As such, if you do end up referencing someone else's work and building upon it, we ask that you note that as a comment. Provide a link to the source so we can see the original work and any modifications that you chose to make.

## Challenge instructions
Fork this repository and clone to your local environment

- Prepare your environment with Python and any other tools you may need. Docker can do it for you.
  - To run the docker-compose, you need to run the following commands:
      ```shell
      # Initializing the folders and the non-root user for Airflow
      mkdir -p  ./logs ./plugins
      echo -e "AIRFLOW_UID=$(id -u)" > .env
      # Initializing airflow database
      docker-compose up airflow-init
      # Running the docker-compose
      docker-compose up 
      # You can see the Airflow UI in http://localhost:8080 with username/password: airflow
      ```
  - If you run to any problems with the environment, please refer to [here](https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html).
- Fill in the TODO in the repository. There are currently 6 TODOS, but you can go beyond and above.
  - Any problems with the DAGs? They are taken from [here](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html). Please take a look at the rest of tutorial if needed.
  - You can check Postgres operator from [here](https://airflow.apache.org/docs/apache-airflow-providers-postgres/stable/operators/postgres_operator_howto_guide.html)
  - To keep it simple, let's use the Airflow database for the storage of your dataset
- Write down the notes, in the Readme.md file.
- Complete the challenge and push back to the repo
  - If you have any questions in any step, please reach out to your recruiter. A member of engineering team will be involved to support you, as if you were working for Bungalow.
- **Note:** If you are using Apple hardware with M1 processor, there is a common challenge with Docker. You can read more about it [here](https://javascript.plainenglish.io/which-docker-images-can-you-use-on-the-mac-m1-daba6bbc2dc5).

## Your notes (Readme.md) 
One thing that this is not taking into great consideration is permissioning.
I tried to set up the objects in a way to make permissioning easier down the line. However, I had some trouble implementing it in postgres. As a result, there are some oddly placed workarounds.

In order to get this to run, the following steps will need to be run:

1. Run the following snippet:
```sql
CREATE SCHEMA AIRFLOW.WEATHER;
CREATE USER dag_operator WITH PASSWORD 'dag_operator';

set search_path to weather;
GRANT USAGE ON SCHEMA WEATHER TO DAG_OPERATOR;
ALTER USER dag_operator SET SEARCH_PATH = weather;
```
2. Create a connection in airflow using dag_operator
3. Upgrade to head in alembic `alembic upgrade head`
4. Grant privileges to dag_operator
```sql
grant usage, select on sequence dag_runs_run_id_seq to dag_operator;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA WEATHER TO dag_operator;
```

From there, both the fetcher and transformer dags can be run.


### Time spent
Give us a rough estimate of the time you spent working on this. If you spent time learning in order to do this project please feel free to let us know that too. This makes sure that we are evaluating your work fairly and in context. It also gives us the opportunity to learn and adjust our process if needed.

This took a decent amount of time, probably on the order of 6-8 hours. 

### Assumptions
Did you find yourself needing to make assumptions to finish this? If so, what were they and how did they impact your design/code?

1. Target database is postgres out of convenience, but in an actual deployment, we would use a columnar database.
2. Fetcher is being kept as a separate dag as its target would traditionally be a file store.
3. No end user has asked for anything specific -- yet. The goal is to set the ground work that's easily scalable not just with quantity of data but also by unpredictability of stakeholder request.

### Next steps
Provide us with some notes about what you would do next if you had more time. Are there additional features that you would want to add? Specific improvements to your code you would make?
1. Logger settings in alembic need to be adjusted
2. I set the ground work of notifications and monitoring, but not the actual implementation.
3. The next layer of views for stakeholders as defined by business use cases. I would create views on top of the t2 tables and provision access to the views.
4. Right now, the fetcher is bottlenecked by the number of calls it can make. If however, the bottleneck were to move to the amount of data within each call, this current implementation of row wise processing would be unperformant.
5. I added a place where data validation could be added, but no actual validation due to time constraints.
6. A current limitation: Running transformer on default parameters only ingests the weather data from the last fetcher run. Should be expanded to all runs that have been fetched but not transformed.
7. Users, roles and privileges
8. General cleanup -- There are a lot of hardcoded ids and names. I would really like to clean these up. Right now, changing a task id could have dangerous unpredictable consequences.
9. Tests
10. Use of binding variables and avoiding string formatting sql queries 

### Instructions to the evaluator
Provide any end user documentation you think is necessary and useful here
