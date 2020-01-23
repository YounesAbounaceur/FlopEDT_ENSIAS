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



           /*     \
          ----------           
        --------------         
      ------------------       
    ----------------------     
  --------------------------   
------------------------------ 
-------     ACTIONS    -------
------------------------------ 
  --------------------------   
    ----------------------     
      ------------------       
        --------------         
          ----------           
                 */



/*--------------------------
  ------- PREFERENCES ------
  --------------------------*/

// apply pref change when simple mode
function apply_change_simple_pref(d) {
    if (pref_only || ckbox["dis-mod"].cked) {
        if (Math.floor(d.val % (par_dispos.nmax / 2)) != 0) {
            d.val = Math.floor(d.val / (par_dispos.nmax / 2)) * par_dispos.nmax / 2;
        }
        d.val = (d.val + par_dispos.nmax / 2) % (3 * par_dispos.nmax / 2);
        dispos[user.nom][d.day][d.hour] = d.val;
        user.dispos[day_hour_2_1D(d)].val = d.val;
        go_pref(true);
    }
}

/*---------------------
  ------- WEEKS -------
  ---------------------*/

// move timeline to the left
function week_left() {
    if (weeks.fdisp > 0) {
        weeks.fdisp -= 1;
        weeks.cur_data.pop();
        weeks.cur_data.unshift(weeks.init_data[weeks.fdisp]);
    }
    go_week_menu(false);
}

// move timeline to the right
function week_right() {
    if (weeks.fdisp + weeks.ndisp + 2 < weeks.init_data.length) {
        weeks.fdisp += 1;
        weeks.cur_data.splice(0, 1);
        weeks.cur_data.push(weeks.init_data[weeks.fdisp + weeks.ndisp + 1]);
    }
    go_week_menu(false);
}


// change week
// Not sure ok even if user is quick (cf fetch_cours)
function apply_wk_change(d, i) { //if(fetch.done) {
    if (i > 0 && i <= weeks.ndisp) {
        weeks.sel[0] = i + weeks.fdisp;
    }
    dispos = [];
    user.dispos = [];

    fetch_all(false);

    go_week_menu(false);
} //}



/*----------------------
  -------- GRID --------
  ----------------------*/

// clear pop message when unauthorized course modification
function clear_pop(gs) {
    if (gs.pop) {
        gs.pop = false;
        gs.display = false;
        gs.reason = "";
        go_grid(false);
    }
}


/*--------------------
  ------- ROOMS ------
  --------------------*/


// return: true iff a change is needed (i.e. unassigned room or already occupied) (or level>0)
function select_room_change() {
    var level = room_cm_level;
    room_tutor_change.cm_settings = room_cm_settings[level] ;

    var c = room_tutor_change.course[0] ;
    room_tutor_change.old_value = c.room ;
    room_tutor_change.cur_value = c.room ;

    var busy_rooms, cur_roomgroup, is_occupied, proposed_rg, initial_rg ;
    var i, j ;

    proposed_rg = [] ;

    if (level < room_cm_settings.length - 1) {

	// find rooms where a course take place
	var simultaneous_courses = cours
	    .filter(function(d) {
		return d.day==c.day && d.slot==c.slot && d.id_cours!=c.id_cours ;
	    });
	var occupied_rooms = [] ;
	for (i = 0 ; i < simultaneous_courses.length ; i++) {
	    busy_rooms = rooms.roomgroups[simultaneous_courses[i].room] ;
	    for (j = 0 ; j<busy_rooms.length ; j++) {
		if (occupied_rooms.indexOf(busy_rooms[j])==-1) {
		    occupied_rooms.push(busy_rooms[j]) ;
		}
	    }
	}


	if (level == 0) {
	    initial_rg = rooms.roomtypes[c.room_type] ;
	} else if (level == 1) {
	    initial_rg = Object.keys(rooms.roomgroups) ;
	} else {
	    // should not go here
	    initial_rg = [] ;
	}
	for (i = 0 ; i < initial_rg.length ; i++) {
	    cur_roomgroup = initial_rg[i] ;
	    if (is_garbage(c.day,c.slot)
		|| unavailable_rooms[c.day][c.slot]
		.indexOf(cur_roomgroup) == -1) {

		// is a room in the roomgroup occupied?
		is_occupied = false ;
		j = 0;
		while(!is_occupied
		      && j<rooms.roomgroups[cur_roomgroup].length) {
		    is_occupied = (occupied_rooms
				   .indexOf(rooms.roomgroups[cur_roomgroup][j])
				   != -1);
		    j++ ;
		}

		if(!is_occupied) {
		    proposed_rg.push(initial_rg[i]);
		}
	    }
	}

    } else {
	proposed_rg = Object.keys(rooms.roomgroups) ;
    }


    // atomic rooms first, then composed
    var rg, atomic_rooms, composed_rooms, room;
    atomic_rooms = [];
    composed_rooms = [];
    var fake_id = new Date() ;
    fake_id = fake_id.getMilliseconds() + "-" + c.id_cours ;
    room_tutor_change.proposal = [] ;

    for (rg = 0 ; rg < proposed_rg.length ; rg++) {
	room = {fid: fake_id, content: proposed_rg[rg]} ;
	if(rooms.roomgroups[room.content].length == 1) {
	    atomic_rooms.push(room);
	} else {
	    composed_rooms.push(room);
	}
    }
    room_tutor_change.proposal = atomic_rooms.concat(composed_rooms);

    if(level < room_cm_settings.length - 1) {
	room_tutor_change.proposal.push({fid: fake_id, content: "+"});
    }

    room_tutor_change.cm_settings.nlin
	= Math.ceil(room_tutor_change.proposal.length
		    / room_tutor_change.cm_settings.ncol) ;

    if (level > 0 || c.room == une_salle ||
	occupied_rooms.indexOf(c.room) != -1) {
	return true;
    } else {
	return false ;
    }

}


