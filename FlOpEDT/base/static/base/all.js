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

/*-------------------
  ---- VARIABLES ----
  -------------------*/



      // {"tot":15,
      //  "colors":[]},
      // {"tot":16,
      //  "colors":[]},
      // {"tot":18,
      //  "colors":[]},
      // {"tot":19,
      //  "colors":[]},
      // {"tot":20,
      //  "colors":[]}





var user = {nom: logged_usr.nom,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: []
	   };

var margin = {
    top: 250,     // - TOP BANNER - //
    left:  50,
    right:  110,
    bot:  10,
    but: -230
};


var bs_margin_w = 20 ;
var bs_margin_h = 5 ;

var svg = {
    height: window.innerHeight - $("#menu-edt").height() - bs_margin_h,
    width: window.innerWidth - bs_margin_w,
};


var week = 42 ;
var year = 2017;

var labgp = {height: 40, width: 30, tot: 8, height_init: 40, width_init: 30, hm: 40, wm:15};

dim_dispo.height = 2*labgp.height ;



butgp.tly = margin.but;//-margin_but.ver-6*butgp.height-80 ;
butpr.tly = margin.but;


modules.x=butpr.tlx+butpr_x(null,butpr.perline-2)+butpr.width+butpr.mar_x-60;
modules.y=margin.top+gsckd_y(null)-40;
modules.width = 170 ;
modules.height = 0 ;


salles.x=modules.x-1.2*modules.width ; //5*butpr.width;
salles.y=modules.y-modules.height;//.6*butpr.height;
salles.width = 150 ; 
salles.height = modules.height ; 

pref_only = false ;

/*-------------------
  ------ BUILD ------
  -------------------*/


function on_group_rcv(dg) {

    create_groups(dg);

    go_gp_buttons();

    create_edt_grid();

    create_alarm_dispos() ;
    create_val_but() ;
    create_regen() ;
    create_quote() ;
    
    go_ack_msg();

    create_bknews();

    go_promo_gp_init() ;
    go_gp_buttons();


    fetch_all(true);

    if (splash_id == 1) {
    
	var splash_mail = {
	    id: "mail-sent",
	    but: {list: [{txt: "Ok", click: function(d){} }]},
	    com: {list: [{txt: "E-mail envoyé !", ftsi: 23}]}
	}
	splash(splash_mail);

    } else if (splash_id == 2) {

	var splash_quote = {
	    id: "quote-sent",
	    but: {list: [{txt: "Ok", click: function(d){} }]},
	    com: {list: [{txt: "Citation envoyée ! (en attente de modération)", ftsi: 23}]}
	}
	splash(splash_quote);

    }
    
    //go_edt(true);
}


function on_room_rcv(room_data) {
    rooms = room_data;
}





/*-------------------------
  - CONTEXT MENUS HELPERS -
  -------------------------*/

function cancel_cm_adv_preferences(){
    if(ckbox["dis-mod"].cked) {
	if(! context_menu.dispo_hold) {
	    data_dispo_adv_cur = [] ;
	    go_cm_advanced_pref(true);
	}
	context_menu.dispo_hold = false ;
    }
}

function cancel_cm_room_tutor_change(){
    if(ckbox["edt-mod"].cked) {
	if(!context_menu.room_tutor_hold) {
	    if (room_tutor_change.course.length > 0) {
		room_tutor_change.course = [] ;
		room_tutor_change.proposal = [] ;
		go_cm_room_tutor_change();
	    }
	}
	context_menu.room_tutor_hold = false ;
    }
}


/*---------------------
  ------ STARTER ------
  ---------------------*/


create_general_svg(false);
create_quote()

def_drag();
def_cm_change();

create_clipweek();
create_menus();
create_forall_prof();

fetch_dispos_type();




d3.json(groupes_fi,
 	on_group_rcv);

d3.json(rooms_fi,
 	on_room_rcv);


    

d3.select("body")
    .on("click", function(d) {
	cancel_cm_adv_preferences();
	cancel_cm_room_tutor_change();
    })




