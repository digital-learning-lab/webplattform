<template>
  <div class="row mt-5 mb-5">
    <div class="col col-3">
      <div class="section-info">
        <form action="">
          <h2>Filtern nach</h2>

          <h3>Sortierung</h3>
          <select name="sortby" id="sortby-select" v-model="sortBy">
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3>Schlagwortsuche</h3>
          <input type="text" v-model="searchTerm" name="searchTerm">
          <h3>Auswahl</h3>
          <ul class="list-unstyled">
            <li>
              <input type="checkbox" id="teaching-modules-checkbox" v-model="showTeachingModules">
              <label for="teaching-modules-checkbox">Unterrichtsbausteine</label>
            </li>
            <li>
              <input type="checkbox" id="tools-checkbox" v-model="showTools">
              <label for="tools-checkbox">Tools</label>
            </li>
            <li>
              <input type="checkbox" id="trends-checkbox" v-model="showTrends">
              <label for="trends-checkbox">Trends</label>
            </li>
          </ul>
        </form>
      </div>
    </div>
    <div class="col col-9">
      <h1>{{ competence.name }}</h1>
      <p class="mb-5">{{ competence.description }}</p>
      <div class="row">
        <div class="col col-12 col-md-6 mb-4" v-for="content in sortedAndFilteredContents">
          <app-content-teaser :content="content"></app-content-teaser>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import ContentTeaser from './components/ContentTeaser.vue'

  export default {
    name: 'CompetenceFilterApp',
    components: {
      'AppContentTeaser': ContentTeaser
    },
    data () {
      return {
        contents: [
          {name: 'edulabs1', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'trend', type_verbose: 'Trend', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs2', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'teaching-module', type_verbose: 'Unterrichtsbaustein', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs3', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'tool', type_verbose: 'Tool', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs4', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'trend', type_verbose: 'Trend', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs5', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'teaching-module', type_verbose: 'Unterrichtsbaustein', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs6', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'trend', type_verbose: 'Trend', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs7', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'tool', type_verbose: 'Tool', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs8', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'trend', type_verbose: 'Trend', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'edulabs9', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'tool', type_verbose: 'Tool', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'aedulabs', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'teaching-module', type_verbose: 'Unterrichtsbaustein', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'bedulabs', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'trend', type_verbose: 'Trend', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'cedulabs', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'teaching-module', type_verbose: 'Unterrichtsbaustein', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'dedulabs', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'tool', type_verbose: 'Tool', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']},
          {name: 'eedulabs', image: '/media/filer_public_thumbnails/filer_public/54/f7/54f765bc-c0d0-44bc-8b65-97cf7b838c75/edulabs.jpg__750x500_q85_subsampling-2_upscale.jpg', type: 'trend', type_verbose: 'Trend', teaser: 'Lorem', competences: ['suchen-verarbeiten-aufbewahren', 'kommunizieren-kooperieren']}
        ],
        competence: {
          name: 'Kommunizieren & Kooperieren',
          description: 'Um im digitalen Raum adäquat KOMMUNIZIEREN & KOOPERIEREN zu können, braucht es entsprechende Kompetenzen, digitale Werkzeuge zur angemessenen und effektiven Kommunikation einsetzen und in digitalen Umgebungen zielgerichtet kooperieren zu können. Dabei geht es vor allem darum, entsprechend der jeweiligen Situation und ausgerichtet an den Kommunikations- bzw. Kooperationspartnern die passenden Werkzeuge auszuwählen und entsprechende Umgangsregeln einzuhalten.'
        },
        sortBy: 'az',
        searchTerm: '',
        showTeachingModules: true,
        showTrends: true,
        showTools: true
      }
    },
    methods: {
      sortContents (a, b) {
        const nameA = a.name.toUpperCase();
        const nameB = b.name.toUpperCase();

        let comparison = 0;
        if (nameA > nameB) {
          comparison = 1;
        } else if (nameA < nameB) {
          comparison = -1;
        }

        return this.sortBy === 'az' ? comparison : -comparison;
      }
    },
    computed: {
      sortedAndFilteredContents () {
        let filteredContents = this.contents.filter((content) => {
          if (content.type === 'teaching-module') {
            return this.showTeachingModules
          }
          if (content.type === 'trend') {
            return this.showTrends
          }
          if (content.type === 'tool') {
            return this.showTools
          }
        })
        return filteredContents.sort(this.sortContents)

      }
    },
    created () {
    }
  }
</script>

<style scoped>

</style>