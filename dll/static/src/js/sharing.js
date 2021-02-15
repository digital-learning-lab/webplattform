import $ from 'jquery';

$(function () {
  $('.js-share-content').popover({
    html: true,
    sanitize: false,
    trigger: 'focus'
  });
  $("body").on("click", "[data-share]", (e) => {
    var value = $(e.target).closest("[data-share]").data("share");
    _paq.push(["trackEvent", "Sharing", value, window.location.href]);
  });
});
