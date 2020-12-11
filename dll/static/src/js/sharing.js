import $ from 'jquery';

$(function () {
  $('.js-share-content').popover({
    html: true,
    sanitize: false,
    trigger: 'focus'
  })
})
