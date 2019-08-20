<template>
  <form class="mb-4">
    <div v-if="mode === 'create'">
      123
    </div>
  </form>
</template>

<script>

  export default {
    name: 'ContentSubmissionApp',
    data () {
      return {
        mode: 'create'
      }
    }
  }
</script>

<style scoped>

</style>