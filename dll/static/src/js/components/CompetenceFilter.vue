<template>
  <div>
    <h3 class="form-subhead">Kompetenzen in der digitalen Welt</h3>
    <ul class="list-unstyled">
      <li class="form-check">
        <input class="form-check-input" type="checkbox" id="competence-1" name="competenceType" value="1" @change="update" v-model="competences">
        <label class="form-check-label" for="competence-1">Suchen, Verarbeiten & Aufbewahren</label>
      </li>
      <li class="form-check">
        <input class="form-check-input" type="checkbox" id="competence-2" name="competenceType" value="2" @change="update" v-model="competences">
        <label class="form-check-label" for="competence-2">Kommunizieren & Kooperieren</label>
      </li>
      <li class="form-check">
        <input class="form-check-input" type="checkbox" id="competence-3" name="competenceType" value="3" @change="update" v-model="competences">
        <label class="form-check-label" for="competence-3">Produzieren & Präsentieren</label>
      </li>
      <li class="form-check">
        <input class="form-check-input" type="checkbox" id="competence-4" name="competenceType" value="4" @change="update" v-model="competences">
        <label class="form-check-label" for="competence-4">Schützen & sicher Agieren</label>
      </li>
      <li class="form-check">
        <input class="form-check-input" type="checkbox" id="competence-5" name="competenceType" value="5" @change="update" v-model="competences">
        <label class="form-check-label" for="competence-5">Problemlösen & Handeln</label>
      </li>
      <li class="form-check">
        <input class="form-check-input" type="checkbox" id="competence-6" name="competenceType" value="6" @change="update" v-model="competences">
        <label class="form-check-label" for="competence-6">Analysieren & Reflektieren</label>
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: 'CompetenceFilter',
    data () {
      return {
        competences: []
      }
    },
    methods: {
      update () {
        this.$emit('update:competences', this.competences)
      }
    }
  }
</script>

<style scoped>

</style>