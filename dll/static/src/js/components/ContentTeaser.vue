<template>
  <a class="content-teaser" :class="contentClass" :href="content.url">
    <div class="content-teaser__image-container">
      <img v-if="content.image" class="content-teaser__image" :src="content.image" srcset="" :alt="'Vorschaubild ' + content.name ">
    </div>
    <div class="content-teaser__body">
      <div class="content-teaser__type">{{ content.type_verbose }}</div>
      <div class="content-teaser__favor" v-if="content.favored">
        <span class="fa fa-heart favor-icon favor-icon--active">
          <span class="sr-only">Auf dem Merkzettel</span>
        </span>
      </div>
      <div class="clearfix"></div>
      <div class="content-teaser__title">{{ content.name }}</div>
      <div class="content-teaser__abstract">{{ content.teaser }}</div>
      <div class="content-teaser__footer">
        <div class="content-teaser__competences">
          <span v-for="competence in content.competences" class="content-teaser__competence" :class="competence.icon"  v-tooltip="competence.name"></span>
        </div>
      </div>
    </div>
  </a>
</template>

<script>
  import { tooltipDirective } from '../tooltips'

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
    },
    directives: {
      tooltip: tooltipDirective
    }
  }
</script>

<style scoped>

</style>