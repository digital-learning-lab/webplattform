import Vue from 'vue'
import ToolFilterApp from './ToolFilterApp.vue'

new Vue({
  components: { ToolFilterApp },
  template: '<ToolFilterApp/>',
  render: h => h(ToolFilterApp)
}).$mount('#tools-app')
