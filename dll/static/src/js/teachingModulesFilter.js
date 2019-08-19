import Vue from 'vue'
import TeachingModulesFilterApp from './TeachingModulesFilterApp.vue'

new Vue({
  components: { TeachingModulesFilterApp },
  template: '<TeachingModulesFilterApp/>',
  render: h => h(TeachingModulesFilterApp)
}).$mount('#teaching-modules-app')
