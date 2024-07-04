<template>
  <div class="row mt-5 mb-5">
    <div class="col col-12 col-lg-5 col-xl-4 mb-5">
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

          <div class="form-check mt-3">
            <input
              id="input-hybrid"
              v-model="hybrid"
              type="checkbox"
              name="hybrid"
              class="form-check-input"
              @change="updateContents"
            />
            <label for="input-hybrid" class="form-check-label">Grundsätzlich geeignet für den Hybridunterricht</label>
          </div>

          <CompetenceFilter v-model="competences" />
          <div>
            <h3 class="form-subhead">Unterrichtsfach</h3>
            <ul class="list-unstyled">
              <li v-for="(subject, index) in getSubjects()" :key="index" class="form-check">
                <input
                  :id="'subject-' + subject.value"
                  v-model="subjects"
                  type="checkbox"
                  :value="subject.value"
                  name="subjects"
                  class="form-check-input"
                  @change="updateContents"
                />
                <label :for="'subject-' + subject.value" class="form-check-label">{{ subject.name }}</label>
              </li>
            </ul>
          </div>
          <div>
            <h3 class="form-subhead">Schulform</h3>
            <select v-model="schoolType" class="form-control" @change="updateContents">
              <option v-for="(type, index) in getSchoolTypes()" :key="index" :value="type.value">
                {{ type.name }}
              </option>
            </select>
          </div>
          <div>
            <h3 class="form-subhead">Jahrgangsstufe von / bis:</h3>
            <div class="row">
              <div class="col">
                <input
                  v-model="schoolClassFrom"
                  type="text"
                  name="schoolClassFrom"
                  class="form-control me-2"
                  @change="debouncedUpdate"
                />
              </div>
              <div class="col-1 text-center">-</div>
              <div class="col">
                <input
                  v-model="schoolClassTo"
                  type="text"
                  name="schoolClassTo"
                  class="form-control ms-2"
                  @change="debouncedUpdate"
                />
              </div>
            </div>
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
import { computed, ref, watchEffect } from 'vue';

import AppPagination from '../components/AppPagination.vue';
import CompetenceFilter from '../components/CompetenceFilter.vue';
import ContentTeaser from '../components/ContentTeaser.vue';
import { useContentFilter } from '../composables/contentFilter';
import { usePagination } from '../composables/pagination';
import { usePreventEnter } from '../composables/preventEnter';

const {
  competences,
  contents,
  currentPage,
  currentResponse,
  dataUrl,
  debouncedUpdate,
  getSubjects,
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

const subjects = ref(initArray(queryParams.value.subjects));
const schoolClassFrom = ref(queryParams.value.schoolClassFrom || null);
const schoolClassTo = ref(queryParams.value.schoolClassTo || null);
const schoolType = ref(queryParams.value.schoolType || null);
const hybrid = ref(queryParams.value.hybrid || false);

dataUrl.value = '/api/unterrichtsbausteine';

const getSchoolTypes = () => window.schoolFilter;

//  --------------------------------------------------------------------------------------------------------------------
//  computed
//  --------------------------------------------------------------------------------------------------------------------
const teachingModulesQueryParams = computed(() => {
  return {
    hybrid: hybrid.value,
    schoolClassFrom: schoolClassFrom.value,
    schoolClassTo: schoolClassTo.value,
    schoolType: schoolType.value,
    subjects: subjects.value
  };
});

//  --------------------------------------------------------------------------------------------------------------------
//  watchers
//  --------------------------------------------------------------------------------------------------------------------
watchEffect(() => {
  queryParams.value = teachingModulesQueryParams.value;
});

//  --------------------------------------------------------------------------------------------------------------------
//  lifecycle
//  --------------------------------------------------------------------------------------------------------------------
updateContents();
</script>

<style scoped></style>
