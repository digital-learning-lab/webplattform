import $ from 'jquery'
import Vue from 'vue'

$('.content-teaser__competence, .information-area__icon').tooltip({
  trigger: 'hover'
})

export const tooltipDirective = Vue.directive('tooltip', function(el, binding){
    $(el).tooltip({
             title: binding.value,
             trigger: 'hover'
         })
})
