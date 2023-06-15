# Projet IMDB - Hive
## Auteur
- David DELPUECH

## Description
Ce projet a pour but de créer un cluster Hive avec des données provenant de IMDB.
Les données sont récupérées depuis le site [IMDB](https://www.imdb.com/interfaces/).
Les données sont ensuite stockées dans un cluster Hive.


## Utilisation

### Prérequis
- Docker
- Docker-compose
- Python 3
- Python virtualenv
- dotenv

### Lancement du projet
- Lancer le script `./install.sh`
- Faites-vous un café...


## Data Discovery
Les données sont disponibles sur le site [IMDB](https://www.imdb.com/interfaces/).
Les données sont disponibles au format TSV.
Les données sont disponibles au format GZIP.

### Data Discovery - Title Basics
- [Documentation](https://www.imdb.com/interfaces/#title_basics)
- [Fichier](https://datasets.imdbws.com/title.basics.tsv.gz)

| Champs         | Type         | Map Table   | Map type       | Commentaire                                 |
|----------------|--------------|-------------|----------------|---------------------------------------------| 
| tconst         | string       | movies.id   | varchar(9)     | Identifiant unique du film sur 9 caractères |
| titleType      | string       | movies.type | varchar        | Type du film                                |
| primaryTitle   | string       | movies      | varchar        | nom du film utilisé par le réalisateur      |
| originalTitle  | string       | movies      | varchar        | nom du film original                        |
| isAdult        | int          | movies      | bool           | 0 = non adulte, 1 = adulte                  |
| startYear      | YYYY         | movies      | int            | Année de sortie du film                     |
| endYear        | YYYY         | movies      | int            | Année de fin du film                        |
| runtimeMinutes | int          | movies      | int            | Durée du film en minutes                    |
| genres         | string array | movies      | ARRAY<VARCHAR> | Liste des genres du film                    |
Remarques :
- Le champ `tconst` est utilisé comme clé primaire
- Le champ `genres` est un tableau de string; il pourrait être intéressant de le transformer en tableau de genre avec une table de référence
- les champs NULL sont remplacés par `\N`, impact au chargement ?
- le partitionnement par année de sortie du film pourrait être intéressant

Partitions :
- type: titleType
- year: startYear via table movies_by_year

Table supplémentaire :
- genres: id, genre - généré à partir du champ `genres` de la table `movies` 
- movies_by_genre: id, genre, tconst - généré à partir du champ `genres` de la table `movies`
- movies_by_year: id, originalTitle, startYear - généré à partir du champ `startYear` de la table `movies`

### Data Discovery - Title Ratings
- [Documentation](https://www.imdb.com/interfaces/#title_ratings)
- [Fichier](https://datasets.imdbws.com/title.ratings.tsv.gz)

| Champs        | Type   | Map Table  | Map type   | Commentaire                                 |
|---------------|--------|------------|------------|---------------------------------------------|
| tconst        | string | ratings.id | varchar(9) | Identifiant unique du film sur 9 caractères |
| averageRating | float  | ratings    | float      | Note moyenne du film                        |
| numVotes      | int    | ratings    | int        | Nombre de votes                             |
Remarques :
- Le champ `tconst` peux être utilisé comme foreign key vers la table `movies`
- les champs NULL sont remplacés par `\N`, impact au chargement ?

clé étrangère : movies.id

### Data Discovery - Name Basics
- [Documentation](https://www.imdb.com/interfaces/#name_basics)
- [Fichier](https://datasets.imdbws.com/name.basics.tsv.gz)

| Champs            | Type         | Map Table    | Map type       | Commentaire                                        |
|-------------------|--------------|--------------|----------------|----------------------------------------------------|
| nconst            | string       | persons.id   | varchar(9)     | Identifiant unique de la personne sur 9 caractères |
| primaryName       | string       | persons.name | varchar        | Nom de la personne                                 |
| birthYear         | YYYY         | persons      | int            | Année de naissance de la personne                  |
| deathYear         | YYYY         | persons      | int            | Année de décès de la personne                      |
| primaryProfession | string array | persons      | ARRAY<VARCHAR> | Liste des professions de la personne               |
| knownForTitles    | string array | persons      | ARRAY<VARCHAR> | Liste des films connus de la personne              |
Remarques :
- Le champ `nconst` est utilisé comme clé primaire
- Le champ `knownForTitles` est un tableau de string; il pourrait être intéressant de créer une table many-to-many vers la  table movies
- les champs NULL sont remplacés par `\N`, impact au chargement ?


### Data Discovery - Title Crew
- [Documentation](https://www.imdb.com/interfaces/#title_crew)
- [Fichier](https://datasets.imdbws.com/title.crew.tsv.gz)

| Champs    | Type         | Map Table     | Map type       | Commentaire                                 |
|-----------|--------------|---------------|----------------|---------------------------------------------|
| tconst    | string       | crew.movie_id | varchar(9)     | Identifiant unique du film sur 9 caractères |
| directors | string array | crew          | ARRAY<VARCHAR> | Liste des réalisateurs du film              |
| writers   | string array | crew          | ARRAY<VARCHAR> | Liste des scénaristes du film               |
Remarques :
- Le champ `tconst` peux être utilisé comme foreign key vers la table `movies`
- les champs NULL sont remplacés par `\N`, impact au chargement ?
- Il y a des lignes avec des valeurs vides pour les champs `directors` et `writers`

clé étrangère : movies.id

### Data Discovery - Title Principals
- [Documentation](https://www.imdb.com/interfaces/#title_principals)
- [Fichier](https://datasets.imdbws.com/title.principals.tsv.gz)

| Champs     | Type         | Map Table            | Map type       | Commentaire                                        |
|------------|--------------|----------------------|----------------|----------------------------------------------------|
| tconst     | string       | principals.movie_id  | varchar(9)     | Identifiant unique du film sur 9 caractères        |
| ordering   | int          | principals           | int            | Ordre d'apparition dans le film                    |
| nconst     | string       | principals.person_id | varchar(9)     | Identifiant unique de la personne sur 9 caractères |
| category   | string       | principals           | varchar        | Catégorie de la personne dans le film              |
| job        | string       | principals           | varchar        | Travail de la personne dans le film                |
| characters | string array | principals           | ARRAY<VARCHAR> | Liste des personnages joués par la personne        |
Remarques :
- Le champ `tconst` peux être utilisé comme foreign key vers la table `movies`
- Le champ `nconst` peux être utilisé comme foreign key vers la table `persons`
- les champs NULL sont remplacés par `\N`, impact au chargement ?

clé étrangère : 
- movies.id
- persons.id

### Data Discovery - Title Episode
- [Documentation](https://www.imdb.com/interfaces/#title_episode)
- [Fichier](https://datasets.imdbws.com/title.episode.tsv.gz)

| Champs        | Type   | Map Table             | Map type   | Commentaire                                        |
|---------------|--------|-----------------------|------------|----------------------------------------------------|
| tconst        | string | episodes.movie_id     | varchar(9) | Identifiant unique du film sur 9 caractères        |
| parentTconst  | string | episodes.parent_movie | varchar(9) | Identifiant unique du film parent sur 9 caractères |
| seasonNumber  | int    | episodes              | int        | Numéro de la saison                                |
| episodeNumber | int    | episodes              | int        | Numéro de l'épisode                                |
Remarques :
- Le champ `tconst` peux être utilisé comme foreign key vers la table `movies`
- Le champ `parentTconst` peux être utilisé comme foreign key vers la table `movies`
- les champs NULL sont remplacés par `\N`, impact au chargement ?

### Data Discovery - Title Akas
- [Documentation](https://www.imdb.com/interfaces/#title_akas)
- [Fichier](https://datasets.imdbws.com/title.akas.tsv.gz)

| Champs          | Type    | Map Table     | Map type   | Commentaire                                 |
|-----------------|---------|---------------|------------|---------------------------------------------|
| titleId         | string  | akas.movie_id | varchar(9) | Identifiant unique du film sur 9 caractères |
| ordering        | int     | akas          | int        | Ordre d'apparition dans le film             |
| title           | string  | akas          | varchar    | Titre du film                               |
| region          | string  | akas          | varchar    | Région du film                              |
| language        | string  | akas          | varchar    | Langue du film                              |
| types           | string  | akas          | varchar    | Type du film                                |
| attributes      | string  | akas          | varchar    | Attributs du film                           |
| isOriginalTitle | boolean | akas          | boolean    | Est-ce le titre original du film            |
Remarques :
- Le champ `titleId` peux être utilisé comme foreign key vers la table `movies`
- les champs NULL sont remplacés par `\N`, impact au chargement ?
- le champs title peut contenir de caractères spéciaux, il faudra faire attention lors de l'importation
- un partitionnement par region et language pourrait être intéressant

clé étrangère : movies.id

Partitions :
- region
- language
