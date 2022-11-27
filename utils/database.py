import os
import psycopg2
######################################################################
# Environment variables

# DATABASE = os.environ.get("DATABASE_URL", None)
DATABASE = "postgres://kmimzucrgrmugj:927f0949a0ff70bced12082f2597a99d543748a395e2b4455c3ac18b1e2607ca@ec2-3-229-161-70.compute-1.amazonaws.com:5432/d1o6dilasbh8t5"

######################################################################
# Open database connection
# I prefer to create a cursor at the time of data query, so just
# setting up a connection is good for now

connection = psycopg2.connect(DATABASE, sslmode="require")
print("Database connection initialized...")

######################################################################
def assert_database_entries(guild_id: int) -> None:
    """Creates new records in all guild ID-dependant tables when the
    bot joins a new guild.
    """

    c = connection.cursor()

    c.execute(
        "INSERT INTO job_postings (guild_id) VALUES (%s) ON CONFLICT "
        "(guild_id) DO NOTHING",
        (guild_id, )
    )

    connection.commit()
    c.close()

    return

######################################################################
