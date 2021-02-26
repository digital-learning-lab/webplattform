import $ from 'jquery'

$('.js-navigation-toggle').click(function (e) {
  $('.navigation').toggleClass('navigation--is-active')
  $('.navigation-toggle').toggleClass('navigation-toggle--is-active')
})
$('.js-navigation__item').click(function (e) {
  $('.navigation').removeClass('navigation--is-active')
  $('.navigation-toggle').removeClass('navigation-toggle--is-active')
})
$('.js-navigation-scroll').click(function (e) {
  if (e.target && e.target.href) {
    const url = new URL(e.target.href)
    if (url.hash && window.location.pathname === url.pathname && window.location.hostname === url.hostname) {
      e.preventDefault();
      $('html, body').animate({scrollTop: $(url.hash).offset().top - $('.js-header').height() - 20})
    }
  }
})
$('.navigation').addClass('navigation--transition')