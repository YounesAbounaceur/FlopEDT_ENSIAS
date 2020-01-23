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

/* INPUTS

var user = {nom: string,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: [],
	   };

var margin = {top: nb, left: nb, right: nb, bot: nb};

var svg = {height: nb, width: nb};

var week = nb ;
var year = nb;

var labgp = {height: nb, width: nb, tot: nb, height_init: nb, width_init: nb};

var dim_dispo = {height:2*labgp.height, width: 60, right: 10, plot:0,
		 adv_v_margin: 5};
*/
           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
-------  VAR GLOBALES  -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
           \     */

/*--------------------
   ------ ALL -------
  --------------------*/

// number of days in the week
var nbPer = 5;

// number of slots within 1 day
var nbSl = 6;

// initial number of promos
var init_nbRows = 2;

// current number of rows
var nbRows;
// last positive number of rows
var pos_nbRows = 0;

// maximum number of lab groups among promos
var rootgp_width = 0;
// last positive number of lab groups
var pos_rootgp_width = 0;

// different grounds where to plot
var fg, mg, bg, dg, meg, vg, gpg, prg, stg, mog, sag, fig, log, cmpg, cmtg;
var wg = {
    upper: null,
    bg: null,
    fg: null
};

// opacity of disabled stuffs
var opac = .4;


// status of fetching (cours_pl : cours placés, cours_pp : cours pas placés)
var fetch = {
    ongoing_cours_pl: false,
    ongoing_dispos: false,
    ongoing_cours_pp: false,
    ongoing_bknews: false,
    ongoing_un_rooms: false,
    done: false,
    cours_ok: false,
    dispos_ok: false
};
//cours_ok pas très utile


var svg_cont ;

/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// 3D array (username,id_day,id_slot)
var dispos = [];

// parameters for availability
var par_dispos = {
    nmax: 8, // maximum happiness
    adv_red: .7, // width of dd menu
    // compared to dispo cell
    rad_cross: .6, // radius of + circle
    // compared to smiley
    red_cross: .3 // length of + branches
        // compared to smiley
};

// parameters for the smileys
var smiley = {
    tete: 10,
    oeil_x: .35,
    oeil_y: -.35,
    oeil_max: .08,
    oeil_min: .03,
    bouche_x: .5,
    bouche_haut_y: -.1,
    bouche_bas_y: .6,
    sourcil: .4,
    init_x: 0,
    init_y: -180,
    max_r: 1,
    mid_o_v: 0xA5 * 100 / 255,
    mid_y_v: 0xE0 * 100 / 255,
    min_v: 0x90 * 100 / 255,
    rect_w: 1.1,
    rect_h: .3
};

// helper arrays for smileys
var data_dispo_adv_init = [];
for (var i = 0; i <= par_dispos.nmax; i++) {
    data_dispo_adv_init.push({
        day: 0,
        hour: 0,
        off: i
    });
}
var data_dispo_adv_cur = [];
var del_dispo_adv = false;

// number of required and provided availability slots
var required_dispos = -1;
var filled_dispos = -1;

// display only preferences
var pref_only ;

var dim_dispo = {
    height: 0,
    width: 60,
    right: 10,
    plot:0,
    adv_v_margin: 5
};


/*---------------------
  ------- WEEKS -------
  ---------------------*/
var weeks = {
    init_data: null,
    cur_data: null,
    width: 40,
    height: 30,
    x: 0,
    y: -240, //margin.but,  // - TOP BANNER - //
    ndisp: 13,
    fdisp: 0,
    sel: [1],
    rad: 1.2,
    hfac: 0.9,
    wfac: 0.9,
    cont: null
};

/*----------------------
  -------- GRID --------
  ----------------------*/

// one element per labgroup and per slot
// is filtered when bound
var data_mini_slot_grid = [];

// one element per slot
var data_slot_grid = [];

// keys on top or at the bottom of the grid representing the name of
// the labgroup
// (one element per labgroup and per day)
var data_grid_scale_gp = [];


