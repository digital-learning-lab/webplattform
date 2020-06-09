function mouseOverEffect(object, svgDoc, komp, color) {
    if (!color) {
        color = 'black';
    }
    object.setAttribute("cursor", "pointer");
    var id_value =  object.getAttribute( 'data-element_type' );
    var element = svgDoc.getElementById(id_value);
    if (komp) {
        element.setAttribute("fill", "#376e78");
    } else {
        element.setAttribute("fill", color);
    }
}

function mouseOutEffect(object, svgDoc, komp, color) {
    if (!color) {
        color = 'white'
    }
    var id_value =  object.getAttribute( 'data-element_type' );
    var element = svgDoc.getElementById(id_value);
    if (komp) {
        element.setAttribute("fill", "#00232d");
    } else {
        element.setAttribute("fill", color);
    }
}
// Get thelement = svgDoc.getElementById(id_value);e Object by ID
var a = document.getElementById("dllflower");
if (a) {
    // Get the SVG-elements inside the Object tag
    var svgDoc = a;
    // Get one of the SVG-elements by ID;
    var ubausteine = svgDoc.getElementById("ubausteine_trigger");
    var trends = svgDoc.getElementById("trends_trigger");
    var tools = svgDoc.getElementById("tools_trigger");
    var kompetenzen = svgDoc.getElementsByClassName('st6');
    var base = svgDoc.getElementsByClassName('st7');

    for (var i = 0; i < base.length; i++) {
        base[i].addEventListener("click", function(){
            // get ID-Value of SVG-Element
            var id_value = this.getAttribute( 'data-element_type' );
            // relocate to a new page
            window.location="/" + id_value;
        });
    }

    ubausteine.addEventListener('mouseover', function () { mouseOverEffect(this, svgDoc, false, "#961423") });
    ubausteine.addEventListener('mouseout', function () { mouseOutEffect(this, svgDoc, false, "#e14141") });
    tools.addEventListener('mouseover', function () { mouseOverEffect(this, svgDoc, false, "#1e468c") });
    tools.addEventListener('mouseout', function () { mouseOutEffect(this, svgDoc, false, "#0078a5") });
    trends.addEventListener('mouseover', function () { mouseOverEffect(this, svgDoc, false, "#96784b") });
    trends.addEventListener('mouseout', function () { mouseOutEffect(this, svgDoc, false, "#c8b482") });

    for (var i = 0; i < kompetenzen.length; i++) {
        // get ID-Value of SVG-Element
        kompetenzen[i].addEventListener('click', function() {
            // relocate to a new page
            var id_value = this.getAttribute( 'data-element_type' );
            window.location = "/kompetenz/" + id_value;

        });

        kompetenzen[i].addEventListener('mouseover', function () { mouseOverEffect(this, svgDoc, true) });
        kompetenzen[i].addEventListener('mouseout', function () { mouseOutEffect(this, svgDoc, true) });

    }
}