function confirm_room_change(d){
    var c = room_tutor_change.course[0] ;
    add_bouge(c);
    c.room = d.content;
    //room_tutor_change.cur_value = d.room;
    room_tutor_change.course = [] ;
    room_tutor_change.proposal = [] ;
    go_courses() ;
}



/*---------------------
  ------- TUTORS ------
  ---------------------*/

// apply changes in the display of tutor pr
function apply_tutor_display(pr) {
    if (fetch.done) {
	if(logged_usr.dispo_all_change && ckbox["dis-mod"].cked){
	    prof_displayed = [pr] ;
	    user.nom = pr ;
	    create_dispos_user_data() ;
	    go_pref(true) ;
	} else {
            if (prof_displayed.indexOf(pr) > -1) {
		if (prof_displayed.length == profs.length) {
                    prof_displayed = [pr];
		} else {
                    var ind = prof_displayed.indexOf(pr);
                    prof_displayed.splice(ind, 1);
                    if (prof_displayed.length == 0) {
			prof_displayed = profs.slice(0);
                    }
		}
            } else {
		prof_displayed.push(pr);
            }
	}

            go_tutors();
    }
}


// display all tutors
function apply_tutor_display_all() {
    if (fetch.done
	&& (!logged_usr.dispo_all_change || !ckbox["dis-mod"].cked)) {
        prof_displayed = profs.slice(0);
        go_tutors();
    }
}


function fetch_all_tutors() {
    if(all_tutors.length == 0) {
	show_loader(true);
	$.ajax({
            type: "GET",
            dataType: 'json',
            url: url_all_tutors,
            async: false,
            contentType: "application/json; charset=utf-8",
            success: function (msg) {
		all_tutors = msg.tutors.filter(function(d) {
		    return d>'A';
		});
		all_tutors.sort();
		show_loader(false);
            },
	    error: function(msg) {
		console.log("error");
		show_loader(false);
	    },
	    complete: function(msg) {
		console.log("complete");
	    }
	});
    }
}



function select_tutor_module_change() {
    room_tutor_change.cm_settings = tutor_module_cm_settings ;

    var c = room_tutor_change.course[0] ;
    room_tutor_change.old_value = c.prof ;
    room_tutor_change.cur_value = c.prof ;

    var tutor_same_module = cours
	.filter(function(c) {
	    return c.mod == room_tutor_change.course[0].mod;
	})
	.map(function(c){ return c.prof; });

    // remove duplicate 
    tutor_same_module = tutor_same_module.filter(function(t,i) {
	return tutor_same_module.indexOf(t)==i ;
    }) ;

    var fake_id = new Date() ;
    fake_id = fake_id.getMilliseconds() + "-" + c.id_cours ;
    room_tutor_change.proposal = [] ;

    room_tutor_change.proposal = tutor_same_module.map(function(t) {
	return {fid: fake_id, content: t};
    });

    room_tutor_change.proposal.push({fid: fake_id, content: "+"});

    room_tutor_change.cm_settings.nlin = Math.ceil(room_tutor_change.proposal.length / room_tutor_change.cm_settings.ncol) ;

}