// keys to the left representing the name of the row
//(one element per row and per hour)
var data_grid_scale_row = [];
var data_grid_scale_hour = ["8h-9h25", "9h30-10h55", "11h05-12h30", "14h15-15h40", "15h45-17h10", "17h15-18h40"];

// Names of the days
var data_grid_scale_day_init = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven."];
var data_grid_scale_day = ["Lun.", "Mar.", "Mer.", "Jeu.", "Ven."];

// Garbage parameters
var garbage = {
    // day: 3,
    // slot: nbSl,
    // cell: {
        day: 3,
        slot: nbSl,
        display: false,
        dispo: false,
        pop: false,
        reason: ""
//    }
};


/*----------------------
  ------- BKNEWS -------
  ----------------------*/

// bknews = breaking news
var bknews = {
    hour_bound:3, // flash info between hour #2 and hour #3
    ratio_height: .55,        // ratio over course height 
    ratio_margin: .15, // ratio over course height 
    cont: [],
    nb_rows: 0,
};

/*---------------------
  ------- QUOTE -------
  ---------------------*/

var quote = "" ;


/*----------------------
  ------- GROUPS -------
  ----------------------*/

// 2D data about groups (id_promo, group_subname)
var groups = [];


// access to the root of each promo, and to the groups belonging
// to the same line 
var root_gp = []; // indexed by numpromo
var row_gp = []; // indexed by numrow

// set of promo numbers
var set_promos = [];
// set of promo short description
var set_promos_txt = [];
// set of row numbers
var set_rows = [];

// display parameters
var butgp = {
    height: 20,
    width: 30,
    tlx: 640
};
var margin_but = {
    ver: 10,
    hor: 10
};

/*--------------------
  ------ MENUS -------
  --------------------*/
var menus = {
    x: weeks.x + 20,
    y: weeks.y + 25,
    mx: 20,
    dx: 280,
    h: 30,
    sfac: 0.4,
    ifac: 0.7,
    coled: 100,
    colcb: 140
};

var edt_but, edt_message;
// parameters for each checkbox
var ckbox = [];
ckbox["edt-mod"] = {
    i: 0,
    menu: "edt-mod",
    cked: false,
    txt: "Modifier",
    disp: true,
    en: true
};
ckbox["dis-mod"] = {
    i: 1,
    menu: "dis-mod",
    cked: false,
    txt: "Modifier",
    disp: true,
    en: true
};



var context_menu = {
    dispo_hold: false,
    room_tutor_hold: false
};

/*--------------------
   ------ MODULES ------
   --------------------*/
// modules (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var modules = {
    sel: "",
    pl: [],
    pp: [],
    all: []
};

/*--------------------
   ------ ROOMS ------
   --------------------*/
// salles (sel: selected, pl:scheduled (PLacé), pp: not scheduled (Pas Placé), all: all modules
var salles = {
    sel: "",
    pl: [],
    pp: [],
    all: []
};

var rooms ;


var unavailable_rooms = [] ;
unavailable_rooms = new Array(nbPer);
for (var i = 0; i < nbPer; i++) {
    unavailable_rooms[i] = new Array(nbSl);
}


/*---------------------
   ------ TUTORS ------
   --------------------*/

// instructors of unscheduled courses
var profs_pp = [];

// instructors of scheduled courses
var profs_pl = [];

// all instructors
var profs = [];

// instructors not blurried
var prof_displayed = [];

// display parameters
var butpr = {
    height: 30,
    width: 30,
    perline: 12,
    mar_x: 2,
    mar_y: 4,
    tlx: 900
};

// has any instructor been fetched?
var first_fetch_prof = true;

// all tutors (to propose changes)
var all_tutors = [] ;

/*--------------------
   ------ SCALE ------
  --------------------*/
// listeners for Horizontal Scaling and Vertical Scaling buttons
var drag_listener_hs, drag_listener_vs;

/*-----------------------
   ------ COURSES -------
  -----------------------*/
