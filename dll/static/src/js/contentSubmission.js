import Vue from 'vue'
import ContentSubmissionApp from './ContentSubmissionApp.vue'

new Vue({
  components: { ContentSubmissionApp },
  template: '<ContentSubmissionApp/>',
  render: h => h(ContentSubmissionApp)
}).$mount('#content-submission')