function select_tutor_filters_change() {
    room_tutor_change.cm_settings = tutor_filters_cm_settings ;

    var c = room_tutor_change.course[0] ;

    var chunk_size = tutor_cm_settings.ncol * tutor_cm_settings.nlin - 2 ;

    var rest = all_tutors.length % chunk_size ;

    room_tutor_change.proposal = [] ;
    
    var i = 0 ; var i_end ;
    while(i < all_tutors.length) {
	i_end = i + chunk_size - 1 ;
	if(rest > 0) {
	    i_end++;
	    rest--;
	} 
	room_tutor_change.proposal.push(all_tutors[i]
					+ arrow.right
					+ all_tutors[i_end]);
	i = i_end + 1 ;
    }
    
    var fake_id = new Date() ;
    fake_id = fake_id.getMilliseconds() + "-" + c.id_cours ;
    room_tutor_change.proposal = room_tutor_change.proposal.map(function(t) {
	return {fid: fake_id, content: t};
    });

    room_tutor_change.cm_settings.nlin = Math.ceil(room_tutor_change.proposal.length / room_tutor_change.cm_settings.ncol) ;

}

function select_tutor_change(f) {
    room_tutor_change.cm_settings = tutor_cm_settings ;

    
    var c = room_tutor_change.course[0] ;

    var ends = f.content.split(arrow.right);

    room_tutor_change.proposal = all_tutors.filter(function(t) {
	return t >= ends[0] && t <= ends[1] ;
    });

    room_tutor_change.proposal.push(arrow.back) ;
    
    var fake_id = new Date() ;
    fake_id = fake_id.getMilliseconds() + "-" + c.id_cours ;
    room_tutor_change.proposal = room_tutor_change.proposal.map(function(t) {
	return {fid: fake_id, content: t};
    });

}


// unicode →


function confirm_tutor_change(d){
    var c = room_tutor_change.course[0] ;
    add_bouge(c);
    c.prof = d.content;
    //room_tutor_change.cur_value = d.room;
    room_tutor_change.course = [] ;
    room_tutor_change.proposal = [] ;
    go_courses() ;
}





function go_cm_room_tutor_change() {

    var tut_cm_course_dat = cmtg
        .selectAll(".cm-chg")
        .data(room_tutor_change.course,
              function(d) {
                  return d.id_cours;
              });
    
    var tut_cm_course_g = tut_cm_course_dat
        .enter()
        .append("g")
        .attr("class", "cm-chg")
        .attr("cursor", "pointer");
    

    tut_cm_course_g
        .append("rect")
        .attr("class", "cm-chg-bg")
        .merge(tut_cm_course_dat.select(".cm-chg-bg"))
        .attr("x", cm_chg_bg_x)
        .attr("y", cm_chg_bg_y)
        .attr("width", cm_chg_bg_width)
        .attr("height", cm_chg_bg_height)
        .attr("fill", "white");
        // .attr("stroke", "darkslategrey")
        // .attr("stroke-width", 2);

    tut_cm_course_g
        .append("text")
        .attr("class", "cm-chg-comm")
        .merge(tut_cm_course_dat.select(".cm-chg-comm"))
        .attr("x", cm_chg_txt_x)
        .attr("y", cm_chg_txt_y)
        .text(cm_chg_txt);
        // .attr("stroke", "darkslategrey")
        // .attr("stroke-width", 2);

    tut_cm_course_dat.exit().remove();



    var tut_cm_room_dat = cmtg
        .selectAll(".cm-chg-rooms")
        .data(room_tutor_change.proposal,
              function(d,i) {
                  return d.fid + "-" + i;
              });
    
    var tut_cm_room_g = tut_cm_room_dat
        .enter()
        .append("g")
        .attr("class", "cm-chg-rooms")
        .attr("cursor", "pointer")
	.on("click", room_tutor_change.cm_settings.click);
    

    tut_cm_room_g
        .append("rect")
        .attr("class", "cm-chg-rec")
        .merge(tut_cm_room_dat.select(".cm-chg-rec"))
        .attr("x", cm_chg_but_x)
        .attr("y", cm_chg_but_y)
        .attr("width", cm_chg_but_width)
        .attr("height", cm_chg_but_height)
        .attr("fill", cm_chg_but_fill)
        .attr("stroke", "black")
        .attr("stroke-width", cm_chg_but_stk);

    tut_cm_room_g
        .append("text")
        .attr("class", "cm-chg-bt")
        .merge(tut_cm_room_dat.select(".cm-chg-bt"))
        .attr("x", cm_chg_but_txt_x)
        .attr("y", cm_chg_but_txt_y)
        .text(cm_chg_but_txt);
        // .attr("stroke", "darkslategrey")
        // .attr("stroke-width", 2);

    tut_cm_room_dat.exit().remove();

    
}



