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

var socket;

var opti_timestamp;

var select_opti_date, select_opti_train_prog;
var week_year_sel, train_prog_sel, txt_area;

var launchButton;
var started = false;


function displayConsoleMessage(message){
    while (message.length > 0 && message.slice(-1) == '\n') {
        message = message.substring(0, message.length - 1);
    }

    if (message.length > 0) {
        txt_area.textContent += "\n" + message;
    }

    if (txt_area.selectionStart == txt_area.selectionEnd) {
        txt_area.scrollTop = txt_area.scrollHeight;
    }
}

function start() {
    console.log("GOOO");
    open_connection();
}

function stop() {
    console.log("STOOOOP");

    socket = new WebSocket("ws://" + window.location.host + "/solver/");
    socket.onmessage = function (e) {
        var dat = JSON.parse(e.data);
        dispatchAction(dat);
        displayConsoleMessage(dat['message']);
    }
    socket.onopen = function () {
        socket.send(JSON.stringify({
            'message': 'kill',
            'action': "stop",
            'timestamp': opti_timestamp
        }))
    }

    socket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };
    // Call onopen directly if socket is already open
    if (socket.readyState == WebSocket.OPEN) socket.onopen();
}

function format_zero(x) {
    if (x < 10) {
        return "0" + x;
    }
    return x;
}

function open_connection() {
    var now = new Date();
    opti_timestamp = now.getFullYear() + "-"
        + format_zero(now.getMonth() + 1) + "-"
        + format_zero(now.getDate()) + "--"
        + format_zero(now.getHours()) + "-"
        + format_zero(now.getMinutes()) + "-"
        + format_zero(now.getSeconds());

    socket = new WebSocket("ws://" + window.location.host + "/solver/");

    socket.onmessage = function (e) {
        var dat = JSON.parse(e.data);
        dispatchAction(dat);
        displayConsoleMessage(dat['message']);
    }
    
    socket.onopen = function () {
        // Get current training program abbrev
        var tp = '';
        if (train_prog_sel != text_all) {
            tp = train_prog_sel;
        }

        // Update constraints activation state
        update_constraints_state();

        // Get solver parameters
        var solver = solver_select.value;
        var time_limit = parseInt(time_limit_select.value);

        // Get working copy number for stabilization
        var stabilize_working_copy = stabilize_select.value;

        socket.send(JSON.stringify({
            'message':
                "C'est ti-par.\n" + opti_timestamp + "\nSolver ok?",
            'action': "go",
            'department': department,
            'week': week_year_sel.week,
            'year': week_year_sel.year,
            'train_prog': tp,
            'constraints': constraints,
            'stabilize': stabilize_working_copy,
            'timestamp': opti_timestamp,
            'time_limit': time_limit,
            'solver': solver
        }))
    }

    socket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };
    // Call onopen directly if socket is already open
    if (socket.readyState == WebSocket.OPEN) socket.onopen();
}

/* 
	Drop dpwn list initialization
*/

function init_dropdowns() {
    // create drop down for week selection
    select_opti_date = d3.select("#opti_date");
    select_opti_date.on("change", function () { choose_week(true); fetch_context(); });
    select_opti_date
        .selectAll("option")
        .data(week_list)
        .enter()
        .append("option")
        .text(function (d) { return d[1]; });

    // create drop down for training programme selection
    train_prog_list.unshift(text_all);
    select_opti_train_prog = d3.select("#opti_train_prog");
    select_opti_train_prog.on("change", function () { choose_train_prog(true); fetch_context(); });
    select_opti_train_prog
        .selectAll("option")
        .data(train_prog_list)
        .enter()
        .append("option")
        .text(function (d) { return d; });

    choose_week();
    choose_train_prog();
}

function choose_week() {
    var di = select_opti_date.property('selectedIndex');
    var sa = select_opti_date
        .selectAll("option")
        .filter(function (d, i) { return i == di; })
        .datum();
    week_year_sel = { week: sa[1], year: sa[0] };
}
function choose_train_prog() {
    var di = select_opti_train_prog.property('selectedIndex');
    var sa = select_opti_train_prog
        .selectAll("option")
        .filter(function (d, i) { return i == di; })
        .datum();
    train_prog_sel = sa;
}

/* 
	Context view initialization
*/

function update_context_view(context) {

    if (context) {
        work_copies = context.work_copies;
        constraints = context.constraints;
    }

    init_work_copies(work_copies);
    init_constraints(constraints);
}

