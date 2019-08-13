import Vue from 'vue'
import CompetenceFilterApp from './CompetenceFilterApp.vue'

new Vue({
  components: { CompetenceFilterApp },
  template: '<CompetenceFilterApp/>',
  render: h => h(CompetenceFilterApp)
}).$mount('#filter-app')
