import $ from 'jquery'
import axios from 'axios'

class Trigger {
  constructor(type, delay, survey) {
    this.html = ''
    this.getSurveyContent(survey)
    window.addEventListener(type, () => {
      setTimeout(() => {
        var modal = $('.js-surveyModal').modal()
        modal.find('.modal-body').html(this.html)
        modal.show()
      }, delay)
    })
  }

  getSurveyContent(survey) {
    axios.get('/surveys/' + survey).then(
      (res) => {
        this.html = res.data
      }
    )
  }
}


window.Trigger = Trigger
