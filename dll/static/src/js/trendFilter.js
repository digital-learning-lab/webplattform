import Vue from 'vue'
import TrendFilterApp from './TrendFilterApp.vue'

if (document.getElementById('trends-app')) {
  new Vue({
    components: {TrendFilterApp},
    template: '<TrendFilterApp/>',
    render: h => h(TrendFilterApp)
  }).$mount('#trends-app')
}