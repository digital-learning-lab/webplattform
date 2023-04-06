import $ from 'jquery';
$(function () {
  function checkScroll(e) {
    if (window.scrollY > 100) {
      $(".js-scroll-to-top").addClass("show");
    } else {
      $(".js-scroll-to-top").removeClass("show");
    }
  }
  $(window).on("scroll", checkScroll);
  $(".js-scroll-to-top").click(() => {
    $("html, body").animate({ scrollTop: 0 }, "slow");
  });
  setTimeout(checkScroll, 300);
});
