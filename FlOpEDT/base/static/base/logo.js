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
     +----------------------------------------------------+
     |			^				  |
     |			| 50                              |
     |			v				  |
     |       +---------------+  +---------------+	  |
     |       |---------------|  |---------------|	  |
     |       |---------------|  |---------------|	  |
     |       |_______________|  |_______________|	  |
     | 							  |
     |<----->+---------------+  +---------------+	  |
     |  50   |---------------|  |---------------|	  |
     |       |---------------|  |---------------|	  |
     |       |_______________|  |_______________|	  |
     | 							  |
     |       +---------------+  +---------------+	  |
     |       |---------------|  |---------------|	  |
     |       |---------------|  |---------------|	  |
     |       |_______________|  |_______________|	  |
     | 							  |
     |                       1050                         |
     |<-------------------------------------------------->|
     +----------------------------------------------------+       
     */

var logo = {scale: .12,
	    init:{dim: 1000,
		  margin: 50},
	    get_current_dim: function () {
		return this.scale * this.init.dim ;},
	    get_current_margin: function () {
		return this.scale * this.init.margin ;}
	   }


var headlines =
    [ "Gestionnaire d'emploi du temps <span id=\"flopPasRed\">Fl"
        + "</span>exible et <span id=\"flopRed\">Op</span>enSource",
      "\"Qui veut faire les EDT cette année ?\" ... Fl"
      + "<span id=\"flopRed\">Op</span> !",
      "Et votre emploi du temps fera un "
      + "<span id=\"flopRedDel\">flop</span> carton !",
      "Et même votre logo sera à l'heure..." 
    ];


init_logo();


function init_logo() {
    fetch_logo();
    init_date();
    resize_logo();
    add_headline();
}


// fetch the logo and include it as svg
function fetch_logo(){
    var xhr = new XMLHttpRequest();
    xhr.open("GET",url_logo,false);
    xhr.overrideMimeType("image/svg+xml");
    xhr.send("");
    var lolo = document.getElementById("live-logo");
    lolo.appendChild(xhr.responseXML.documentElement);
}


// initialize the long and short hands of the logo
function init_date() {
    var d = new Date();
    var hm = new Array(2);
    hm[0] = 360*(d.getHours() % 12 + d.getMinutes()/60)/12;
    hm[1] = 360*(d.getMinutes()+d.getSeconds()/60)/60;
    console.log(hm);
    var anim = new Array(2);
    anim[0] = document.getElementById("csh")
	.getElementsByTagName("animateTransform")[0];
    anim[1] = document.getElementById("clh")
	.getElementsByTagName("animateTransform")[0];
    for (var i = 0 ; i<2 ; i++) {
	var from = anim[i].getAttribute("from").split(" ");
	from[0] = (+from[0]) + hm[i] ;
	anim[i].setAttribute("from", from.join(" "));
	var to = anim[i].getAttribute("to").split(" ");
	to[0] = (+to[0]) + hm[i] ;
	anim[i].setAttribute("to", to.join(" "));
    }
}


function resize_logo() {
    logo.svg = d3
	.select("#live-logo")
	.select("svg");
  
  
    logo.svg
	.select("#dims")
	.attr("transform", "scale(" + logo.scale + ")");
  
    logo.svg
	.attr("width", logo.get_current_dim() + logo.get_current_margin())
	.attr("height", logo.get_current_dim() + logo.get_current_margin());
}

function add_headline() {
    var draw = Math.floor(Math.random()*headlines.length);
    document.getElementById("head_logo").innerHTML = headlines[draw];
}
