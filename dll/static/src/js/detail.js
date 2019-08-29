import $ from 'jquery'

$('.js-sidebar-nav-item').click(function (e) {
  $('html, body').animate({scrollTop: $('.js-tab-content').offset().top - $('.js-header').height() - 40}, 400)
})
