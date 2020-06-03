import $ from 'jquery'
$(document).ready(function () {
    if (typeof grecaptcha !== 'undefined') {
        grecaptcha.ready(function () {
            grecaptcha.execute(websiteKey, {action: 'generate_link'}).then(function (token) {
                $('[name="g-recaptcha-response"]').val(token);
            });
        });
    }
})