/*----------------------
  ------- GROUPS -------
  ----------------------*/


var is_no_hidden_grp = true;

function check_hidden_groups() {
    is_no_hidden_grp = true;
    for (var a in groups) {
        for (var g in groups[a]) {
            if (groups[a][g].display == false) {
                is_no_hidden_grp = false;
                return;
            }
        }
    }
}

function are_all_groups_hidden() {
    // if all groups are hidden
    // all groups are automatically displayed
    for (var a in groups) {
        for (var g in groups[a]) {
            if (groups[a][g].display == true) {
                return;
            }
        }
    }
    set_all_groups_display(true);
}

function set_all_groups_display(isDisplayed) {
    for (var a in groups) {
        for (var g in groups[a]) {
            groups[a][g].display = isDisplayed;
        }
    }
}


// apply changes in the display of group gp
// start == true iff a particular group is chosen by a GET request
// go_button == true iff the group buttons are to be updated
function apply_gp_display(gp, start, go_button) {
    if (fetch.done || start) {
        if (is_no_hidden_grp) {
            set_all_groups_display(false);
            gp.display = true;
        } else {
            gp.display = !gp.display;
        }

        propagate_display_up(gp, gp.display);
        propagate_display_down(gp, gp.display);

        are_all_groups_hidden(); // all hidden => all displayed
        check_hidden_groups();

        update_all_groups();
	if (go_button) {
            go_gp_buttons();
	}
    }
    if (fetch.done) {
        go_edt();
    }
}


// set to boolean b the attribute display of every group
// that is a descendant of gp, gp included
function propagate_display_down(gp, b) {
    gp.display = b;
    for (var i = 0; i < gp.children.length; i++) {
        propagate_display_down(groups[gp.promo][gp.children[i]], b);
    }
}

// set to boolean b the attribute display of every group
// that is an ancestor of gp, gp included
function propagate_display_up(gp, b) {
    gp.display = b;
    if (gp.parent != null) {
        if (b) { // ancestors should be displayed too 
            propagate_display_up(groups[gp.promo][gp.parent], true);
        } else { // is there any sibling still displayed?
            var i = 0;
            var hidden_child = true;
            while (hidden_child && i < groups[gp.promo][gp.parent].children.length) {
                if (groups[gp.promo][groups[gp.promo][gp.parent].children[i]].display) {
                    hidden_child = false;
                } else {
                    i += 1;
                }
            }
            if (hidden_child) {
                propagate_display_up(groups[gp.promo][gp.parent], false);
            }
        }
    }
}


/*--------------------
  ------ MENUS -------
  --------------------*/

