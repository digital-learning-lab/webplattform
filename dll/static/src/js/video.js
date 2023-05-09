
function checkYoutubeAllowed() {
    const youtubeAllowed = getCookie('youtubeAllowed') === 'true';
    if (youtubeAllowed) {
        const iframes = document.querySelectorAll('iframe');
        iframes.forEach(function (iframe) {
            if (iframe.srcdoc) {
                iframe.removeAttribute('srcdoc');
            }
        });
    }
}

window.allowYoutube = function () {
    const date = new Date();
    date.setTime(date.getTime() + (6 * 30 * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = "youtubeAllowed=true; " + expires;
    checkYoutubeAllowed();
}

checkYoutubeAllowed();
