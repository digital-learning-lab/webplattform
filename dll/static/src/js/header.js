import $ from 'jquery'

$(document).scroll(() => {
  if ($(document).scrollTop() >= 10) {
    $('.js-header').addClass('header-border')
  } else {
    $('.js-header').removeClass('header-border')
  }
})