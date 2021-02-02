import $ from 'jquery'
import axios from 'axios'

class Trigger {
  constructor(type, delay, survey, url, targetSelector) {
    /*
     * Setup Trigger instance. Load survey html content asynchronously.
     */
    this.delay = delay
    this.url = url
    this.type = type
    this.survey = survey
    this.targetSelector = targetSelector
    var surveys = localStorage.getItem('surveys') || ""
    surveys = surveys.split(",")
    if (!surveys.includes(survey.toString())) {
      this.getSurveyContent().then((res) => {
        this.html = res.data
        this.setup()
      })
    }
  }
  setup() {
    let listenerFunc = (e) => {
      // Show leave intent only once.
      if (this.type === 'leaveIntent') {
        document.removeEventListener('mouseleave', listenerFunc)
      }
      // Check if click events corresponds to given target selector.
      if (this.type === 'click') {
        if (!Array.from(document.querySelectorAll(this.targetSelector)).includes(e.target)) {
          return
        }
      }
      // Remove listener after first call.
      if (this.type === 'click' || this.type === 'scroll') {
        window.removeEventListener(this.type, listenerFunc)
        document.removeEventListener(this.type, listenerFunc)
      }
      // Show survey modal with given html after defined timeout.
      setTimeout(() => {
        var modalElement = $('.js-surveyModal');
        modalElement.off('submit');
        this.setupModalSubmit();
        var modal = modalElement.modal()
        modal.find('.modal-body').html(this.html)
        modal.show()
      }, this.delay)
    }
    // Only append leave intent event listener when url matches.
    if (this.type === 'leaveIntent' && window.location.pathname === this.url) {
      document.addEventListener('mouseleave', listenerFunc)
      return
    }
    // Only append pageOpen event listener when url matches.
    if (this.type === 'pageOpen' && window.location.pathname === this.url) {
      listenerFunc()
      return
    }
    if (this.type === 'scroll') {
      document.addEventListener(this.type, listenerFunc)
      return
    }
    if (this.type === 'login') {
      if (window.loginTrigger) {
        listenerFunc()
      }
      return
    }
    // Otherwise append event trigger type to window.
    window.addEventListener(this.type, listenerFunc)
  }
  setupModalSubmit () {
    $('.js-surveyModal').on('submit', `#survey-${this.survey}`, (e) => {
      e.preventDefault()
      axios.post(`/surveys/${this.survey}`, $(e.target).serialize()).then(res => {
        var modal = $('.js-surveyModal').modal()
        if (!res.data.success) {
          this.html = res.data.form
          modal.find('.modal-body').html(this.html)
        } else {
          modal.modal('hide')
          var surveys = localStorage.getItem('surveys') || ""
          surveys += `,${this.survey}`
          localStorage.setItem('surveys', surveys)
        }
      }).catch(err => {
        console.log(err)
      })
      return false
    })
  }
  getSurveyContent() {
    /*
     * Retrieve survey html content asynchronously.
     */
    return axios.get(`/surveys/${this.survey}`)
  }
}

function setupTrigger(triggerArray) {
  for (let i = 0; i < triggerArray.length; i++) {
    const trigger = triggerArray[i];
    new Trigger(trigger.event, trigger.delay, trigger.survey, trigger.url, trigger.target)
  }
}

function getTriggers(url) {
  if (!url) {
    url = '/api/triggers'
  }
  axios.get(url).then(res => {
    setupTrigger(res.data.results);
    if (res.data.next) {
      getTriggers(res.data.next);
    }
  })
}

getTriggers();