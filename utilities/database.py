import os
import psycopg2
####################################################################################################

__all__ = ("db_connection", "assert_database_entries")

####################################################################################################
# Environment variables

# DATABASE = os.environ.get("DATABASE_URL", None)
DATABASE = "postgres://jxnlptguidmjbk:2807ce5f05d595c4f06d27340fd8dad9de74fe1099f427ec1336293082f60832@ec2-44-208-88-195.compute-1.amazonaws.com:5432/d7jh5kaam0plun"
####################################################################################################
# Open database connection
# I prefer to create a cursor at the time of data query, so just
# setting up a connection is good for now

db_connection = psycopg2.connect(DATABASE, sslmode="require")
print("Database connection initialized...")

####################################################################################################
def assert_database_entries(guild_id: int) -> None:
    """Creates new records in all guild ID-dependant tables when the
    bot joins a new guild.
    """

    c = db_connection.cursor()

    c.execute(
        "INSERT INTO job_postings (guild_id) VALUES (%s) ON CONFLICT "
        "(guild_id) DO NOTHING",
        (guild_id, )
    )

    db_connection.commit()
    c.close()

    return

####################################################################################################