// apply the updates resulting from a change in a checkbox
function apply_ckbox(dk) {
    if (ckbox[dk].en && fetch.done) {

        if (ckbox[dk].cked) {
            ckbox[dk].cked = false;
        } else {
            ckbox[dk].cked = true;
        }

        if (dk == "dis-mod") {
            if (ckbox[dk].cked) {
                //create_dispos_user_data();
                //ckbox["dis-mod"].disp = true;
                stg.attr("visibility", "visible");

                dim_dispo.plot = 1;
                if (rootgp_width != 0) {
                    labgp.width *= 1 - (dim_dispo.width + dim_dispo.right) / (rootgp_width * labgp.width);
                }
		
                // if (!fetch.dispos_ok) {
                //     fetch_dispos();
                // } else {
                //     if (user.dispos.length == 0) {
                //         create_dispos_user_data();
                //     }
                //     go_edt(false);
                // }
                if (dispos.length == 0) {
		    fetch_dispos();
		}
		
            } else {
                user.dispos = [];
                //ckbox["dis-mod"].disp = false;
                stg.attr("visibility", "hidden");
                dim_dispo.plot = 0;
                if (rootgp_width != 0) {
                    labgp.width *= 1 + (dim_dispo.width + dim_dispo.right) / (rootgp_width * labgp.width);
                }
                go_edt(false);
            }
        } else if (dk == "edt-mod") {
            if (ckbox[dk].cked) {
		fetch_unavailable_rooms();
		fetch_all_tutors();
		if (total_regen && (logged_usr.rights >> 2) % 2 == 0) {

		    ckbox[dk].cked = false ;
		
		    var splash_disclaimer = {
			id: "disc-edt-mod",
			but: {list: [{txt: "Ok", click: function(d){} }]},
			com: {list: [{txt: "Avis", ftsi: 23}, {txt: ""},
				     {txt: "L'emploi du temps va être regénéré totalement (cf. en bas à droite)."},
				     {txt: "Contentez-vous de mettre à jour vos disponibilités : elles seront prises en compte lors de la regénération."}]}
		    }
		    splash(splash_disclaimer);
		    
		    return ;
		}
		
                edt_but.attr("visibility", "visible");

		if (dispos.length == 0) {
		    fetch_dispos();
		}
                // if (!fetch.dispos_ok) {
                //     fetch_dispos();
                // } else {
                //     go_edt(true);
                // }
            } else {
                edt_but.attr("visibility", "hidden");
                go_edt(true);
            }
        } else {
            go_edt(true);
        }
        // Fetch data, ask for login, etc.
        // ...

        stg
            .select("[but=st-ap]")
            .attr("cursor", st_but_ptr());



        go_menus();
    }
}



/*-----------------------
   ------ VALIDATE ------
   ----------------------*/

function compute_changes(changes, profs, gps) {
    var i, id, change, prof_changed, gp_changed, gp_named;

    var cur_course, cb ;

    var splash_case, msg ;
    var msgRetry = "Corrigez, puis réessayez." ;
    var butOK = {list: [{txt: "Ok", click: function(d){}}]} ;

    
    for (i = 0; i < Object.keys(cours_bouge).length ; i++) {
	id = Object.keys(cours_bouge)[i] ;
	cur_course = get_course(id) ;
	cb = cours_bouge[id] ;

	if (had_moved(cb , cur_course) || cur_course.prof != cb.prof) {

	    /* Sanity checks */
	    
	    // No course has been moved to garbage slots
            if (is_garbage(cur_course.day, cur_course.slot)) {
		splash_case = {
		    id: "garb-sched",
		    but: butOK,
		    com: {list: [{txt: "Vous avez déplacé, puis laissé des cours non placés."},
				 {txt: msgRetry}]}
		}
		
		splash(splash_case);
		return false ;
            } 
	    // Course in unavailable slots for some training programme
	    else if (is_free(cur_course.day,
			     cur_course.slot,
			     cur_course.promo)) {
		
		msg = "Pas de cours pour les ";
		if (set_promos[gp_changed.promo] == 3) {
		    msg += "LP" ;
		} else {
		    msg += set_promos[cur_course.promo] + "A" ;
		    
		}
		msg += " le " + data_grid_scale_day[cur_course.day]
		    + " sur le créneau "
		    + data_grid_scale_hour[cur_course.slot]
		    + "."
		
		splash_case = {
		    id: "unav-tp",
		    but: butOK,
		    com: {list: [{txt: msg},
				 {txt: msgRetry}]}
		}
		
		splash(splash_case);
		return false ;
            } else if (cur_course.room == une_salle){
		splash_case = {
		    id: "def-room",
		    but: butOK,
		    com: {list: [{txt: "Vous avez laissé la salle 'par défaut'."},
				 {txt: "Pour l'instant, le changement n'est pas accepté."},
				 {txt: "Merci de chercher et de renseigner une salle disponible."}]}
		}
		
		splash(splash_case);
		return false ;
	    }
	    
	    
	    /* Change is accepted now */
	    
	    // add instructor if never seen
            if (profs.indexOf(cur_course.prof) == -1
		&& cur_course.prof != logged_usr.nom) {
                profs.push(cur_course.prof);
            }
            if (profs.indexOf(cb.prof) == -1
		&& cur_course.prof != logged_usr.nom) {
                profs.push(cb.prof);
            }

	    // add group if never seen
	    gp_changed = groups[cur_course.promo][cur_course.group] ;
	    gp_named = set_promos[gp_changed.promo] + gp_changed.nom ;
	    // if (set_promos[gp_changed.promo] == 3) {
	    // 	gp_named = "LP" ;
	    // } else {
	    // 	gp_named = set_promos[gp_changed.promo] + "A";
	    // 	if(gp_changed.nom != "P") {
	    // 	    gp_named += gp_changed.nom ;
	    // 	}
	    // }
            if (gps.indexOf(gp_named) == -1) {
                gps.push(gp_named);
            }
	    

	    // build the communication with django
	    
            change = {id: id,
		      day: {o: cb.day,
			    n: null },
		      slot: {o: cb.slot,
			     n: null },
		      room: {o: cb.room,
			     n: null },
		      week: {o: weeks.init_data[weeks.sel[0]].semaine,
			     n: null },
		      year: {o: weeks.init_data[weeks.sel[0]].an,
			     n: null},
		      tutor:{o: cb.prof,
			     n: null}
		     };
	    
	    
            console.log("change", change);
	    if (cb.day != cur_course.day ||
                cb.slot != cur_course.slot) {
                change.day.n = cur_course.day;
                change.slot.n = cur_course.slot;
	    }
	    if (cb.room != cur_course.room) {
                change.room.n = cur_course.room;
	    }
	    if (cb.prof != cur_course.prof) {
                change.tutor.n = cur_course.prof;
	    }
	    
	    changes.push(change);
		
            
	    
	}


    }
    
    console.log(JSON.stringify({
        v: version,
        tab: changes
    }));

    return true ;

}


