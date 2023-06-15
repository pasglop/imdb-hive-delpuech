from time import sleep
from utils import fetchResult, execute_query
from tabulate import tabulate


def process_movie_table():
    print("On va travailler la table Movies...")

    print("Regardons la répartition des films par type...")
    query = "SELECT type, COUNT(*) as nb_record FROM imdb.movies GROUP BY type"
    results, headers = fetchResult(query)
    print(tabulate(results, headers, tablefmt='psql'))
    sleep(5)
    print("On pourrait partitionner la table Movies par type"
          " mais avec des Meta-types : movie, short, series, game...\n"
          " Partitionnement par année de sortie serait bien aussi"
          " mais cela crée une erreur d'execution (nbre de partitions??) ...\n"
          " Alors on va clusteriser sur l'année de sortie avec 10 buckets (un peu plus d'une décennie),"
          " ce qui permettra de permettre du traitement horizontal...")
    sleep(5)
    print("Ajoutons une colonne meta_type à la table Movies...")
    print("Créons une nouvelle table avec partitionnement sur metatype...")
    execute_query(
        "CREATE TABLE IF NOT EXISTS imdb.movies_partitionned (id VARCHAR(9), type VARCHAR(10), primaryTitle VARCHAR(100), originalTitle VARCHAR(100), "
        "isAdult BOOLEAN, startYear INT, "
        "endYear INT, runtimeMinutes INT, genres ARRAY<VARCHAR(20)>,"
        "PRIMARY KEY (id) DISABLE NOVALIDATE) PARTITIONED BY (meta_type VARCHAR(10))"
        "CLUSTERED BY (startYear) INTO 10 BUCKETS STORED AS ORC")
    print("On va remplir la table + colonne meta_type... Please Wait ~1mn...")
    execute_query(
        "INSERT INTO imdb.movies_partitionned PARTITION (meta_type) SELECT id, type, primaryTitle, originalTitle, "
        "isAdult, startYear, endYear, runtimeMinutes, genres, "
        "CASE "
        "   WHEN type in ('movie', 'tvMovie') THEN 'movie'"
        "   WHEN type in ('short', 'tvShort', 'tvMiniSeri', 'video') THEN 'short'"
        "   WHEN type in ('tvSeries', 'tvEpisode', 'tvSpecial', 'tvPilot') THEN 'series'"
        "   ELSE 'game' END as meta_type FROM imdb.movies", partition_mode=True)

    print("Controlons le nombre de films par meta_type...")
    query = "SELECT meta_type, COUNT(*) as nb_record FROM imdb.movies_partitionned GROUP BY meta_type"
    results, headers = fetchResult(query)
    print(tabulate(results, headers, tablefmt='psql'))
    sleep(5)
    results, headers = fetchResult("SHOW PARTITIONS imdb.movies_partitionned")
    print(tabulate(results, headers, tablefmt='psql'))
    print("On peut maintenant supprimer la table Movies...")
    execute_query("DROP TABLE imdb.movies")
    print("On peut maintenant renommer la table Movies_partitionned en Movies...")
    execute_query("ALTER TABLE imdb.movies_partitionned RENAME TO imdb.movies")

def process_genres():
    print("On va créer une table Genres à partir du tableau de genres de movies...\n")

    print("Créons une nouvelle table genres avec l'id du film et le genre.\n")
    print("On va partitionner sur le genre...\n")
    execute_query("CREATE TABLE IF NOT EXISTS imdb.movie_genres "
                  "(id VARCHAR(9)) PARTITIONED BY (genre VARCHAR(20)) STORED AS ORC")
    print("On va remplir la table genres... Please Wait...")
    execute_query("INSERT INTO imdb.movie_genres PARTITION (genre) "
                  "SELECT id, genre "
                  "FROM imdb.movies LATERAL VIEW explode(genres) exploded_table AS genre", partition_mode=True)

    results, headers = fetchResult("SHOW PARTITIONS imdb.movie_genres")
    print(tabulate(results, headers, tablefmt='psql'))

if __name__ == "__main__":
    # Partitionned tables
    process_movie_table()
    process_genres()

    print("Je m'arrête là pour aujourd'hui...\n"
          "Si insuffisant, j'ai d'autres idées dans le readme \n")



