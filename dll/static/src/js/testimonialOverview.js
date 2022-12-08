import Vue from 'vue'
import TestimonialOverviewApp from './TestimonialOverviewApp.vue'

if (document.getElementById('testimonial-overview-app')) {
  new Vue({
    components: {TestimonialOverviewApp},
    template: '<TestimonialOverviewApp/>',
    render: h => h(TestimonialOverviewApp)
  }).$mount('#testimonial-overview-app')
}
