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

var select_orig_date;
var select_prof =  d3.select("[id=prof]");
var select_gp =  d3.select("[id=gp]");
//var select_sem =  d3.select("[id=init_se]");

var default_dd = " * ";

var filtered = {semaine:semaine_init,
		an:an_init,
		mod_prof_gp:[
		    {title:'Module    ',id:'fil-mod',get:'m',arr:[default_dd],val:default_dd},
		   {title:'Enseignant·e    ',id:'fil-prof',get:'p',arr:[default_dd],val:default_dd},
		    {title:'Groupe(s)    ',id:'fil-gp',get:'g',arr:[default_dd],val:default_dd}],
		//[,[default_dd],[default_dd]],
		chosen:[0,0,0]
	       };

var aim = {semaine: 0, an:0, prof:''};

var liste_cours=[];

var liste_aim_prof = [] ;

var first_when = true ;

var commit = [];


var hours = ["8h-9h25","9h30-10h55","11h05-12h30","14h15-15h40","15h45-17h10","17h15-18h40"];

var days = ["Lun.","Mar.","Mer.","Jeu.","Ven."];





initiate();

function initiate() {

    var i =0 ;
    var found = false ;


    // current user as first choice
    while(!found && i<profs.length){
	if(profs[i]!=usna){
	    found = true;
	} else {
	    i+=1;
	}
    }
    if(i<profs.length && profs.length>0){
	var tmp = profs[0];
	profs[0] = profs[i];
	profs[i] = tmp;
    }
    fill_aim_prof([]);


    // create drop down for week selection
    select_orig_date =  d3.select("[id=orig_date]");
    select_orig_date.on("change",function(){ choose_week(true); });
    select_orig_date
	.selectAll("option")
	.data(semaine_an_list)
	.enter()
	.append("option")
	.text(function(d){return d['semaine'];});

    
    // data selection
    aim.prof=usna;
    aim.semaine=semaine_an_list[0].semaine;
    aim.an=semaine_an_list[0].an;
    

    // called with get parameters
    if(filtered.semaine!=-1 || filtered.an!=-1){

	update_after_first();
	
	d3
	    .select(".scheduled")
	    .attr("checked","checked");

	select_orig_date
	    .selectAll("option")
	    .each(function(d,i) {
		if (d.semaine==semaine_init && d.an==an_init){
		    d3.select(this).attr("selected","");
		}
	    });
    }

    create_dd();
    go_dd();

}


