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
----------  UPDATE -----------
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

// update all preferences
function go_pref(quick) {
        var t, dat, datdi, datsmi;

        if (quick) {
            t = d3.transition()
                .duration(0);
        } else {
            t = d3.transition();
        }


	// preferences: background color, and smiley
	
        dat = mg.selectAll(".dispo")
            .data(user.dispos)
            .attr("cursor", ckbox["dis-mod"].cked ? "pointer" : "default");

        datdi = dat
            .enter()
            .append("g")
            .attr("class", "dispo");

        var datdisi = datdi
            .append("g")
            .attr("class", "dispo-si")
            .on("click", apply_change_simple_pref);

        datdisi
            .append("rect")
            .attr("class", "dispo-bg")
            .attr("stroke", "black")
            .attr("stroke-width", 1)
            .attr("width", dispo_w)
            .attr("height", 0)
            .attr("x", dispo_x)
            .attr("y", dispo_y)
            .attr("fill", function(d) {
                return smi_fill(d.val / par_dispos.nmax);
            })
            .merge(dat.select(".dispo-bg"))
            .transition(t)
            .attr("width", dispo_w)
            .attr("height", dispo_h)
            .attr("x", dispo_x)
            .attr("y", dispo_y)
            .attr("fill", function(d) {
                return smi_fill(d.val / par_dispos.nmax);
            });

        var datex = dat
            .exit();

        datex
            .select(".dispo-bg")
            .transition(t)
            .attr("height", 0);

        datex
            .remove();

        go_smiley(dat, datdisi, t);



	// detailed view

        datadvdi = datdi
            .append("g")
            .attr("class", "dispo-a");

        datadvdi
            .merge(dat.select(".dispo-a"))
            .on("click", function(d) {
                if (ckbox["dis-mod"].cked) {
		    context_menu.dispo_hold = true ;
                    data_dispo_adv_cur = data_dispo_adv_init.map(
                        function(c) {
                            return {
                                day: d.day,
                                hour: d.hour,
                                off: c.off
                            };
                        });
		    go_cm_advanced_pref(true);
                }
            });


        datadvdi
            .append("rect")
            .attr("stroke", "none")
            .attr("stroke-width", 1)
            .attr("fill", "black")
            .attr("opacity", 0)
            .merge(dat.select(".dispo-a").select("rect"))
            .attr("width", dispo_more_h)
            .attr("height", dispo_more_h)
            .attr("x", dispo_more_x)
            .attr("y", dispo_more_y);

        datadvdi
            .append("line")
            .attr("stroke-linecap", "butt")
            .attr("stroke", "antiquewhite")
            .attr("stroke-width", 2)
            .attr("li", "h")
            .attr("x1", cross_l_x)
            .attr("y1", cross_m_y)
            .attr("x2", cross_r_x)
            .attr("y2", cross_m_y)
            .merge(dat.select(".dispo-a").select("[li=h]"))
            .transition(t)
            .attr("x1", cross_l_x)
            .attr("y1", cross_m_y)
            .attr("x2", cross_r_x)
            .attr("y2", cross_m_y);

        datadvdi
            .append("line")
            .attr("stroke-linecap", "butt")
            .attr("stroke", "antiquewhite")
            .attr("stroke-width", 2)
            .attr("li", "v")
            .attr("x1", cross_m_x)
            .attr("y1", cross_t_y)
            .attr("x2", cross_m_x)
            .attr("y2", cross_d_y)
            .merge(dat.select(".dispo-a").select("[li=v]"))
            .transition(t)
            .attr("x1", cross_m_x)
            .attr("y1", cross_t_y)
            .attr("x2", cross_m_x)
            .attr("y2", cross_d_y);

        datadvdi
            .append("circle")
            .attr("fill", "none")
            .attr("stroke", "antiquewhite")
            .attr("stroke-width", 2)
            .attr("cx", cross_m_x)
            .attr("cy", cross_m_y)
            .attr("r", par_dispos.rad_cross * smiley.tete)
            .merge(dat.select(".dispo-a").select("circle"))
            .transition(t)
            .attr("cx", cross_m_x)
            .attr("cy", cross_m_y)
            .attr("r", par_dispos.rad_cross * smiley.tete);


	go_cm_advanced_pref(quick) ;


}



