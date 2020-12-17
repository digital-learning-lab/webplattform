class WagtailAccordion {
  constructor(element) {
    this.element = $(element);
    this.init()
  }

  init () {
    var button = $("<button type='button' class='collapse-button'></button>");
    button.click(() => {
      button.toggleClass('is-active');
      this.element.toggle();
    });
    button.insertBefore(this.element);
  }
}

var counter = 0;

function setupAccordions () {
  var elements = document.querySelectorAll('.collapse--custom');
  if (elements.length === 0 && counter <= 4) {
    counter++;
    setTimeout(setupAccordions, 500);
    return;
  }
  for (var i = 0; i < elements.length; i++) {
    new WagtailAccordion(elements[i]);
  }
  return;
}

setTimeout(setupAccordions, 500);
