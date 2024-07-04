<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4 mb-4">
      <div class="section-info">
        <form id="filterForm" action="" class="collapse d-lg-block">
          <h2>Filtern nach</h2>

          <h3 class="form-subhead">Sortierung</h3>
          <select id="sortby-select" v-model="sorting" name="sortby" class="form-control" @change="updateContents">
            <option value="-latest">Neustes zuerst</option>
            <option value="latest">Ältestes zuerst</option>
            <option value="az">A-Z</option>
            <option value="za">Z-A</option>
          </select>
          <h3 class="form-subhead">Schlagwortsuche</h3>
          <input v-model="q" type="text" name="searchTerm" class="form-control" @keydown="preventEnter" />
          <CompetenceFilter v-model="competences" />
          <div>
            <h3 class="form-subhead">Sprachen</h3>
            <select
              id="language-dropdown"
              v-model="language"
              name="language"
              class="form-control"
              @change="updateContents"
            >
              <option id="language-0" value="" name="language" selected>--------</option>
              <option id="language-1" value="german" name="language">Deutsch</option>
              <option id="language-2" value="english" name="language">Englisch</option>
            </select>
          </div>
          <div>
            <h3 class="form-subhead">Trendtyp:</h3>
            <ul class="list-unstyled">
              <li class="form-check">
                <input
                  id="type-1"
                  v-model="trendTypes"
                  type="checkbox"
                  value="1"
                  name="trend-type"
                  class="form-check-input"
                />
                <label class="form-check-label" for="type-1">Forschung</label>
              </li>
              <li class="form-check">
                <input
                  id="type-2"
                  v-model="trendTypes"
                  type="checkbox"
                  value="2"
                  name="trend-type"
                  class="form-check-input"
                />
                <label class="form-check-label" for="type-2">Portal</label>
              </li>
              <li class="form-check">
                <input
                  id="type-3"
                  v-model="trendTypes"
                  type="checkbox"
                  value="3"
                  name="trend-type"
                  class="form-check-input"
                />
                <label class="form-check-label" for="type-3">Praxisbeispiel</label>
              </li>
              <li class="form-check">
                <input
                  id="type-4"
                  v-model="trendTypes"
                  type="checkbox"
                  value="4"
                  name="trend-type"
                  class="form-check-input"
                />
                <label class="form-check-label" for="type-4">Veröffentlichung</label>
              </li>
            </ul>
          </div>
        </form>
        <div class="text-center">
          <button
            class="button button--primary d-lg-none"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#filterForm"
            aria-expanded="false"
            aria-controls="filterForm"
            @click="mobileFilterExpanded = !mobileFilterExpanded"
          >
            {{ mobileFilterToggle }} <span class="fas" :class="mobileFilterExpanded ? 'fa-chevron-circle-up' : 'fa-chevron-circle-down'" />
          </button>
        </div>
      </div>
    </div>
    <div class="col col-12 col-lg-7 col-xl-8">
      <div v-if="contents.length > 0 || loading" class="row">
        <div v-for="(content, index) in contents" :key="index" class="col col-12 col-xl-6 mb-4">
          <ContentTeaser :content="content" />
        </div>
        <AppPagination
          v-model:pagination="pagination"
          v-model:current-page="currentPage"
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
            <a href="https://oerhoernchen.de/suche" target="_blank" rel="noopener noreferrer">OERhörchen</a>.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, watchEffect } from 'vue';

import AppPagination from '../components/AppPagination.vue';
import CompetenceFilter from '../components/CompetenceFilter.vue';
import ContentTeaser from '../components/ContentTeaser.vue';
import { useContentFilter } from '../composables/contentFilter';
import { usePagination } from '../composables/pagination';
import { usePreventEnter } from '../composables/preventEnter';

//  --------------------------------------------------------------------------------------------------------------------
//  component variables
//  --------------------------------------------------------------------------------------------------------------------
const {
  competences,
  contents,
  currentPage,
  currentResponse,
  dataUrl,
  debouncedUpdate,
  loading,
  q,
  queryParams,
  sorting,
  updateContents,
  initArray,
  mobileFilterExpanded,
  mobileFilterToggle
} = useContentFilter();
const { jumpTo, nextPage, pagination, previousPage } = usePagination(updateContents, currentResponse);
const { preventEnter } = usePreventEnter();

const language = ref(queryParams.value.language || null);
const trendTypes = ref(initArray(queryParams.value.trendTypes));

dataUrl.value = '/api/trends';

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const trendFilterQueryParams = computed(() => {
  return {
    language: language.value,
    trendTypes: trendTypes.value
  };
});

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watchEffect(() => {
  queryParams.value = trendFilterQueryParams.value;
});

watch(trendTypes, () => {
  debouncedUpdate();
});

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
updateContents();
</script>

<style scoped></style>