function confirm_change() {
    var changes, profs_conc, gps, i, prof_txt, gp_txt;
    changes = [];
    profs_conc = [];
    gps = [];
    var changesOK = compute_changes(changes, profs_conc, gps);

    if (!changesOK) {
	return ;
    }

    if (changes.length == 0) {
        ack.edt = "base EdT : RAS";
        go_ack_msg(true);
    } else {

        if (profs_conc.length > 0) {
            prof_txt = "Avez-vous contacté " ;
	    prof_txt += array_to_msg(profs_conc) ;
	    prof_txt += " ?" ;
	} else {
            prof_txt = "Tudo bem ?" ;
	}

        gp_txt = "(Par ailleurs, ce serait bien de prévenir ";
	if (gps.length == 1) {
	    gp_txt += "le groupe ";
	} else {
	    gp_txt += "les groupes ";
	}
	gp_txt += array_to_msg(gps) ;
        gp_txt += ").";


	var splash_confirm = {
	    id: "conf-chg",
	    but: {list: [{txt: "Oui", click: function(d){send_edt_change(changes);}},
			 {txt: "Non", click: function(d){} }]},
	    com: {list: [{txt: prof_txt},
			 {txt:gp_txt}]}
	}

	splash(splash_confirm);

    }
}


function array_to_msg(a) {
    console.log(a);
    var i ;
    var ret = "" ;
    for (i = 0; i < a.length - 2 ; i++) {
	ret += a[i] + ", " ;
    }
    if (a.length > 1) {
	ret += a[a.length - 2] + " et "
	    + a[a.length - 1] ;
    } else {
	ret += a[0] ;
    }
    return ret ;
}



function send_edt_change(changes) {
    var sent_data = {} ;
    sent_data['v'] = JSON.stringify(version) ; 
    sent_data['tab'] = JSON.stringify(changes) ;

    show_loader(true);
    $.ajax({
        url: url_edt_changes
	    + "?s=" + weeks.init_data[weeks.sel[0]].semaine
	    + "&a=" + weeks.init_data[weeks.sel[0]].an
	    + "&c=" + num_copie,
        type: 'POST',
//        contentType: 'application/json; charset=utf-8',
        data: // JSON.stringify({
        //     v: version,
        //     tab: changes
        // }),
	sent_data,
        dataType: 'json',
        success: function(msg) {
            edt_change_ack(msg);
            show_loader(false);
        },
        error: function(msg) {
            edt_change_ack(msg);
            show_loader(false);
        }
    });
}




