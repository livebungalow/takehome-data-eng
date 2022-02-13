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

Thoughts below.

### Time spent
> Give us a rough estimate of the time you spent working on this. If you spent time learning in order to do this project please feel free to let us know that too. This makes sure that we are evaluating your work fairly and in context. It also gives us the opportunity to learn and adjust our process if needed.

About 3 hours total, spread out in chunks (might have been faster if I did it all continuously and didn't have to context switch back from other tasks):

- A good chunk of time was spent on:
    - Trying to understand the problem, the scope (asked questions via email)
    - Refreshing Airflow knowledge (got burned because I forgot to define the Postgres connection in UI)
    - Reading docs on Airflow and the API
    - Reading through the docker-compose
    - Forget the nuances of passing/accessing context/XCom, played around with it a bit

- Probably spent a bit more time than necessary on structuring the files (did some juggling and mind changing on whether to write the SQL inline in the DAG files or make external) and adding type annotations

- Spent time thinking:
    - about the structure of the raw/staging table and the mart/modelled table
    - idempotency, different approaches to achieve this, ease of maintenance

- Remaining time coding

### Assumptions
> Did you find yourself needing to make assumptions to finish this? If so, what were they and how did they impact your design/code?

Yes - lots. There was a lot of open endedness, and in practice, I'd be bothering the hell out of PM or stakeholder to refine these assumptions and really understand what is needed here.

- It wasn't really clear how many cities or locations, and over what time frame you wanted the data pulled for and at what frequency. The API also has rate limits so I didn't want to run it over a period of time for testing. Ultimately I decided to assume (after checking in with Carly who relayed to Saeed) that a list of city IDs would be passed into the ingestion tasks, and that the list of said IDs wouldn't be too large to fit in memory. Performance might need to be considered depending on how frequently you wanted the API to run. In the email, you said "record per day", which seems sort of infrequent; I set up the schedule interval to be every 2 hours.

- Idempotency and retry policy (especially if a failure happened) was something to think about; we'd also need to consider the gaps that would happen if we had multiple city IDs; the first city ID would get a weather earlier than the Nth; if N is large, then city N's API call might occur a fair bit later than the first city. For simplicity, I assumed we're OK with negligible delay between the cities. Also, I designed transformer to run independently to fetcher (i.e. transformer will be idempotent if fetcher does nothing or fails).

- General note: I noticed some weirdness with the API; if I called on the same city a few seconds apart, sometimes the `dt` value on the second call would be *earlier* than the one on the first. The way I designed the ingestion/upsert into the table should handle this under the assumption that we're not caring about by the second resolution.

- Persistence/fault tolerance; a common practice is to actually dump the ingestion step data into flat files in some storage (S3, say). Under my assumption that we'd be running on a not very large set of city IDs, at a not too frequent interval, I stuck with keeping things in memory. If things get really big, it might make sense to instead have the ingestion task simply stream to file(s), and then the loading could happen in a separate task or DAG at a later time in some batch manner (since at that point we've already stored the "true" data and can access it). I added the possibility to do this in a rudimentary manner via a flag to one of the DAG task callables. We could then use sensors to read from files instead of passing via memory.

- I assumed the API would always return `id`, `dt`, and `timezone` in the payload, and that these are not null, which I feel are reasonable assumptions given the nature of the data. To give myself flexibility, we store the entire payload as a raw JSONB column too (a more ELT approach), which assumes that the payload is JSON serializable. We can then perform transformations inside the database itself instead with SQL, instead of having to manage brittle ETL code to account for possible future changes in the API payload shape (i.e. we just need to update our SQL to account for changes after some time, and the pipeline keeps running, instead of having it break or having to update code). One gap is that if the payload changes, the transformation step (SQL) will just have NULL for specific fields in the modelled table; we could either set those columns to be NOT NULL to have the tasks fail at the transformer DAG, or we could add JSON validation in the fetcher DAG.

- I assumed the composite primary key on the tables would be a sufficient enough index for our use cases and queries (get the weather of a city at a given time). This wouldn't be so much an issue with a DWH/OLAP type database like Snowflake or BigQuery. It's probably important to get this right near the creation of the table, as it's not always great (depending on the table) to add an index after the table is used in production and has grown big, as it can block writes (though we could build the indexes concurrently).

- I assumed we could model our problems in one raw table and one mart/cleaned modelling table. The level of normalization to take depends on a lot of factors. I decided to keep things simple. If we wanted to get fancy we could use Kimball modelling to break out the city/weather/temperature dimensions out into separate dimension tables.

### Next steps
> Provide us with some notes about what you would do next if you had more time. Are there additional features that you would want to add? Specific improvements to your code you would make?

E2E tests of the actual pipeline, focusing on covering edge cases.

Depending on need, investigate using Branching to cover certain failure cases.

More logging, alert system.

Further requirements gathering about the intended use case of the downstream dataset - access patterns, who specifically is using it, etc.

Decide if we want to use something like an ExternalTaskSensor for custom dependency logic between fetcher and transformer.

### Instructions to the evaluator

The one test file assumes `pytest` is installed on the evaluator's machine (i.e. I'm not testing it using the docker container)

