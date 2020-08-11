<template>
  <a class="content-teaser" :class="contentClass" :href="content.url">
    <div class="content-teaser__image-container">
      <img v-if="content.image" class="content-teaser__image" :src="content.image" srcset="" :alt="'Vorschaubild ' + content.name ">
    </div>
    <div class="content-teaser__body">
      <div class="content-teaser__type">{{ content.type_verbose }}</div>
      <div class="content-teaser__title">{{ content.name }}</div>
      <div class="content-teaser__abstract">{{ content.teaser }}</div>
      <div class="content-teaser__footer">
        <div class="content-teaser__competences">
          <span v-for="competence in content.competences" class="content-teaser__competence" :class="competence"></span>
        </div>
        <div class="content-teaser__upload-date-container" v-if="content.type === 'teaching-module'">
          <span class="content-teaser__upload-icon icon-upload"></span>
          <span class="content-teaser__upload-date">
              {{ content.created }}
            </span>
        </div>
      </div>
    </div>
  </a>
</template>

<script>
  export default {
    name: 'ContentTeaser',
    props: {
      content: {
        type: Object,
        default: function () {
          return {}
        }
      }
    },
    computed: {
      contentClass: function () {
        return this.content.type ? `content-teaser--${this.content.type}` : ''
      }
    }
  }
</script>

<style scoped>

</style>