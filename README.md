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
@TODO: Add any additional notes / documentation in this file.

The task, the way the DAGs were set up, seemed to indicate that we create the table and then insert into it directly, from the JSON reponse we get from the PythonOperator. My thought is that DDL operations should be independent of any orchestration and to create the table ahead of time and then run code to write into it. With this in mind, my Python script uses the Pandas library to create a dataframe from the API response and insert the record into the table. The modeled table - current_weather - is meant to be a reporting-ready table - with meaningful column names and some additional columns to have Fahrenheit versions of temperatures and wind speeds in miles per hour, in addition to the standard Celsius and meters per second, respectively. 

For fetcher.py - Given the way the DAG is set up, I structured it so the raw table's DDL is the first step - so that the table is created - and the second step is the invocation to the Python script.
For transformer.py - The first step creates the reporting-ready table and the second table writes into it selecting only those records that haven't been written into it yet.

### Time spent
Give us a rough estimate of the time you spent working on this. If you spent time learning in order to do this project please feel free to let us know that too. This makes sure that we are evaluating your work fairly and in context. It also gives us the opportunity to learn and adjust our process if needed.

Time spent - I spent about 10 hours in developing the solution and 3 hours troubleshooting an issue I was running into with Docker, spread across 3 days from Monday to Wednesday. I am not too familiar with Docker and so I might have spent less time debugging was I more familiar. The 10 hours included reading up documentation, testing out 2 approaches to determine which would easier/better, and learning exactly how to use json_normalize in Pandas.

### Assumptions
Did you find yourself needing to make assumptions to finish this? If so, what were they and how did they impact your design/code?

Assumptions - Given that we get a JSON body back, there were two options - write to Postgres directly and then deal with parsing it there, or figure out the schema ahead of time, parse it first and then write out to a structured table. I took a look at the JSON functions in Postgres and while technically possible, I could see that it would get gnarly very quickly if we went the SQL-only route of breaking up the JSON body. Added to this, was the consideration to take into account that not all fields that *could* be part of the response actually *would* be part of it. For example, if it is not raining in a particular place at the time we request weather for, it simply wouldn't show up in the response. Rather than handle all these cases in SQL, I decided to go the Python route.

While we know that we use JSON format to have loosely structured data, we also know that OpenWeather has a set schema of all possible elements that would make up the response body. Using that, I created the raw_current_weather table, and included the raw JSON response as well, in case someone wants to access the raw JSON, as opposed to the broken up columns. I tested this with a few different places with rain and snow to confirm we see all elements and that I was setting the schema the right way. 

In terms of the table design, I figured a modeled table would be one which we could point a dashboarding tool against and get insights, and with that in mind, I drop a few columns (id, icon etc) and rename a bunch of others, and transform a few more. One could argue that the transformation should/could be pushed down a level to the dashboarding layer, but it really depends on organizational needs, and either approach work and are equally valid, in my opinion. I chose to add extra columns to showcase that it could be done. 

For data scientists or engineers, they can access the raw_current_weather table to either get all the raw columns, or work directly with the JSON body, if need be. Data analysts/BI developers can use the current_weather table to derive insights, and still have the flexibility to use SQL and query the raw table to get any bits of information not present in the modeled table. 

### Next steps
Provide us with some notes about what you would do next if you had more time. Are there additional features that you would want to add? Specific improvements to your code you would make?

Ideally, only a single DAG with two steps would exist - the first step would run the Python code and the second step would run the process_raw_weather_data.sql file. The creation of the tables would be completely behind the scenes and outside of Airflow's purview.

### Instructions to the evaluator
Provide any end user documentation you think is necessary and useful here