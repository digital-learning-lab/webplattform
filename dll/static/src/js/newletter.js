import $ from 'jquery';
if (window.location.search.includes('newsletter=true')) {
    var toastEle = $('.js-toast');
    toastEle.toast({
      delay: 8000
    });
    $('.js-toast-head').text('Newsletter');
    $('.js-toast-body').text('Sie haben sich erfolgreich für unseren Newsletter angemeldet!')
    toastEle.toast('show');
}