// fetch the data corresponding to the current selection
function go_filter(){
    var sel, di, sa, i ;
    var url_fd_full = url_fetch_decale+"?a="+filtered.an+"&s="+filtered.semaine;
    var prof_changed = false ;

    // remember the current selections (module, prof, group)
    for(i = 0 ; i<3 ; i++){
	sel = d3.select("[id="+filtered.mod_prof_gp[i].id+"]"); 
	di = sel.property('selectedIndex');
	sa = sel
	    .selectAll("option")
	    .filter(function(d,i){return i==di;})
	    .datum();
	if(sa!=default_dd){
	    url_fd_full+="&"+filtered.mod_prof_gp[i].get+"="+sa;
	}
	if(i==1 && sa!=filtered.mod_prof_gp[i].val){
	    prof_changed = true ;
	}
	filtered.mod_prof_gp[i].val=sa;
    }
    
    // remember current targeted prof
    sel = d3.select("[id=aim_prof]"); 
    di = sel.property('selectedIndex');
    sa = sel
	.selectAll("option")
	.filter(function(d,i){return i==di;})
	.datum();
    if(prof_changed){
	if (filtered.mod_prof_gp[1].val == default_dd){
	    sa = usna ;
	} else {
	    sa = filtered.mod_prof_gp[1].val ;
	}
	aim.prof = sa ;
    }

    show_loader(true);
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: url_fd_full,
        async: false,
        contentType: "application/json; charset=utf-8",
        success: function (msg) {
            // console.log(msg);
            // console.log("success");
	    // console.log(msg.modules);
	    filtered.mod_prof_gp[0].arr = msg.modules;
	    filtered.mod_prof_gp[1].arr = msg.profs;
	    filtered.mod_prof_gp[2].arr = msg.groupes;
	    liste_cours = msg.cours;
	    liste_jours = msg.jours;

	    fill_aim_prof(msg.profs_module);

	    
	    for(i = 0 ; i<3 ; i++){
		filtered.mod_prof_gp[i].arr.unshift(default_dd);
	    }
	    
	    go_dd();
	    go_dd_aim();

	    // rebuild the previously selected elements
	    for(i = 0 ; i<3 ; i++){
		var found = false ;
		var j = 0;
		while(!found && j<filtered.mod_prof_gp[i].arr.length){
		    if(filtered.mod_prof_gp[i].arr[j]==filtered.mod_prof_gp[i].val){
			found=true;
		    } else {
			j+=1 ;
		    }
		}
		if(!found){
		    document.getElementById(filtered.mod_prof_gp[i].id).selectedIndex = 0 ;
		} else {
		    document.getElementById(filtered.mod_prof_gp[i].id).selectedIndex = j;
		}
	    }

	    // rebuild the previously targeted prof
	    var found = false ;
	    var j = 0;
	    while(!found && j<liste_aim_prof.length){
		    if(liste_aim_prof[j]==sa){
			found=true;
		    } else {
			j+=1 ;
		    }
		}
	    document.getElementById("aim_prof").selectedIndex = j;


	    go_cours();
	    show_loader(false);

        },
	error: function(msg) {
	    console.log("error");
	    show_loader(false);
	},
	complete: function(msg) {
	    console.log("complete");
	    show_loader(false);
	}
    });
}

// fill drop down list of targeted prof
function fill_aim_prof(pm){
    var i;
    liste_aim_prof = [];
    liste_aim_prof.push(usna);
    liste_aim_prof.push("");
    
    for(i=0;i<pm.length;i++){
	if(pm[i]!=usna){
	    liste_aim_prof.push(pm[i]);
	}
    }
    if(pm.length>0){
	liste_aim_prof.push("");
    }
    for(i=0;i<profs.length;i++){
	if(!liste_aim_prof.includes(profs[i])){
	    liste_aim_prof.push(profs[i]);
	}
    }
}


// route action when validate
function is_orph() {
    if (first_when){
	update_after_first();
    }
    
    if(document.getElementById("canceled").checked){
	filtered.semaine = 0;
	filtered.an = 0;
	go_filter();
    } else if(document.getElementById("pending").checked){
	filtered.semaine = 1;
	filtered.an = 0;
	go_filter();
    } else {
	choose_week(false);
    }
}

// create drop down lists for targeted mod-prof-gp and actions
function create_dd() {
    d3.select(".div-filt")
	.selectAll("select")
	.data(filtered.mod_prof_gp)
	.enter()
	.append("span")
	.attr("class","crit")
	.text(function(d){return d.title;})
	.append("select")
	.attr("id",function(d){return d.id;})
	.on("change",go_filter);

    var di = d3.select(".div-aim")
	.append("div");

    di
	.append("input")
	.attr("type","radio")
	.attr("name","aim")
	.attr("id","cancel");

    di.append("label")
	.attr("for","cancel")
	.text("Annuler définitivement");

    di.append("br");

    di
	.append("input")
	.attr("type","radio")
	.attr("name","aim")
	.attr("id","pend");

    di.append("label")
	.attr("for","pend")
	.text("Mettre le(s) cours en attente");

    

    di = d3.select(".div-aim")
	.append("div");
    di
	.append("input")
	.attr("type","radio")
	.attr("name","aim")
	.attr("id","move");

    var rad = di
	.append("label");

    rad
	.append("span")
	.text("À opérer en semaine  ")
//
//    rad
	.append("select")
	.attr("id","aim_date")
	.on("change",function(d){choose_aim('d');})
//    
    rad
	.append("span")
	.attr("class","crit")
	.text("par  ")
	.append("select")
	.attr("id","aim_prof")
	.on("change",function(d){choose_aim('p');});
    
    d3.select("[id=aim_date]")
	.selectAll("option")
	.data(semaine_an_list)
	.enter()
	.append("option")
    	.attr("value", function(d){ return d['semaine']; })
	.text(function(d){return d['semaine'];});

    go_dd_aim();
    
}


