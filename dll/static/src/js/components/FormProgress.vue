<template>
  <div>
    <div v-for="idx, step in steps">
      <img :src="`/static/img/forms/step_${idx}.svg`" alt="">
    </div>
  </div>
</template>

<script>
  export default {
    name: 'FormProgress',
    props: {
      steps: {
        type: Array,
        required: true,
        default: () => {
          return []
        }
      },
      active: {
        type: Number,
        default: 0,
        required: false
      }
    }
  }
</script>

<style scoped>

</style>