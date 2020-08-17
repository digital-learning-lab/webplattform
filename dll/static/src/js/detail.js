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
        $(e.target).parent().addClass('d-none')
        $('.js-unfavor').parent().removeClass('d-none')
      } else {
        $(e.target).parent().addClass('d-none')
        $('.js-favor').parent().removeClass('d-none')
      }
    })
    .catch(err => {
      console.log(err)
    })
  e.preventDefault();
  return false;
})
