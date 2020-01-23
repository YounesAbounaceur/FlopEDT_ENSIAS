# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
# 
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

if [ $# -gt 1 ]
then
    echo "usage: $0 [name of the setting file]"
    echo "by default: local"
else
    SETTING_FILE="FlOpEDT.settings"
    if [ "$1" == "" ]
    then
	SETTING_FILE="$SETTING_FILE.local"
    else
	SETTING_FILE="$SETTING_FILE.$1"
    fi
    echo "Setting file: $SETTING_FILE"
    echo "ATTENTION -- WARNING -- ACHTUNG"
    echo "Tout ce qui se trouve sur cette base de donnée sera perdu"
    echo "Continuer ? (oui ?)"
    read rep
    if [ $rep = "oui" ]
    then
	SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	DB="$($SCRIPT_DIR/../manage.py shell --settings=$SETTING_FILE -c "from django.conf import settings ; print(settings.DATABASES['default']['NAME'])")"
	echo "Database name: $DB"

	sudo systemctl restart postgresql
    	sudo -u postgres psql -c 'drop database '"\"$DB\""
    	sudo -u postgres createdb "$DB"

	apps="base TTapp quote people solve_board"
	echo "Remove migrations from: $apps"
	for a in $apps
	do
	    mig=$a/migrations
	    for i in `ls $SCRIPT_DIR/../$mig --hide=__init__.py`
	    do
		rm $SCRIPT_DIR/../$mig/$i
	    done
	done
    	$SCRIPT_DIR/../manage.py makemigrations --settings=$SETTING_FILE
    	$SCRIPT_DIR/../manage.py migrate --settings=$SETTING_FILE
    fi
fi
