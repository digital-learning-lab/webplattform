import $ from 'jquery'

$('.js-navigation-toggle').click(function (e) {
  $('.navigation').toggleClass('navigation--is-active')
  $('.navigation-toggle').toggleClass('navigation-toggle--is-active')
})
$('.js-navigation__item').click(function (e) {
  $('.navigation').removeClass('navigation--is-active')
  $('.navigation-toggle').removeClass('navigation-toggle--is-active')
})