import Vue from 'vue'
import TrendFilterApp from './TrendFilterApp.vue'

new Vue({
  components: { TrendFilterApp },
  template: '<TrendFilterApp/>',
  render: h => h(TrendFilterApp)
}).$mount('#trends-app')