// update aimed dd lists
function go_dd_aim(){

    var sel = d3.select("[id=aim_prof]")
	.selectAll("option")
	.data(liste_aim_prof,function(d,i){return i;});

    sel
	.enter()
	.append("option")
//        .merge(sel.select("option"))
    	.attr("value", function(d){ return d; })
	.text(function(d){return d;});


    d3.select("[id=aim_prof]")
    	.selectAll("option")
    	.attr("value", function(d){ return d; })
    	.text(function(d){return d;});

    
    d3.select("[id=aim_prof]")
    	.selectAll("option")
	.exit()
	.remove();
    

}

// action when the aimed date or the aimed prof is chosen
function choose_aim(dop){
    document.getElementById("cancel").checked=false;
    document.getElementById("pend").checked=true;
    document.getElementById("move").checked=true;

    
    if(dop=='d'){
	var select_aim_date =  d3.select("[id=aim_date]");
	
	var di = select_aim_date.property('selectedIndex');
	var sa = select_aim_date
	    .selectAll("option")
	    .filter(function(d,i){return i==di;})
	    .datum();
    
	aim.semaine = sa.semaine;
	aim.an = sa.an;
    } else {
	var select_aim_prof =  d3.select("[id=aim_prof]");
	
	var di = select_aim_prof.property('selectedIndex');
	var sa = select_aim_prof
	    .selectAll("option")
	    .filter(function(d,i){return i==di;})
	    .datum();
    
	aim.prof = sa;
    }
}


// update dd lists for mod-prof-gp
function go_dd(){
    var all_sel = d3.select(".div-filt")
	.selectAll("select")
	.selectAll("option");

    var res = all_sel
	.data(function(d,i,j){return d.arr;})
	.enter()
	.append("option")
//	.merge(all_sel)
	.attr("value", function(d){ return d; })
	.text(function(d){return d;});

    var se = d3.select(".div-filt")
	.selectAll("select")
	.selectAll("option")
	.data(function(d,i,j){return d.arr;})
	.attr("value", function(d){ return d; })
	.text(function(d){return d;});
    
    
    se
	.exit()
	.remove();
    
    // d3.select(".div-filt")
    // 	.selectAll("select")
    // 	.selectAll("option")
    // 	.data(function(d,i,j){return d.arr;})
}

// make the valider button to appear after the first choice
function update_after_first(){
    first_when = false ; 
    d3.select(".msg-sem").text("");

    d3.select("[id=but-val]")
	.append("input")
	.attr("class","crittop")
	.attr("type","button")
	.attr("value","Valider")
	.on("click",send_cours);
}