function send_dis_change() {
    var changes = [];
    var nbDispos = 0;

    if (user.dispos_bu.length == 0) {
        ack.edt = "base dispo : RAS";
        go_ack_msg(true);
        return;
    }

    for (var i = 0; i < Object.keys(user.dispos).length; i++) {
        if (user.dispos[i].val > 0) {
            nbDispos++;
        }
        if (user.dispos[i].val != user.dispos_bu[i].val) {
            changes.push(user.dispos[i]);
        }
        user.dispos_bu[i].day = user.dispos[i].day;
        user.dispos_bu[i].hour = user.dispos[i].hour;
        user.dispos_bu[i].val = user.dispos[i].val;
        user.dispos_bu[i].off = user.dispos[i].off;
    }



    // console.log(nbDispos);
    // console.log(changes);
    // console.log(JSON.stringify({create: create, tab: changes}));
    // console.log(JSON.stringify(changes));


    if (changes.length == 0) {
        ack.edt = "base dispo : RAS";
        go_ack_msg(true);
    } else {

	var sent_data = {} ;
	sent_data['changes'] = JSON.stringify(changes) ; 

        show_loader(true);
        $.ajax({
            url: url_dispos_changes
		+ "?s=" + weeks.init_data[weeks.sel[0]].semaine
		+ "&a=" + weeks.init_data[weeks.sel[0]].an
		+ "&u=" + user.nom,
            type: 'POST',
//            contentType: 'application/json; charset=utf-8',
            data: sent_data , //JSON.stringify(changes),
            dataType: 'json',
            success: function(msg) {
                show_loader(false);
                return dis_change_ack(msg, nbDispos);
            },
            error: function(msg) {
                show_loader(false);
                return dis_change_ack(msg, nbDispos);
            }
        });
    }


}




function edt_change_ack(msg) {
    if (msg.responseText == "OK") {
        version += 1;
        ack.edt = "Modifications EDT : OK !";
        cours_bouge = [];
    } else {
        ack.edt = msg.getResponseHeader('reason');
        if (ack.edt != null && ack.edt.startsWith("Version")) {
            ack.edt += "Quelqu'un a modifié entre-temps."
        }
    }
    console.log(ack.edt);
    go_ack_msg(true);
}


function dis_change_ack(msg, nbDispos) {
    console.log(msg);
    if (msg.responseText == "OK") {
        ack.edt = "Modifications dispos : OK !"
    } else {
        ack.edt = msg.getResponseHeader('reason');
    }
    go_ack_msg(true);

    filled_dispos = nbDispos;
    go_alarm_pref();

}



/*--------------------
   ------ SLASH ------
  --------------------*/



function clean_splash(class_id) {
    dg.select("." + class_id).remove() ;
}



