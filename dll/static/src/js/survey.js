import $ from 'jquery'
import axios from 'axios'

class Trigger {
  constructor(type, delay, survey, url) {
    this.delay = delay
    this.url = url
    this.type = type
    this.getSurveyContent(survey).then((res) => {
      this.html = res.data
      this.setup()
    })
  }
  listenerFunc () {
    if (this.type === 'leaveIntent') {
      document.removeEventListener('mouseleave', this.listenerFunc)
    }
    setTimeout(() => {
      var modal = $('.js-surveyModal').modal()
      modal.find('.modal-body').html(this.html)
      modal.show()
    }, this.delay)
  }

  setup() {
    if (this.type === 'leaveIntent' && window.location.pathname === this.url) {
      document.addEventListener('mouseleave', this.listenerFunc)
      return
    }
    if (this.type === 'pageOpen' && window.location.pathname === this.url) {
      this.listenerFunc()
      return
    }
    window.addEventListener(this.type, this.listenerFunc)
  }

  getSurveyContent(survey) {
    return axios.get('/surveys/' + survey)
  }
}


window.Trigger = Trigger