// unscheduled curses
var cours_pp = [];
// scheduled curses
var cours_pl = [];
// all curses
var cours = [];

// listener for curses drag and drop 
var dragListener;


// helper for the d&d
var drag = {
    sel: null,
    x: 0,
    y: 0,
    init: 0,
    svg: null,
    svg_w: 0,
    svg_h: 0
};

// stores the courses that has been moved
var cours_bouge = {};

/*----------------------
  ------- VALIDATE -----
  ----------------------*/

// display parameters
var valid = {
    margin_edt: 50,
    margin_h: 20,
    h: 40,
    w: 210
};

// acknowledgements when availability or courses are changed (ack.edt) ,
// or about the next possible regeneration of the planning (ack.regen)
var ack = {
    edt: "",
    regen: ""
};



/*--------------------
   ------ STYPE ------
  --------------------*/

// display parameters
var did = {
    h: 10,
    w: 15,
    mh: 5,
    mav: 10,
    tlx: 316,
    tly: -180
};
var stbut = {
    w: 104,
    h: 60
};

/*--------------------
   ------ ALL -------
  --------------------*/

// version of the planning
var version;

logged_usr.dispo_all_see = false ;
logged_usr.dispo_all_change = false ;


if ((logged_usr.rights >> 0) % 2 == 1) {
    logged_usr.dispo_all_see = true ;
}
if ((logged_usr.rights >> 1) % 2 == 1) {
    logged_usr.dispo_all_change = true ;
}
    
var user = {nom: logged_usr.nom,
	    dispos: [],
	    dispos_bu: [],
	    dispos_type: [],
	    dispo_all_see: false,
	    dispo_all_change: false
	   };

var total_regen = false ;


// 
var entry_cm_settings =
    {type: 'entry',
     w: 100,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 1,
     nlin: 2,
     txt_intro: {'default':"Quoi changer ?"}
    };
var tutor_module_cm_settings =
    {type: 'tutor_module',
     w: 45,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 3,
     nlin: 0,
     txt_intro: {'default':"Profs du module ?"}
    };
var tutor_filters_cm_settings =
    {type: 'tutor_filters',
     w: 120,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 1,
     nlin: 0,
     txt_intro: {'default':"Ordre alphabétique :"}
    };
var tutor_cm_settings =
    {type: 'tutor',
     w: 45,
     h: 18,
     fs: 10,
     mx: 5,
     my: 3,
     ncol: 3,
     nlin: 4,
     txt_intro: {'default':"Ordre alphabétique :"}
    };
var room_cm_settings =
    [{type: 'room_available',
      txt_intro: {'0':"Aucune salle disponible",
		  '1':"Salle disponible",
		  'default':"Salles disponibles"
		 }
     },
     {type: 'room_available_same_type',
      txt_intro: {'0':"Aucune salle disponible (tout type)",
		  '1':"Salle disponible (tout type)",
		  'default':"Salles disponibles (tout type)"
		 }
     },
     {type: 'room',
      txt_intro: {'0':"Aucune salle",
		  '1':"Salle",
		  'default':"Toutes les salles"
		 }
     }];
for(var l = 0 ; l < room_cm_settings.length ; l++) {
    room_cm_settings[l].w = 45 ;
    room_cm_settings[l].h = 18 ;
    room_cm_settings[l].fs = 10 ;
    room_cm_settings[l].mx = 5 ;
    room_cm_settings[l].my = 3 ;
    room_cm_settings[l].ncol = 3 ;
    room_cm_settings[l].nlin = 0 ;
}
// level=0: the proposed rooms are available and of the same type
//       1: the proposed rooms are available
//       2: all rooms are proposed
var room_cm_level = 0 ;

var room_tutor_change = {
    course: [],    // 1-cell array for d3.js
    proposal: [],
    old_value: "",  
    cur_value: "",
    cm_settings:{},
    top: 30,
    posv: 's',
    posh: 'w'
};

var arrow =
    {right: "→",
     back: "↩"} ;
