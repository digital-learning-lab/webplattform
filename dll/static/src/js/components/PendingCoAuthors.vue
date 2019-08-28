<template>
  <div v-if="pending_co_authors.length">
    <p>Folgende Co-Autor_innen haben eine ausstehende Einladung:
    </p>
    <ul class="list-unstyled">
      <li v-for="author in pending_co_authors">
        {{ author }}
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'PendingCoAuthors',
    props: {
      pending_co_authors: {
        type: Array,
        default: () => {
          return []
        },
        required: true
      }
    }
  }
</script>

<style scoped>

</style>