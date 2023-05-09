import $ from 'jquery'
import axios from 'axios'

function getCookie(name) {
   var cookieValue = null;
   if (document.cookie && document.cookie != '') {
       var cookies = document.cookie.split(';');
       for (var i = 0; i < cookies.length; i++) {
           var cookie = jQuery.trim(cookies[i]);
           // Does this cookie string begin with the name we want?
           if (cookie.substring(0, name.length + 1) == (name + '=')) {
               cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
               break;
           }
       }
   }
   return cookieValue;
}
window.getCookie = getCookie;
$('.js-sidebar-nav-item').click(function (e) {
  $('html, body').animate({scrollTop: $('.js-tab-content').offset().top - $('.js-header').height() - 40}, 400)
})

$('.js-favor, .js-unfavor').click(function (e) {
  const url = e.target.dataset.url;
  axios.post(url, {}, {
    headers: {
      'X-CSRFToken': getCookie('csrftoken')
    }
  })
    .then(res => {
      if (e.target.classList.contains('js-favor')) {
        $('.js-toast-body').text(favorAddedText)
        $(e.target).addClass('d-none')
        $('.js-unfavor').removeClass('d-none')
      } else {
        $('.js-toast-body').text(favorRemovedText)
        $(e.target).addClass('d-none')
        $('.js-favor').removeClass('d-none')
      }
      $('.js-toast').toast('show')
    })
    .catch(err => {
      console.log(err)
    })
  e.preventDefault();
  return false;
})

$('.js-toast').toast({
  delay: 3000
})
