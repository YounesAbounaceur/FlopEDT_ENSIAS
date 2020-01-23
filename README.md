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

Vous pouvez importer le fichier [dump.json](./dump.json) (qui est une
base pour jouer avec l'interface) avec la commande :

`make init` 

Vous pourrez alors vous connecter avec l'utilisateur `MOI` et le mot
de passe `passe`. Cet utilisateur possède les droits associés aux
responsables des emplois du temps. Pour la vision d'une personne
enseignante classique, utiliser l'un des autres login (En fait, tous
les utilisateurs ont le même mot de passe `passe` !).

Les paramètres de la configuration courante se trouvent dans
`FlOpEDT/settings`. Par défaut, on utilise la configuration
`development`. On peut spécifier une autre configuration en modifiant
la variable d'environnement `CONFIG` comme suit :

`CONFIG=production make [build|init|start|stop]`

Dans cet exemple de configuration pour un environnement de production, il est nécessaire de définir la variable `SECRET_KEY=your_very_secret_key` dans le fichier `/docker/env/secret.env`.


## Contributions
- [Discuter](https://framateam.org/flopedt/)
- [Soulever une issue](https://framagit.org/FlOpEDT/FlOpEDT/issues)