/* 
	Working copies list initialization
*/
function init_work_copies(work_copies) {

    copies = work_copies.slice(0);
    copies.unshift("-");

    // Display or hide working copies list
    stabilize_div = d3.select("#stabilize");
    if (work_copies.length == 0) {
        stabilize_div.style("display", "none");
    }
    else {
        stabilize_div.style("display", "block");
    }

    // Update working copies list
    stabilize_sel = stabilize_div.select("select");

    stabilize_sel_data = stabilize_sel 
        .selectAll("option")
        .data(copies);

    stabilize_sel_data    
        .enter()
        .append("option")
        .attr('value', (d) => d)
        .text((d) => d);

    stabilize_sel_data.exit().remove();
}


/* 
    Constraints view initialization
*/
function init_constraints(constraints) {

    // On vérifie si le navigateur prend en charge
    // l'élément HTML template en vérifiant la présence
    // de l'attribut content pour l'élément template.
    if ("content" in document.createElement("template")) {

        // On prépare une ligne pour le tableau 
        var t = document.querySelector("#constraints_template");

        // On clone la ligne et on l'insère dans le tableau
        var container = document.querySelector("#constraints");
        var current = container.querySelector("#constraints_list");
        var target = document.createElement("div");
        target.id = "constraints_list";
        container.replaceChild(target, current);

        // Create new template for each constraint
        constraints.forEach((constraint, index) => {
            if(!constraint)
                return;
                
            var constraintId = `${constraint.model}_${constraint.pk}`;

            var clone = document.importNode(t.content, true);

            // Display state 
            var checkbox = clone.querySelector("input[type=checkbox]");
            checkbox.setAttribute('id', constraintId);
            checkbox.setAttribute('value', index);
            checkbox.checked = constraint.is_active;

            // Display title
            var label = clone.querySelector("label");
            label.setAttribute('for', constraintId)
            label.className = "title"
            label.textContent = constraint.name;

            // Display mandatory
            if (constraint.details.weight) {
                label.classList.add("mandatory");
            }

            // Display description
            var description = clone.querySelector("#description");
            if (constraint.description) {
                description.textContent = constraint.description;
            }

            // Display explanation
            var explanation = clone.querySelector("#explanation");
            if (constraint.explanation) {
                explanation.textContent = constraint.explanation;
            }

            // Display comment
            if (constraint.comment) {
                var comment = clone.querySelector("#comment");
                comment.textContent = constraint.comment;
            }

            // Display details items
            var details = clone.querySelector("#details")

            for (var key in constraint.details) {
                var detail = document.createElement("div")
                details.appendChild(detail)

                var content = document.createTextNode(`${key} : ${constraint.details[key]}`)
                detail.appendChild(content)
            }

            target.appendChild(clone);
        });

    } else {
        // Une autre méthode pour ajouter les lignes
        // car l'élément HTML n'est pas pris en charge.
        alert('template element are not supported')
    }
}

/* 
	Get constraints list with updated state propepety
*/

function update_constraints_state() {
    var checkboxes = document.querySelectorAll("#constraints input[type=checkbox]");
    checkboxes.forEach(c => {
        constraints[c.value].is_active = c.checked;
    });
}

/* 
	Get constraints async
*/

function get_constraints_url(train_prog, year, week) {

    let params = arguments;
    let regexp = /(tp)\/(1111)\/(11)/;
    let replacer = (match, train_prog, year, week, offset, string) => {
        return Object.values(params).join('/');
    }

    return fetch_context_url_template.replace(regexp, replacer)
}

function fetch_context() {
    $.ajax({
        type: "GET",
        dataType: 'json',
        url: get_constraints_url(train_prog_sel, week_year_sel.year, week_year_sel.week),
        async: true,
        contentType: "application/json; charset=utf-8",
        success: function (context) {
            update_context_view(context);
        },
        error: function (msg) {
            console.log("error");
        },
        complete: function (msg) {
            console.log("complete");
        }
    });
}


/*
	Start or stop edt resolution
*/
function manageSolverProcess(event) {
    if (started) {
        changeState('stop');
    }
    else {
        changeState('start');
    }
}
/* 
Update interface state
*/
function changeState(targetState) {
    switch (targetState) {
        case 'start':
            launchButton.value = 'Stop';
            started = true;
            start();
            break;
        case 'stop':
            launchButton.value = 'Go';
            started = false;
            stop();
        case 'stopped':
            launchButton.value = 'Go';
            started = false;
        default:
            break;
    }
}

/*
	Dispatch websocket received action 
*/
function dispatchAction(token) {
    let action = token.action;
    let message = token.message;

    if (!action) {
        console.log('unrecognized action' + token);
        return;
    }

    if (action != 'info')
        changeState('stopped');
}

/*
	Main process
*/

var solver_select = document.querySelector("#solver")
var stabilize_select = document.querySelector("#stabilize select")

time_limit_select = document.querySelector("#limit")
txt_area = document.getElementsByTagName("textarea")[0];

launchButton = document.querySelector("#launch")
if (launchButton)
    launchButton.addEventListener("click", manageSolverProcess);

init_dropdowns();
update_context_view();
