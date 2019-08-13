import $ from 'jquery'

$(document).scroll(function (e) {
  if ($(document).scrollTop() >= 10) {
    $('.js-header').addClass('header-border')
  } else {
    $('.js-header').removeClass('header-border')
  }
})
