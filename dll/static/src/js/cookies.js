var accepted = getCookie('cookiesAccepted') === 'true';
if (!accepted) {
    $('.js-cookiebanner').modal({backdrop: 'static', keyboard: false});
}
window.acceptCookies = function () {
    const date = new Date();
    date.setTime(date.getTime() + (window.cookieBannerDuration * 30 * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = "cookiesAccepted=true; " + expires;
    $('.js-cookiebanner').modal('hide');
}