// top: container issued from selecting all the .dispo
// mid: container with new smileys
// t:   transition
function go_smiley(top, mid, t) {
    
    var datsmi = mid
        .append("g")
        .attr("class", "smiley")
        .attr("stroke-width", 1)
        .attr("transform", smile_trans)
        .attr("stroke", "black");

    datsmi
        .merge(top.select(".smiley"))
        .transition(t)
        .attr("transform", smile_trans)
        .attr("stroke", "black");

    datsmi
        .append("circle")
        .attr("st", "t")
        .merge(top.select("[st=t]"))
        .attr("cx", 0)
        .attr("cy", 0)
        .attr("r", smiley.tete)
        .attr("stroke", function(d) {
            return tete_str(rc(d));
        })
        .attr("fill", function(d) {
            return smi_fill(rc(d));
        });

    datsmi
        .append("circle")
        .attr("st", "od")
        .attr("fill", "none")
        .merge(top.select("[st=od]"))
        .attr("cx", smiley.tete * smiley.oeil_x)
        .attr("cy", smiley.tete * smiley.oeil_y)
        .attr("r", function(d) {
            return oeil_r(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });

    datsmi
        .append("circle")
        .attr("st", "og")
        .attr("fill", "none")
        .merge(top.select("[st=og]"))
        .attr("cx", -smiley.tete * smiley.oeil_x)
        .attr("cy", smiley.tete * smiley.oeil_y)
        .attr("r", function(d) {
            return oeil_r(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });


    datsmi
        .append("line")
        .attr("st", "sd")
        .merge(top.select("[st=sd]"))
        .attr("x1", function(d) {
            return sourcil_int_x(rc(d));
        })
        .attr("y1", function(d) {
            return sourcil_int_y(rc(d));
        })
        .attr("x2", function(d) {
            return sourcil_ext_x(rc(d));
        })
        .attr("y2", function(d) {
            return sourcil_ext_y(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });

    datsmi
        .append("line")
        .attr("st", "sg")
        .merge(top.select("[st=sg]"))
        .attr("x1", function(d) {
            return sourcil_intg_x(rc(d));
        })
        .attr("y1", function(d) {
            return sourcil_int_y(rc(d));
        })
        .attr("x2", function(d) {
            return sourcil_extg_x(rc(d));
        })
        .attr("y2", function(d) {
            return sourcil_ext_y(rc(d));
        })
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });

    datsmi
        .append("rect")
        .attr("st", "si")
        .merge(top.select("[st=si]"))
        .attr("x", -.5 * smiley.rect_w * smiley.tete)
        .attr("y", -.5 * smiley.rect_h * smiley.tete)
        .attr("width", function(d) {
            return interdit_w(rc(d));
        })
        .attr("height", smiley.rect_h * smiley.tete)
        .attr("fill", "white")
        .attr("stroke", "none");

    datsmi
        .append("path")
        .attr("st", "b")
        .merge(top.select("[st=b]"))
        .attr("d", function(d) {
            return smile(rc(d));
        })
        .attr("fill", "none")
        .attr("stroke-width", function(d) {
            return trait_vis_strw(rc(d));
        });


}


// advanced preference menu
function go_cm_advanced_pref(quick) {
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }
    
    var dis_men_dat = cmpg
        .selectAll(".dispo-menu")
        .data(data_dispo_adv_cur);
    
    var dis_men = dis_men_dat
        .enter()
        .append("g")
        .attr("class", "dispo-menu")
        .attr("cursor", "pointer")
        .on("click", function(d) {
            dispos[user.nom][d.day][d.hour] = d.off;
            user.dispos[day_hour_2_1D(d)].val = d.off;
	    data_dispo_adv_cur = [] ;
	    go_pref(true);
        });
    
    dis_men
        .append("rect")
        .attr("class", "dis-men-bg")
        .merge(dis_men_dat.select(".dis-men-bg"))
        .transition(t)
        .attr("x", dispo_all_x)
        .attr("y", dispo_all_y)
        .attr("width", dispo_all_w)
        .attr("height", dispo_all_h)
        .attr("fill", function(d) {
            return smi_fill(d.off / par_dispos.nmax);
            })
        .attr("stroke", "darkslategrey")
        .attr("stroke-width", 2);
    
    go_smiley(dis_men_dat, dis_men, t);
    

    dis_men_dat.exit().remove();
}


