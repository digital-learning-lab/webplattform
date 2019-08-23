import Vue from 'vue'
import ToolSubmissionApp from './ToolSubmissionApp.vue'

if (document.getElementById('tool-submission')) {
  new Vue({
    components: {ToolSubmissionApp},
    template: '<ToolSubmissionApp/>',
    render: h => h(ToolSubmissionApp)
  }).$mount('#tool-submission')
}
