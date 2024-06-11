<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4 mb-4">
      <div class="section-info">
        <div v-if="windowWidth < 1200" class="row d-lg-none">
          <div class="col-12">
            <h1 class="mb-3" v-html="windowCom.competenceName" />
          </div>
          <div class="col-12 mb-4" v-html="windowCom.videoEmbed" />
          <div class="col-12">
            <p>
              <b class="font-weight-bold" v-html="windowCom.competenceTextTitle" />
            </p>
            <p class="mb-5 d-lg-none" v-html="windowCom.competenceText" />
          </div>
        </div>

        <form id="filterForm" :action="dataUrl" class="d-lg-block collapse" method="get">
          <h2>Filtern nach</h2>

          <h3 class="form-subhead">Sortierung</h3>
          <select id="sortby-select" v-model="sorting" class="form-control" name="sortby" @change="updateContents">
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input v-model="q" class="form-control" name="searchTerm" type="text" @keydown="preventEnter" />
          <h3 class="form-subhead">Auswahl</h3>
          <ul class="list-unstyled">
            <li class="form-check">
              <input
                id="teaching-modules-checkbox"
                v-model="teachingModules"
                class="form-check-input"
                type="checkbox"
                @change="updateContents"
              />
              <label class="form-check-label" for="teaching-modules-checkbox">Unterrichtsbausteine</label>
            </li>
            <li class="form-check">
              <input
                id="tools-checkbox"
                v-model="tools"
                class="form-check-input"
                type="checkbox"
                @change="updateContents"
              />
              <label class="form-check-label" for="tools-checkbox">Tools</label>
            </li>
            <li class="form-check">
              <input
                id="trends-checkbox"
                v-model="trends"
                class="form-check-input"
                type="checkbox"
                @change="updateContents"
              />
              <label class="form-check-label" for="trends-checkbox">Trends</label>
            </li>
          </ul>
        </form>
        <div class="text-center d-lg-none">
          <button
            class="button button--primary"
            data-bs-target="#filterForm"
            data-bs-toggle="collapse"
            aria-controls="filterForm"
            aria-expanded="false"
            type="button"
          >
            Filter ausklappen <span class="fas fa-chevron-circle-down" ></span>
          </button>
        </div>
      </div>
    </div>
    <div class="col col-12 col-lg-7 col-xl-8">
      <div v-if="windowWidth >= 1200" class="section-info mb-5">
        <div class="row">
          <div class="col-12">
            <h1 class="d-none d-lg-block text-center mb-5" v-html="windowCom.competenceName" />
          </div>
          <div class="col-lg-12 col-xl-7 mb-4" v-html="windowCom.videoEmbed" />
          <div class="col-lg-12 col-xl-5">
            <p>
              <b class="font-weight-bold" v-html="windowCom.competenceTextTitle" />
            </p>
            <p class="mb-5 d-none d-lg-block" v-html="windowCom.competenceText" />
          </div>
        </div>
      </div>
      <div v-if="contents.length > 0 || loading" class="row">
        <div v-for="(content, index) in contents" :key="index" class="col col-12 col-xl-6 mb-4">
          <ContentTeaser :content="content" />
        </div>
        <AppPagination
          v-model:current-page="currentPage"
          v-model:pagination="pagination"
          @jump-to="jumpTo"
          @next-page="nextPage"
          @previous-page="previousPage"
        />
      </div>
      <div v-else class="row">
        <div class="col">
          <h2>Ihre Suchanfrage ergab keine Treffer.</h2>
          <p>
            Bitte versuchen Sie es mit anderen Suchbegriffen oder schauen Sie gern auf anderen Datenbanken für freie
            Unterrichtsmaterialien wie
            <a href="https://oerhoernchen.de/suche" rel="noopener noreferrer" target="_blank">OERhörchen</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watchEffect } from 'vue';

import AppPagination from '../components/AppPagination.vue';
import ContentTeaser from '../components/ContentTeaser.vue';
import { useContentFilter } from '../composables/contentFilter';
import { usePagination } from '../composables/pagination';
import { usePreventEnter } from '../composables/preventEnter';

//  --------------------------------------------------------------------------------------------------------------------
//  component variables
//  --------------------------------------------------------------------------------------------------------------------
const { contents, currentPage, currentResponse, dataUrl, loading, q, queryParams, sorting, updateContents } =
  useContentFilter();

const { jumpTo, nextPage, pagination, previousPage } = usePagination(updateContents, currentResponse);
const { preventEnter } = usePreventEnter();

const teachingModules = ref(true);
const trends = ref(true);
const tools = ref(true);
const windowWidth = ref(0);

sorting.value = 'az';
dataUrl.value = '/api/inhalte';

// const competence = ref({
//   name: 'Kommunizieren & Kooperieren',
//   description:
//     'Um im digitalen Raum adäquat KOMMUNIZIEREN & KOOPERIEREN zu können, braucht es entsprechende Kompetenzen, digitale Werkzeuge zur angemessenen und effektiven Kommunikation einsetzen und in digitalen Umgebungen zielgerichtet kooperieren zu können. Dabei geht es vor allem darum, entsprechend der jeweiligen Situation und ausgerichtet an den Kommunikations- bzw. Kooperationspartnern die passenden Werkzeuge auszuwählen und entsprechende Umgangsregeln einzuhalten.',
// });

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const windowCom = computed(() => {
  return window;
});

const competenceFilterQueryParams = computed(() => {
  return {
    teachingModules: teachingModules.value,
    tools: tools.value,
    trends: trends.value
  };
});

//  --------------------------------------------------------------------------------------------------------------------
//  component logic
//  --------------------------------------------------------------------------------------------------------------------
const onResize = () => {
  windowWidth.value = window.innerWidth;
};

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watchEffect(() => {
  queryParams.value = competenceFilterQueryParams.value;
});

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
onMounted(async () => {
  windowWidth.value = window.innerWidth;
  window.addEventListener('resize', onResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize);
});

updateContents();
</script>

<style scoped></style>