function splash(splash_ds){


    if (splash_ds.bg === undefined) {
	splash_ds.bg = {x:0,
			y:0,
			width: grid_width(),
			height: grid_height()};// + valid.margin_edt + 1.1 * valid.h} ;
	
    }

    var wp = splash_ds.bg ;

    var class_id = "spl_" + splash_ds.id ;

    dg
	.select("." + class_id)
	.remove();
    
    dg
        .append("g")
        .attr("class", class_id)
        .append("rect")
        .attr("x", wp.x)
        .attr("y", wp.y)
        .attr("width", wp.width)
        .attr("height", wp.height)
        .attr("fill", "white");

    var spg = dg.select("." + class_id) ;


    
    var  i, f ;

    var but_par = splash_ds.but ;

    if (but_par.slack_y === undefined) {
	but_par.slack_y = valid.h ;
    }
    if (but_par.slack_x === undefined) {
	but_par.slack_x = 90 ;
    }
    if (but_par.width === undefined) {
	but_par.width = valid.w;
    }
    if (but_par.height === undefined) {
	but_par.height = valid.h;
    }

    
    var but_dat = but_par.list ;
    var init_but_x = wp.x + .5*wp.width
	- .5 * (but_dat.length * but_par.width
		+ (but_dat.length - 1) * but_par.slack_x) ;
    var init_but_y = wp.y + wp.height - but_par.height - but_par.slack_y ;
    for (i = 0 ; i < but_dat.length; i++){
	f = but_dat[i].click ;
	but_dat[i].x = init_but_x + i * (but_par.width + but_par.slack_x) ;
	but_dat[i].y = init_but_y ;
	but_dat[i].w = but_par.width ;
	but_dat[i].h = but_par.height ;
    }



    var buts = spg
	.selectAll(".but")
	.data(but_dat)
	.enter()
	.append("g")
        .attr("cursor", "pointer")
        .attr("class", "but")
	.on("click", function(d) { d.click(d); clean_splash(class_id); } );
    

    buts
        .append("rect")
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("x", classic_x)
        .attr("y", classic_y)
        .attr("width", classic_w)
        .attr("height", classic_h)
        .attr("fill", "steelblue")
        .attr("stroke", "black")
        .attr("stroke-width", 2);

    buts
	.append("text")
	.attr("style", function(d){
	    return "text-anchor: middle; font-size: 18";
	})
        .attr("x", classic_txt_x)
        .attr("y", classic_txt_y)
        .text(classic_txt);



    var com_par = splash_ds.com ;

    if (com_par.x === undefined) {
	com_par.x = .5 * grid_width();
    }
    if (com_par.slack_y === undefined) {
	com_par.slack_y = 50 ;
    }
    if (com_par.anch === undefined) {
	com_par.anch = "middle" ;
    }


    
    var com_dat = com_par.list ;
    var init_com_y = wp.y + .5*(wp.height - but_par.height - 2* but_par.slack_y)
	- .5 * (com_dat.length  * com_par.slack_y) ;
    for (i = 0 ; i < com_dat.length; i++){
	com_dat[i].x = com_par.x ;
	com_dat[i].y = init_com_y + i * com_par.slack_y ;
	if (com_dat[i].ftsi === undefined) {
	    com_dat[i].ftsi = 18 ;
	}
    }

    console.log(com_dat);


    var comms = spg
	.selectAll(".comm")
	.data(com_dat)
	.enter();


    comms
        .append("text")
        .attr("class", "comm")
	.attr("style", function(d){
	    return "text-anchor: "+d.anch
		+"; font-size:" + d.ftsi;
	})
        .attr("x", classic_x)
        .attr("y", classic_y)
        .text(classic_txt);
    
}








/*--------------------
   ------ STYPE ------
  --------------------*/

function apply_stype() {
    if (ckbox["dis-mod"].cked) {
        for (var d = 0; d < user.dispos.length; d++) {
            user.dispos[d].day = user.dispos_type[d].day;
            user.dispos[d].hour = user.dispos_type[d].hour;
            user.dispos[d].val = user.dispos_type[d].val;
            user.dispos[d].off = user.dispos_type[d].off;
            dispos[user.nom][user.dispos[d].day][user.dispos[d].hour] = user.dispos[d].val;
        }
        go_pref(true);
        send_dis_change();
    }
}



/*--------------------
   ------ ALL -------
   --------------------*/

// add the initial comfiguration of a course to cours_bouge if
// it has not been moved until now
function add_bouge(d) {
    console.log("new");
    if (Object.keys(cours_bouge).indexOf(d.id_cours.toString()) == -1) {
        cours_bouge[d.id_cours] = {
            id: d.id_cours,
            day: d.day,
            slot: d.slot,
            room: d.room,
	    prof: d.prof
        };
        console.log(cours_bouge[d.id_cours]);
    }
}

function had_moved(cb, c){
    return cb.day != c.day
	|| cb.slot != c.slot
	|| cb.room != c.room ;
}


function get_course(id){
    var found = false ;
    var i = 0 ;
    
    while (i < Object.keys(cours).length && !found) {
	if (cours[i].id_cours == id){
	    found = true ;
	} else {
	    i ++ ;
	}
    }

    if (found) {
	return cours[i] ;
    } else {
	return null ;
    }
    
}


function compute_cm_room_tutor_direction() {
    var c = room_tutor_change.course[0] ;
    var cm_start_x, cm_start_y;
    cm_start_x = cours_x(c) + .5 * cours_width(c) ;
    cm_start_y = cours_y(c)  + .5 * cours_height(c) ;
    if (grid_width() - cm_start_x < cm_start_x) {
    	room_tutor_change.posh = 'w';
    } else {
    	room_tutor_change.posh = 'e';
    }
    if (grid_height() - cm_start_y < cm_start_y) {
    	room_tutor_change.posv = 'n';
    } else {
    	room_tutor_change.posv = 's';
    }
}


