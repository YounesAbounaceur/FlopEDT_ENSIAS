// This file is part of the FlOpEDT/FlOpScheduler project.
// Copyright (c) 2017
// Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
// Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public
// License along with this program. If not, see
// <http://www.gnu.org/licenses/>.
// 
// You can be released from the requirements of the license by purchasing
// a commercial license. Buying such a license is mandatory as soon as
// you develop activities involving the FlOpEDT/FlOpScheduler software
// without disclosing the source code of your own applications.


/*
    HELPER : remove child nodes
*/
function removeChildNodes(parentNode){
    if(parentNode){
        while (parentNode.hasChildNodes()) {
            parentNode.removeChild(parentNode.firstChild);
         }            
    }
}


/*
    Display the department's tutor list with 
    their total number of hours of activity
*/
function displayTutorHours(data) {
    let container = d3.select('#statistics table')

    // Clear table    
    removeChildNodes(container.node());

    // Insert header 
    header = container.append('tr')
    header.append('th').text('Professeur')
    header.append('th').text('Nombre de cours')

    tutor =  container.selectAll('tr')
        .data(data)
        .enter()
        .append('tr')

    // Tutor name
    tutor
        .append('td')
        .text((d) => d[1])

    // Number of slots
    tutor
        .append('td')
        .text((d) =>  d[4])
}

/*
    Display the number of days of inactivity for each room
*/
function displayRoomActivity(data) {
    
    let container = d3.select('#statistics table')
    
    // Clear table
    removeChildNodes(container.node());

    // Insert header 
    header = container.append('tr')
    header.append('th').text('Salle')
    header.append('th').text('Nombre de jours')    

    rooms =  container.selectAll('tr')
        .data(data.room_activity)
        .enter()
        .append('tr')

    // Room name
    rooms
        .append('td')
        .text((d) => d.room)

    // Number of days of inactivity
    rooms
        .append('td')
        .text((d) => d.count)
}

/*
    Global method to display 
*/
function displayStatistic(label){
    let statistic = available_statistics[label]
    if(statistic){
        // TODO : loading

        // Request server to get datas
        fetchStatistcs(statistic.url, statistic.callback);
    }
}

function changeStatisticEventHandler(event){
    displayStatistic(event.target.value);
}

/*
    Global method to request statistics 
*/
function fetchStatistcs(url, callback) {
    show_loader(true);
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: url,
        async: true,
        contentType: "text/json",
        success: function (value) {
            callback(value);
        },
        error: function (xhr, error) {
            console.log(xhr);
            console.log(error);
        },
        complete: function(){
            show_loader(false);
        }
    });
}

/*
    Initialization
*/
function init(){
    statisticContainer = document.querySelector('#statistics');
    
    statisticSelect = document.querySelector('#select_statistic');
    statisticSelect.onchange= changeStatisticEventHandler;

    displayStatistic(statisticSelect.options[statisticSelect.selectedIndex].value);
}

/*
    Main process
*/
var statisticContainer;
var statisticSelect;

var available_statistics = {
    'room_activity': {
        url: statistics_urls['room_activity'], 
        callback: displayRoomActivity,
    },
    'tutor_hours': {
        url: statistics_urls['tutor_hours'],
        callback: displayTutorHours,
    },
}

document.addEventListener('DOMContentLoaded', init);
