![Logo](./FlOpEDT/base/static/base/img/flop2.png)

FlOpEDT/FlOpScheduler est un outil de gestion
d'emplois du temps comprenant :
- une application web permettant aux utilisateurs
  * d'exprimer leurs contraintes et préférences
  * de modifier l'emploi du temps
- un moteur de génération d'emplois du temps qui respectent les contraintes et
maximisent la satisfaction générale.

![Aperçu de la vue d'accueil](./img/edt-accueil.jpg)
![Aperçu de la vue de changement des disponibilités (/préférences)](./img/edt-dispos.jpg)

## Licence

[AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html)

## Principales dépendances
- [Django](https://www.djangoproject.com/) pour le site
- [PostgreSQL](https://www.postgresql.org/) pour la base de données
- [PuLP](https://github.com/coin-or/pulp) pour la modélisation en ILP (Integer Linear Programming)
- Un solveur de ILP, e.g. [CBC](https://projects.coin-or.org/Cbc), [Gurobi](gurobi.com)
- [Redis](https://redis.io) pour le cache de Django (optionnel)

## Lancement de l'application dans Docker

Après l'installation de `docker` et `docker-compose`, lancez la
commande suivante :

`make start` (`make stop` pour arrêter l'application)

(En cas de

`ERROR: Couldn't connect to Docker daemon at http+docker://localhost - is it running?`

songez à une exécution en `sudo`.)

L'application sera accessible à l'adresse http://localhost:8000.

Vous pouvez importer la base de donnée de la façon suivante :

docker exec -it $(docker ps | grep dev_web_1 | awk '{ print $1 }') bash
FlOpEDT/manage.py shell --settings=FlOpEDT.settings.development

from misc.deploy_database.deploy_database import extract_database_file 
extract_database_file('database_file.xlsx','GenieLogiciel','GL')
 

Vous pourrez alors vous connecter avec l'utilisateur `root` et le mot
de passe `root`. Cet utilisateur possède les droits associés aux
responsables des emplois du temps. Pour la vision d'une personne
enseignante classique, utiliser l'un des autres login (En fait, tous
les utilisateurs ont le même mot de passe `passe` !).



## Contributions
- [Discuter](https://framateam.org/flopedt/)
- [Soulever une issue](https://framagit.org/FlOpEDT/FlOpEDT/issues)


