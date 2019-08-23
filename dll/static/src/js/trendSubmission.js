import Vue from 'vue'
import TrendSubmissionApp from './TrendSubmissionApp.vue'

if (document.getElementById('trend-submission')) {
  new Vue({
    components: {TrendSubmissionApp},
    template: '<TrendSubmissionApp/>',
    render: h => h(TrendSubmissionApp)
  }).$mount('#trend-submission')
}
