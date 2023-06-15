from tabulate import tabulate
from utils import fetchResult


def query_movies():
    print("Querying movies...")
    print("Comptons le nombre de films (movie) par année...")
    query = "SELECT startYear, COUNT(*) as nb_record FROM imdb.movies WHERE meta_type = 'movie' GROUP BY startYear"
    results, headers = fetchResult(query)
    print(tabulate(results, headers, tablefmt='psql'))


    print("Regardons les genres des films depuis 10 ans...")
    query = "WITH recentmovies AS (SELECT id, startYear FROM imdb.movies WHERE meta_type = 'movie' and startYear between 2012 and 2022)"\
            "SELECT startYear, genre, COUNT(*) as nb_record " \
            "FROM recentmovies " \
            "INNER JOIN imdb.movie_genres using(id)" \
            "GROUP BY startYear, genre"
    results, headers = fetchResult(query)
    print(tabulate(results, headers, tablefmt='psql'))

if __name__ == "__main__":
    query_movies()

    print("Je ne vais pas plus loin dans l'analyse des données "
          "car je n'ai d'objectif précis pour le moment...\n"
            "Si insuffisant, j'ai d'autres idées dans le readme \n")

    print("merci !!!")