// check and inform whenever there is not enough available slots
function go_alarm_pref() {

    dig
        .select(".disp-info").select(".disp-required")
        .text(txt_reqDispos)
        .attr("x", menus.x + menus.mx - 5)
        .attr("y", did.tly + valid.h * 1.5);
    dig
        .select(".disp-info").select(".disp-filled")
        .text(txt_filDispos)
        .attr("x", menus.x + menus.mx - 5)
        .attr("y", did.tly + valid.h * 1.5 + valid.margin_h);

    if (required_dispos > filled_dispos) {
        dig
            .select(".disp-info").select(".disp-filled")
            .attr("font-weight", "bold").attr("fill", "red");
        dig
            .select(".disp-info").select(".disp-required")
            .attr("font-weight", "bold");
    } else {
        dig
            .select(".disp-info").select(".disp-filled")
            .attr("font-weight", "normal").attr("fill", "black");
        dig
            .select(".disp-info").select(".disp-required")
            .attr("font-weight", "normal");
    }
}





/*---------------------
  ------- WEEKS -------
  ---------------------*/


function go_week_menu(quick) {

    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition()
            .duration(200);
    }

    var sa_wk =
        weeks.cont
        .selectAll(".rec_wk")
        .data(weeks.cur_data, function(d) {
            return d.an + "" + d.semaine;
        });

    sa_wk.exit().transition(t).remove();

    var g_wk = sa_wk
        .enter()
        .append("g")
        .attr("class", "rec_wk");

    g_wk
        .merge(sa_wk)
        .on("click", apply_wk_change);


    g_wk
        .append("rect")
        .attr("y", 0)
        .attr("height", weeks.height)
        .attr("width", weeks.width)
        .attr("x", rect_wk_init_x)
        .merge(sa_wk.select("rect"))
        .transition(t)
        .attr("x", rect_wk_x);

    g_wk
        .append("text")
        .attr("fill", "white")
        .text(rect_wk_txt)
        .attr("y", .5 * weeks.height)
        .attr("x", rect_wk_init_x)
        .merge(sa_wk.select("text"))
        .transition(t)
        .attr("x", function(d, i) {
            return rect_wk_x(d, i) + .5 * weeks.width;
        });

    var wk_sel =
        wg.fg
        .selectAll(".sel_wk")
        .data(weeks.sel)
        .select("ellipse")
        .transition(t)
        .attr("cx", week_sel_x);
}



/*----------------------
  -------- GRID --------
  ----------------------*/