function send_cours(){

    var cked = '';
    if(document.getElementById("move").checked){
	cked="move";
    } else if (document.getElementById("pend").checked) {
	cked="pend";
    } else if (document.getElementById("cancel").checked) {
	cked="cancel";
    }

    commit = [];
    
    
    d3.select(".cours")
	.selectAll(".ck")
	.select("input")
	.each(function(d,i){
	    if(d3.select(this).property("checked")){
		commit.push(d);
	    }
	});
    console.log(JSON.stringify(commit));

    if(commit.length == 0){
	change_ack("Pas de case cochée, pas de cours décalé !");
	return;
    }
    if(cked == "move" && aim.prof == ""){
	change_ack("Merci d'affecter le(s) cours à quelqu'un.");
	return;
    }

    if(cked != "cancel" && cked != "move" && cked != "pend"){
	change_ack("Choisir l'action à effectuer");
    } else {
	var tot = {os: filtered.semaine,
		   oa: filtered.an,
		   ns: aim.semaine,
		   na: aim.an,
		   np: aim.prof
		  };

	if(cked == "pend"){
	    tot.ns = 1 ;
	    tot.na = 0 ;
	}
	if(cked == "cancel"){
	    tot.ns = 0 ;
	    tot.na = 0 ;
	}

	var sent_data = {} ;
	sent_data['new'] = JSON.stringify(tot) ; 
	sent_data['liste'] = JSON.stringify(commit) ;
	console.log(sent_data);

	show_loader(true);
	$.ajax({
	    url: url_change_decale,
	    type: 'POST',
//	    contentType: 'application/json; charset=utf-8',
	    data: sent_data, //JSON.stringify({'new':tot,'liste':commit}),
	    dataType: 'json',
	    success: function(msg) {
		recv(msg.responseText);
		show_loader(false);
	    },
	    error: function(msg){
		recv(msg.responseText);
		show_loader(false);
	    }
	});
    }
}


function recv(msg){
    var i ;

    console.log("lc",liste_cours)
    console.log("c",commit)

    d3.select(".cours")
	.selectAll(".ck")
	.select("input")
	.property('checked',false);


    if(msg == 'OK'){
	for(i = 0 ; i<commit.length ; i++){
	    var r = liste_cours.indexOf(commit[i]);
	    console.log(r);
	    if(r > -1){
		liste_cours.splice(r,1);
	    }
	}
    }

    go_cours();

    commit = [] ;
    
    change_ack(msg);
}

function change_ack(msg){
    var old = d3.select("[id=ack]").text();
    if(msg==old){
	msg+=".";
    }
    d3.select("[id=ack]").text(msg);
    console.log(msg);
}


function go_cours(){
    var all_cours = d3.select(".cours")
	.selectAll(".ck")
	.data(liste_cours,function(d,i){return i;});

    var co = all_cours
	.enter()
	.append("div")
	.attr("class","ck");

    co
	.append("input")
	.attr("type","checkbox")
	.attr("id",function(d,i){return "c"+i;});

    co   
	.append("label")
	.attr("for",function(d,i){return "c"+i;})
	.merge(all_cours.select("label"))
	.text(plot_cours);
    
    
    all_cours
	.exit()
	.remove();
}


function plot_cours(d){
    var ret = d.m+"-"+d.p+"-"+d.g+" (";
    if(d.j>=0 && d.h>=0){
	ret +=  days[d.j] + " "+ liste_jours[d.j] + " " + hours[d.h];
    } else {
	ret += "non placé"
    }
    ret+=")";
    return ret;
}

function choose_week(check) {
    if(check){
	// check radio button
	document.getElementById("canceled").checked=false;
	document.getElementById("scheduled").checked=true;
    }

    //(could not do it in d3) d3.select(".scheduled").attr("checked","true");

    // change weeks

    // change origin week
    var di = select_orig_date.property('selectedIndex');
    var sa = select_orig_date
	.selectAll("option")
	.filter(function(d,i){return i==di;})
	.datum();
    
    filtered.semaine = sa.semaine;
    filtered.an = sa.an;

    // and change targeted week
    document.getElementById("aim_date").selectedIndex = select_orig_date.property('selectedIndex');
    aim.semaine = filtered.semaine ;
    aim.an = filtered.an ;


    // does not work properly
    // dd list selected attribute is not always refreshed...
    
    // d3.select("[id=aim_date]")
    // 	.selectAll("option")
    // 	.each(function(d,i) {
    // 	    if (d.semaine==sa.semaine && d.an==sa.an){
    // 		d3.select(this).attr("selected","");
    // 		console.log(d);
    // 	    }
    // 	});


    // filter again
    go_filter();
}
