import Vue from 'vue'
import OverviewApp from './OverviewApp.vue'

if (document.getElementById('overview-app')) {
  new Vue({
    components: {OverviewApp},
    template: '<OverviewApp/>',
    render: h => h(OverviewApp)
  }).$mount('#overview-app')
}