function go_grid(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    var grid = bg.selectAll(".gridm")
        .data(data_mini_slot_grid
            .filter(function(d) {
                return d.gp.display;
            }),
            function(d) {
                return d.gp.promo + "," + d.gp.nom + "," + d.day + "," + d.slot;
            });

    grid
        .enter()
        .append("rect")
        .attr("class", "gridm")
        .attr("x", gm_x)
        .attr("y", gm_y)
        .attr("width", 0)
        .merge(grid)
        .transition(t)
        .attr("x", gm_x)
        .attr("y", gm_y)
        .attr("width", labgp.width)
        .attr("height", labgp.height);

    grid.exit()
        .transition(t)
        .attr("width", 0)
        .remove();

    grid = fg.selectAll(".grids")
        .data(data_slot_grid);

    var gridg = grid
        .enter()
        .append("g")
        .attr("class", "grids")
        .style("cursor", gs_cursor)
        .on("click", clear_pop);


    gridg
        .append("rect")
        .attr("x", gs_x)
        .attr("y", gs_y)
        .attr("stroke", gs_sc)
        .attr("stroke-width", gs_sw)
        .merge(grid.select("rect"))
        .transition(t)
        .attr("fill-opacity", gs_opacity)
        .attr("x", gs_x)
        .attr("y", gs_y)
        .attr("width", gs_width)
        .attr("height", gs_height)
        .attr("fill", gs_fill);

    grid
	.exit()
	.remove();

    gridg
        .append("text")
        .attr("stroke", "none")
        .attr("font-size", 14)
        .attr("x", function(s) {
            return gs_x(s) + .5 * gs_width(s);
        })
        .attr("y", function(s) {
            return gs_y(s) + .5 * gs_height(s);
        })
        .merge(grid.select("text"))
        .transition(t)
        .attr("x", function(s) {
            return gs_x(s) + .5 * gs_width(s);
        })
        .attr("y", function(s) {
            return gs_y(s) + .5 * gs_height(s);
        })
        .text(gs_txt);


    grid = bg.selectAll(".gridscg")
        .data(data_grid_scale_gp
            .filter(function(d) {
                return d.gp.display;
            }),
            function(d) {
                return d.gp.promo + "," + d.day + "," +
                    d.gp.nom;
            });

    grid
        .enter()
        .append("text")
        .attr("class", "gridscg")
        .attr("x", gscg_x)
        .attr("y", gscg_y)
        .text(gscg_txt)
        .merge(grid)
        .transition(t)
        .attr("x", gscg_x)
        .attr("y", gscg_y);

    grid.exit().remove();


    grid = bg.selectAll(".gridscp")
        .data(data_grid_scale_row
            .filter(function(d) {
                return row_gp[d.row].display;
            }),
            function(d) {
                return d.row + "," + d.slot;
            });

    grid
        .enter()
        .append("text")
        .attr("class", "gridscp")
        .attr("x", gscp_x)
        .attr("y", gscp_y)
        .text(gscp_txt)
        .merge(grid)
        .transition(t)
        .attr("x", gscp_x)
        .attr("y", gscp_y);

    grid.exit().remove();



    bg
        .selectAll(".gridsckd")
        .data(data_grid_scale_day)
        .transition(t)
        .text(gsckd_txt)
        .attr("fill", "darkslateblue")
        .attr("font-size", 22)
        .attr("x", gsckd_x)
        .attr("y", gsckd_y);
    bg
        .selectAll(".gridsckh")
        .data(data_grid_scale_hour)
        .transition(t)
        .attr("x", gsckh_x)
        .attr("y", gsckh_y);



    fg.select(".h-sca").select("rect")
        .transition(t)
        .attr("x", but_sca_h_x())
        .attr("y", but_sca_h_y());
    fg.select(".h-sca").select("path")
        .transition(t)
        .attr("d", but_sca_tri_h(0));

    fg.select(".v-sca").select("rect")
        .transition(t)
        .attr("x", but_sca_v_x())
        .attr("y", but_sca_v_y());
    fg.select(".v-sca").select("path")
        .transition(t)
        .attr("d", but_sca_tri_v(0));



}


/*----------------------
  ------- BKNEWS -------
  ----------------------*/


