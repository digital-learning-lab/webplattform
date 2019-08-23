import Vue from 'vue'
import TeachingModuleSubmissionApp from './TeachingModuleSubmissionApp.vue'

if (document.getElementById('teaching-module-submission')) {
  new Vue({
    components: {TeachingModuleSubmissionApp},
    template: '<TeachingModuleSubmissionApp/>',
    render: h => h(TeachingModuleSubmissionApp)
  }).$mount('#teaching-module-submission')
}
