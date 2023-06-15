from utils import create_database, load_data

if __name__ == "__main__":
    try:
        # create database in Hive
        create_database()

        load_data("movies",
                  "id VARCHAR(9), type VARCHAR(10), primaryTitle VARCHAR(100), originalTitle VARCHAR(100), "
                  "isAdult BOOLEAN, startYear INT, "
                  "endYear INT, runtimeMinutes INT, genres ARRAY<VARCHAR(20)>,"
                  "PRIMARY KEY (id) DISABLE NOVALIDATE",
                  "title.basics.tsv")
        load_data("ratings",
                  "id VARCHAR(9), averageRating FLOAT, numVotes INT,"
                  "CONSTRAINT fk FOREIGN KEY (id) REFERENCES imdb.movies(id) DISABLE NOVALIDATE",
                  "title.ratings.tsv")
        load_data("persons",
                  "id VARCHAR(9), name VARCHAR(100), birthYear INT, deathYear INT, primaryProfession "
                  "ARRAY<VARCHAR(20)>, knownForTitles ARRAY<VARCHAR(20)>,"
                  "PRIMARY KEY (id) DISABLE NOVALIDATE",
                  "name.basics.tsv")
        load_data("crew",
                  "movie_id VARCHAR(9), directors ARRAY<VARCHAR(20)>, writers ARRAY<VARCHAR(20)>",
                  "title.crew.tsv")
        load_data("principals",
                  "movie_id VARCHAR(9), ordering INT, person_id VARCHAR(9), category VARCHAR(20), job VARCHAR(100), "
                  "characters ARRAY<VARCHAR(100)>",
                  "title.principals.tsv")
        load_data("episodes",
                  "movie_id VARCHAR(9), parent_movie VARCHAR(9), seasonNumber INT, episodeNumber INT",
                  "title.episode.tsv")
        load_data("akas",
                  "movie_id VARCHAR(9), ordering INT, title VARCHAR(100), "
                  "region VARCHAR(10), language VARCHAR(10), "
                  "types ARRAY<VARCHAR(20)>, attributes ARRAY<VARCHAR(20)>, isOriginalTitle BOOLEAN",
                  "title.akas.tsv"
                  )


    # CREATE TABLE IF NOT EXISTS imdb.genre STORED AS TEXTFILE AS select distinct t.genre from (select explode(genres) as genre from movies) t;

    except Exception as e:
        print(e)