function go_bknews(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    fig
	.select(".top-bar")
        .transition(t)
        .attr("x1", 0)
        .attr("y1", bknews_top_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_top_y());

    fig
	.select(".bot-bar")
        .transition(t)
        .attr("x1", 0)
        .attr("y1", bknews_bot_y())
        .attr("x2", grid_width())
        .attr("y2", bknews_bot_y());
    
    var flash = fig.select(".txt-info");

    var fl_all = flash
	.selectAll(".bn-all")
	.data(bknews.cont,
	      function(d) { return d.id ; });

    var ffl = fl_all
	.enter()
	.append("g")
	.attr("class", "bn-all")
	.append("a")
	.attr("xlink:href", bknews_link);

    ffl
	.append("rect")
	.attr("class", "bn-rec")
	.attr("fill", bknews_row_fill)
	.attr("stroke", bknews_row_fill)
	.attr("stroke-width", 1)
	.attr("y", bknews_row_y)
	.merge(fl_all.select(".bn-rec"))
        .transition(t)
	.attr("x", bknews_row_x)
	.attr("y", bknews_row_y)
	.attr("width", bknews_row_width)
	.attr("height", bknews_row_height);
    
    

    ffl
	.append("text")
	.attr("class", "bn-txt")
	.attr("fill", bknews_row_txt_strk)
	.text(bknews_row_txt)
	.attr("y", bknews_row_txt_y)
	.merge(fl_all.select(".bn-txt"))
        .transition(t)
	.attr("x", bknews_row_txt_x)
	.attr("y", bknews_row_txt_y);

    fl_all.exit().remove();
    
}


/*----------------------
  ------- QUOTES -------
  ----------------------*/


function go_quote() {
    vg.select(".quote").select("text")
        .transition(d3.transition())
        .attr("x", quote_x())
        .attr("y", quote_y());
}




/*----------------------
  ------- GROUPS -------
  ----------------------*/

function go_gp_buttons() {

    for (var p = 0; p < set_promos.length; p++) {
        var cont =
            gpg.selectAll(".gp-but-" + set_promos[p] + "P")
            .data(Object.keys(groups[p]).map(function(k) {
                return groups[p][k];
            }));

        var contg = cont
            .enter()
            .append("g")
            .attr("class", "gp-but-" + set_promos[p] + "P")
            .attr("transform", function(gp) {
                return "translate(" + root_gp[gp.promo].butx + "," + root_gp[gp.promo].buty + ")";
            })
            .attr("gpe", function(gp) {
                return gp.nom;
            })
            .attr("promo", function(gp) {
                return gp.promo;
            })
            .on("click", function(gp) {
		apply_gp_display(gp, false, true);
	    });


        contg.append("rect")
            .attr("x", butgp_x)
            .attr("y", butgp_y)
            .attr("width", butgp_width)
            .attr("height", butgp_height)
            .merge(cont.select("rect"))
            .attr("fill", fill_gp_button)
            .attr("stroke-width", 1)
            .attr("stroke", "black");

        contg.append("text")
            .attr("x", butgp_txt_x)
            .attr("y", butgp_txt_y)
            .text(butgp_txt);

    }

}


/*--------------------
  ------ MENUS -------
  --------------------*/
function go_menus() {

    var init = meg
        .selectAll(".ckline")
        .data(Object.keys(ckbox));


    var ent = init
        .enter()
        .append("g")
        .attr("class", "ckline")
        .on("click", apply_ckbox);



    var cs = ent
        .append("g")
        .attr("class", "ckstat");

    var cd = ent.
    append("g")
        .attr("class", "ckdyn");


    cs
        .append("rect")
        .attr("x", menu_cks_x)
        .attr("y", menu_cks_y)
        .attr("rx", 2)
        .attr("ry", 2)
        .attr("width", menus.sfac * menus.h)
        .attr("height", menus.sfac * menus.h)
        .merge(init.select(".ckstat").select("rect"))
        .attr("stroke", menu_cks_fill)
        .attr("stroke-width", menu_cks_stw);

    cs
        .append("text")
        .attr("x", menu_ck_txt_x)
        .attr("y", menu_ck_txt_y)
        .merge(init.select(".ckstat").select("text"))
        .attr("fill", menu_cks_fill)
        .text(menu_cks_txt);


    cd
        .append("rect")
        .attr("stroke", "none")
        .attr("x", menu_ckd_x)
        .attr("y", menu_ckd_y)
        .attr("width", menus.ifac * menus.sfac * menus.h)
        .attr("height", menus.ifac * menus.sfac * menus.h)
        .merge(init.select(".ckdyn").select("rect"))
        .attr("fill", menu_ckd_fill);


    meg
        .selectAll(".ckline")
        .data(Object.keys(ckbox))
        .attr("cursor", menu_curs);

}


