import $ from 'jquery'

window.submitWithReCaptcha = function() {
    let form = $(this);
    grecaptcha.ready(function () {
        grecaptcha.execute(websiteKey, {action: 'generate_link'}).then(function (token) {
            $('[name="g-recaptcha-response"]').val(token);
            form.submit()
        });
    });
}