/*--------------------
  ------ MODULES -------
  --------------------*/

// update module opacity
function go_modules() {
    var sel_i = mog.property('selectedIndex');
    modules.sel = mog
        .selectAll("option")
        .filter(function(d, i) {
            return i == sel_i;
        })
        .datum();
    go_opac_cours();
}

// Tries to determine the relevant modules for the viewer.
function relevant_modules() {

    // The relevant tutors
    var tutors = new Set();
    if (prof_displayed.length < profs.length) { // some tutors are selected
        prof_displayed.forEach(function (p) {
            tutors.add(p);
        });
    } else if (user.nom) {
        tutors.add(user.nom);
    }

    // The relevant modules
    var modules = new Set();
    cours.forEach(function(c) {
        if (tutors.has(c.prof)) {
            modules.add(c.mod);
        }
    });

    return modules;
}

/*--------------------
  ------ ROOMS -------
  --------------------*/

// update room opacity
function go_rooms() {
    var sel_i = sag.property('selectedIndex');
    salles.sel = sag
        .selectAll("option")
        .filter(function(d, i) {
            return i == sel_i;
        })
        .datum();
    go_opac_cours();
}


/*--------------------
  ------ TUTORS ------
  --------------------*/

function go_tutors() {

    prg.selectAll(".tutor-button")
        .data(profs, function(p) {
            return p;
        })
        .attr("opacity", function(p) {
            return prof_displayed.indexOf(p) > -1 ? 1 : opac;
        });

    create_mod_dd();
    go_opac_cours();
}





/*--------------------
   ------ COURS -------
  --------------------*/

function go_courses(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }


    var cg = mg.selectAll(".cours")
        .data(cours.filter(function(d) {
                return groups[d.promo][d.group].display;
            }),
            function(d) {
                return d.id_cours;
            })
        .attr("cursor", ckbox["edt-mod"].cked ? "pointer" : "default");

    var incg = cg.enter()
        .append("g")
        .attr("class", "cours")
        .attr("cursor", ckbox["edt-mod"].cked ? "pointer" : "default")
        .on("contextmenu", function(d) { if (ckbox["edt-mod"].cked) {
	    d3.event.preventDefault();
	    room_tutor_change.cm_settings = entry_cm_settings ;
	    room_tutor_change.course = [d] ;
	    compute_cm_room_tutor_direction();
	    //select_room_change(d);
	    select_entry_cm(d);
	    go_cm_room_tutor_change();
	}})
        .call(dragListener);
    
    incg
        .append("rect")
        .attr("class", "crect")
        .attr("x", cours_x)
        .attr("y", cours_y)
        .attr("width", 0)
        .merge(cg.select("rect"))
        .attr("fill", cours_fill)
        .transition(t)
        .attr("x", cours_x)
        .attr("y", cours_y)
        .attr("width", cours_width)
        .attr("height", cours_height);

    if (ckbox["edt-mod"].cked
	&& logged_usr.dispo_all_see) {
        d3.selectAll("rect.crect").style("fill", function(d) {
            try {
                lDis = dispos[d.prof][d.day][d.slot];
            } catch (e) {
                lDis = par_dispos.nmax;
            }

            return smi_fill(lDis / par_dispos.nmax);
        })
    } else {
        d3.selectAll("rect.crect").style("fill", cours_fill);
    }

    // Tutor's fullname 

    // var divtip = d3.select("body").append("div")
    // .attr("class", "tooltip")
    // .style("opacity", 0);

    // 
    // d3.selectAll("g.cours")
    // .on("mouseover", function(d) {
    //     divtip.transition()
    //         .duration(500)
    //         .style("opacity", .95);
    //     divtip.html(d.prof_full_name + " : "  + d.mod)
    //         .style("left", (d3.event.pageX) + "px")
    //         .style("top", (d3.event.pageY+15) + "px");
    //     })
    // .on("mouseout", function(d) {
    //     divtip.transition()
    //         .duration(200)
    //         .style("opacity", 0);
    // })

    incg
        .append("text")
        .attr("st", "m")
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_top_y)
        .text(cours_txt_top_txt)
        .attr("fill", cours_txt_fill)
        .merge(cg.select("[st=m]"))
        .transition(t)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_top_y);

    incg
        .append("text")
        .attr("st", "p")
        .attr("fill", cours_txt_fill)
        .merge(cg.select("[st=p]"))
        .transition(t)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_mid_y)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_mid_y)
        .text(cours_txt_mid_txt);

    incg
        .append("text")
        .attr("st", "r")
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_bot_y)
        .merge(cg.select("[st=r]"))
        .text(cours_txt_bot_txt)
        .attr("fill", cours_txt_fill)
        .transition(t)
        .attr("x", cours_txt_x)
        .attr("y", cours_txt_bot_y);

    cg.exit()
        .remove();

    go_cm_room_tutor_change();
}





// update courses opacity
function go_opac_cours() {

    if (prof_displayed.length < profs.length || modules.sel != "" || salles.sel != "") {
        // view with opacity filter
        var coursp = mg.selectAll(".cours")
            .data(cours.filter(function(d) {
                    var ret = prof_displayed.indexOf(d.prof) > -1;
                    ret = ret && (modules.sel == "" || modules.sel == d.mod);
                    ret = ret && (salles.sel == "" || salles.sel == d.room);
                    return ret;
                }),
                function(d) {
                    return d.id_cours;
                });

        coursp
            .attr("opacity", 1)
            .select("rect").attr("stroke", 'black');

        coursp
            .exit()
            .attr("opacity", opac)
            .select("rect").attr("stroke", 'none');

    } else {
        // view without opacity filter
        mg
            .selectAll(".cours")
            .attr("opacity", 1)
            .select("rect").attr("stroke", 'none');

    }

}



/*-----------------------
   ------ VALIDATE ------
  -----------------------*/

// update acknowledgment message
function go_ack_msg(quick) {
    var t;
    if (quick) {
        t = d3.transition()
            .duration(0);
    } else {
        t = d3.transition();
    }

    if (ack.edt != "") {
        edt_message.attr("visibility", "visible");
        edt_message.select("text").text(ack.edt);
    } else {
        edt_message.attr("visibility", "hidden");
    }

}


// update info about re-generation
function go_regen(s) {
    if (s != null) {
	total_regen = false ;
        var txt = "";
        var elements = s.split(/,| /);
        if (elements.length % 2 != 0 && elements.length > 1) {
            txt = "";
        } else if (elements[0] == 'N') {
            txt = "Pas de (re)génération prévue";
        } else if (elements[0] == 'C') {
	    total_regen = true ;
            if (elements.length > 2 && elements[2] == 'S') {
                txt = "Regénération totale (mineure) le " + elements[1] +
                    "(" + elements[3] + ")";
            } else {
                txt = "Regénération totale le " + elements[1];
            }
        } else if (elements[0] == 'S') {
            txt = "Regénération mineure le " + elements[1];
        }

        ack.regen = txt;

        vg.select(".ack-reg").select("text")
            .text(ack.regen);

    }

    vg.select(".ack-reg").select("text")
        .transition(d3.transition())
        .attr("x", grid_width())
        .attr("y", ack_reg_y());

}


function but_bold() {
    d3
        .select(this)
        .select("rect")
        .attr("stroke-width", 4);
}

function but_back() {
    d3
        .select(this)
        .select("rect")
        .attr("stroke-width", 2);
}



/*--------------------
   ------ ALL -------
  --------------------*/

// update everything
function go_edt(t) {
    go_grid(t);
    go_courses(t);
    go_tutors();
    go_pref(t);
    go_ack_msg(t);
    go_bknews(t);
    go_alarm_pref();
    go_regen(null);
    go_quote();
}
